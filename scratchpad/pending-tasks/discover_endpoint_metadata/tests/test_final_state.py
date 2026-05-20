import json
import os
import socket

import pytest
import requests
from xprocess import ProcessStarter


PROJECT_DIR = "/home/user/app"
BASE_URL = "http://localhost:3000"
DISCOVER_URL = f"{BASE_URL}/api/novu?action=discover"


@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "start_app"
        args = ["node", "index.js"]
        env = {**os.environ, "NOVU_STRICT_AUTHENTICATION_ENABLED": "false"}
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 120
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", 3000)) == 0

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _find_workflow(payload):
    """Locate the workflows list within the discover response, accommodating
    minor shape variations across @novu/framework versions."""
    if isinstance(payload, dict):
        if "workflows" in payload and isinstance(payload["workflows"], list):
            return payload["workflows"]
        for value in payload.values():
            found = _find_workflow(value)
            if found is not None:
                return found
    elif isinstance(payload, list):
        # If the payload is itself a list of workflow descriptors.
        if payload and isinstance(payload[0], dict) and (
            "workflowId" in payload[0] or "steps" in payload[0]
        ):
            return payload
        for item in payload:
            found = _find_workflow(item)
            if found is not None:
                return found
    return None


def _collect_strings(obj):
    """Recursively gather all string leaves from an arbitrary JSON value."""
    strings = []
    if isinstance(obj, str):
        strings.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            strings.extend(_collect_strings(v))
    elif isinstance(obj, list):
        for v in obj:
            strings.extend(_collect_strings(v))
    return strings


def _find_status_enum(node):
    """Find an enum constraint for the `status` field anywhere in the schema."""
    target = {"shipped", "delivered", "canceled"}
    if isinstance(node, dict):
        # JSON-schema style: { "status": { "enum": [...] } }
        status_node = node.get("status")
        if isinstance(status_node, dict):
            enum_vals = status_node.get("enum")
            if isinstance(enum_vals, list) and set(enum_vals) == target:
                return True
        for v in node.values():
            if _find_status_enum(v):
                return True
    elif isinstance(node, list):
        # Direct enum list match.
        if set(node) == target:
            return True
        for v in node:
            if _find_status_enum(v):
                return True
    return False


def _schema_requires_orderid(node):
    if isinstance(node, dict):
        if isinstance(node.get("required"), list) and "orderId" in node["required"]:
            return True
        props = node.get("properties")
        if isinstance(props, dict) and "orderId" in props:
            order_node = props["orderId"]
            if isinstance(order_node, dict):
                t = order_node.get("type")
                if t == "string" or (isinstance(t, list) and "string" in t):
                    # Mark as present; treat as required if `required` includes it
                    if isinstance(node.get("required"), list) and "orderId" in node["required"]:
                        return True
        for v in node.values():
            if _schema_requires_orderid(v):
                return True
    elif isinstance(node, list):
        for v in node:
            if _schema_requires_orderid(v):
                return True
    return False


def test_discover_returns_single_workflow(start_app):
    resp = requests.get(DISCOVER_URL, timeout=30)
    assert resp.status_code == 200, (
        f"GET {DISCOVER_URL} returned status {resp.status_code}: {resp.text}"
    )
    data = resp.json()
    workflows = _find_workflow(data)
    assert workflows is not None, (
        f"Could not locate a `workflows` array in discover response: {data}"
    )
    assert len(workflows) == 1, (
        f"Expected exactly one workflow, got {len(workflows)}: {workflows}"
    )


def test_discover_workflow_metadata(start_app):
    resp = requests.get(DISCOVER_URL, timeout=30)
    assert resp.status_code == 200, f"discover failed: {resp.status_code} {resp.text}"
    workflows = _find_workflow(resp.json())
    assert workflows and len(workflows) == 1, "Expected one workflow in discover output."
    wf = workflows[0]
    assert wf.get("workflowId") == "order-status", (
        f"Expected workflowId 'order-status', got: {wf.get('workflowId')}"
    )
    assert wf.get("name") == "Order Status Updates", (
        f"Expected name 'Order Status Updates', got: {wf.get('name')}"
    )
    assert wf.get("description") == "Sends order updates via email and SMS", (
        f"Expected description 'Sends order updates via email and SMS', got: {wf.get('description')}"
    )


def test_discover_steps_in_correct_order(start_app):
    resp = requests.get(DISCOVER_URL, timeout=30)
    workflows = _find_workflow(resp.json())
    wf = workflows[0]
    steps = wf.get("steps")
    assert isinstance(steps, list) and len(steps) == 2, (
        f"Expected exactly 2 steps, got: {steps}"
    )
    assert steps[0].get("stepId") == "order-email", (
        f"Expected first step stepId 'order-email', got: {steps[0].get('stepId')}"
    )
    assert steps[0].get("type") == "email", (
        f"Expected first step type 'email', got: {steps[0].get('type')}"
    )
    assert steps[1].get("stepId") == "order-sms", (
        f"Expected second step stepId 'order-sms', got: {steps[1].get('stepId')}"
    )
    assert steps[1].get("type") == "sms", (
        f"Expected second step type 'sms', got: {steps[1].get('type')}"
    )


def test_discover_payload_schema_enum_and_required(start_app):
    resp = requests.get(DISCOVER_URL, timeout=30)
    workflows = _find_workflow(resp.json())
    wf = workflows[0]
    # The schema is exposed under different locations in different versions.
    candidates = [
        wf.get("payload"),
        wf.get("payloadSchema"),
        wf.get("schema"),
    ]
    candidates = [c for c in candidates if c is not None]
    assert candidates, f"No payload schema found in workflow: {wf}"

    assert any(_find_status_enum(c) for c in candidates), (
        f"Expected status enum [shipped, delivered, canceled] in payload schema, "
        f"got: {json.dumps(candidates)[:1000]}"
    )
    assert any(_schema_requires_orderid(c) for c in candidates), (
        f"Expected `orderId` to be required string in payload schema, "
        f"got: {json.dumps(candidates)[:1000]}"
    )


def test_preview_email_step_interpolation(start_app):
    url = (
        f"{BASE_URL}/api/novu?action=preview"
        f"&workflowId=order-status&stepId=order-email"
    )
    body = {
        "payload": {"orderId": "O-99", "status": "shipped"},
        "controls": {},
        "state": {"steps": []},
    }
    resp = requests.post(url, json=body, timeout=30)
    assert resp.status_code == 200, (
        f"POST preview email failed: {resp.status_code} {resp.text}"
    )
    strings = _collect_strings(resp.json())
    assert any("Order O-99" in s for s in strings), (
        f"Expected resolved subject 'Order O-99' in preview response, got strings: {strings}"
    )
    assert any("Status: shipped" in s for s in strings), (
        f"Expected resolved body 'Status: shipped' in preview response, got strings: {strings}"
    )


def test_preview_sms_step_interpolation(start_app):
    url = (
        f"{BASE_URL}/api/novu?action=preview"
        f"&workflowId=order-status&stepId=order-sms"
    )
    body = {
        "payload": {"orderId": "O-99", "status": "shipped"},
        "controls": {},
        "state": {"steps": []},
    }
    resp = requests.post(url, json=body, timeout=30)
    assert resp.status_code == 200, (
        f"POST preview sms failed: {resp.status_code} {resp.text}"
    )
    strings = _collect_strings(resp.json())
    assert any("Order O-99 is now shipped" in s for s in strings), (
        f"Expected resolved sms body 'Order O-99 is now shipped' in preview response, "
        f"got strings: {strings}"
    )
