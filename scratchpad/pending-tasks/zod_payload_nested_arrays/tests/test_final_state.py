import os
import socket
import time

import pytest
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/app"
BRIDGE_URL = "http://localhost:3000/api/novu"


@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "novu_bridge"
        args = ["node", "index.js"]
        env = {
            **os.environ,
            "NOVU_STRICT_AUTHENTICATION_ENABLED": "false",
            "PORT": "3000",
        }
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 120
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("localhost", 3000)) != 0:
                    return False
            try:
                r = requests.get(f"{BRIDGE_URL}?action=health-check", timeout=5)
                return r.status_code < 500
            except requests.RequestException:
                return False

    xprocess.ensure(Starter.name, Starter)

    # Extra readiness wait
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            r = requests.get(f"{BRIDGE_URL}?action=health-check", timeout=5)
            if r.status_code < 500:
                break
        except requests.RequestException:
            pass
        time.sleep(1)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _find_workflow(discover_data, workflow_id):
    """Search recursively for a workflow with the given workflowId."""
    workflows = None
    if isinstance(discover_data, dict):
        if "workflows" in discover_data and isinstance(discover_data["workflows"], list):
            workflows = discover_data["workflows"]
        elif "data" in discover_data and isinstance(discover_data["data"], dict):
            return _find_workflow(discover_data["data"], workflow_id)
    if workflows is None:
        return None
    for wf in workflows:
        if isinstance(wf, dict) and wf.get("workflowId") == workflow_id:
            return wf
    return None


def _get_payload_schema(workflow):
    """Locate the JSON schema describing the payload in the discover response."""
    candidates = []
    if "payload" in workflow and isinstance(workflow["payload"], dict):
        p = workflow["payload"]
        if "schema" in p and isinstance(p["schema"], dict):
            candidates.append(p["schema"])
        else:
            candidates.append(p)
    if "payloadSchema" in workflow and isinstance(workflow["payloadSchema"], dict):
        candidates.append(workflow["payloadSchema"])
    if "options" in workflow and isinstance(workflow["options"], dict):
        opts = workflow["options"]
        if "payloadSchema" in opts and isinstance(opts["payloadSchema"], dict):
            candidates.append(opts["payloadSchema"])
    for c in candidates:
        if "properties" in c:
            return c
    return candidates[0] if candidates else None


def test_discover_exposes_workflow_and_nested_schema(start_app):
    r = requests.get(f"{BRIDGE_URL}?action=discover", timeout=15)
    assert r.status_code == 200, f"discover returned {r.status_code}: {r.text}"
    data = r.json()
    wf = _find_workflow(data, "bulk-order-summary")
    assert wf is not None, (
        f"Workflow 'bulk-order-summary' not found in discover output: {data}"
    )

    steps = wf.get("steps") or []
    email_steps = [s for s in steps if s.get("stepId") == "summary-email"]
    assert len(email_steps) == 1, (
        f"Expected exactly one step 'summary-email', got steps={steps}"
    )
    assert email_steps[0].get("type") == "email", (
        f"Expected step type 'email', got: {email_steps[0]}"
    )

    schema = _get_payload_schema(wf)
    assert schema is not None, f"Could not locate payload schema in workflow: {wf}"
    props = schema.get("properties", {})

    customer = props.get("customer", {})
    assert customer.get("type") == "object" or "properties" in customer, (
        f"customer should be an object schema: {customer}"
    )
    customer_props = customer.get("properties", {})
    assert customer_props.get("name", {}).get("type") == "string", (
        f"customer.name must be a string, got: {customer_props.get('name')}"
    )
    email_prop = customer_props.get("email", {})
    assert email_prop.get("format") == "email", (
        f"customer.email must have format 'email', got: {email_prop}"
    )

    items = props.get("items", {})
    assert items.get("type") == "array", f"items must be an array schema, got: {items}"
    assert items.get("minItems") == 1, (
        f"items must have minItems == 1, got: {items.get('minItems')}"
    )
    item_schema = items.get("items", {})
    item_props = item_schema.get("properties", {})
    assert item_props.get("sku", {}).get("type") == "string", (
        f"items.items.sku must be string, got: {item_props.get('sku')}"
    )
    assert item_props.get("quantity", {}).get("type") == "integer", (
        f"items.items.quantity must be integer, got: {item_props.get('quantity')}"
    )
    assert item_props.get("price", {}).get("type") == "number", (
        f"items.items.price must be number, got: {item_props.get('price')}"
    )

    total = props.get("totalAmount", {})
    assert total.get("type") == "number", (
        f"totalAmount must be number, got: {total}"
    )


def _execute_body(payload):
    return {
        "payload": payload,
        "subscriber": {"subscriberId": "test-subscriber"},
        "controls": {},
        "inputs": {},
        "state": [],
        "stepId": "summary-email",
        "workflowId": "bulk-order-summary",
    }


def test_invalid_payload_empty_items_rejected(start_app):
    body = _execute_body({
        "customer": {"name": "Alice", "email": "alice@example.com"},
        "items": [],
        "totalAmount": 0,
    })
    r = requests.post(
        f"{BRIDGE_URL}?action=execute&workflowId=bulk-order-summary&stepId=summary-email",
        json=body,
        timeout=15,
    )
    assert r.status_code >= 400, (
        f"Expected non-2xx for empty items array, got {r.status_code}: {r.text}"
    )


def test_invalid_payload_bad_email_rejected(start_app):
    body = _execute_body({
        "customer": {"name": "Alice", "email": "not-an-email"},
        "items": [{"sku": "A", "quantity": 1, "price": 1}],
        "totalAmount": 1,
    })
    r = requests.post(
        f"{BRIDGE_URL}?action=execute&workflowId=bulk-order-summary&stepId=summary-email",
        json=body,
        timeout=15,
    )
    assert r.status_code >= 400, (
        f"Expected non-2xx for invalid email, got {r.status_code}: {r.text}"
    )


def _find_subject_body(obj):
    """Recursively find subject/body strings in a preview response."""
    found = {}
    if isinstance(obj, dict):
        if "subject" in obj and "body" in obj and isinstance(obj.get("subject"), str):
            return {"subject": obj["subject"], "body": obj["body"]}
        for v in obj.values():
            res = _find_subject_body(v)
            if res:
                found = res
                break
    elif isinstance(obj, list):
        for v in obj:
            res = _find_subject_body(v)
            if res:
                found = res
                break
    return found


def test_valid_payload_preview_renders_subject_and_body(start_app):
    body = _execute_body({
        "customer": {"name": "Bob", "email": "b@x.com"},
        "items": [
            {"sku": "A", "quantity": 2, "price": 10},
            {"sku": "B", "quantity": 1, "price": 5},
        ],
        "totalAmount": 25,
    })
    r = requests.post(
        f"{BRIDGE_URL}?action=preview&workflowId=bulk-order-summary&stepId=summary-email",
        json=body,
        timeout=15,
    )
    assert r.status_code == 200, (
        f"Preview should return 200 for valid payload, got {r.status_code}: {r.text}"
    )
    data = r.json()
    rendered = _find_subject_body(data)
    assert rendered, f"Could not locate subject/body in preview response: {data}"
    assert rendered["subject"] == "Order summary for Bob", (
        f"Unexpected subject: {rendered['subject']!r}"
    )
    assert rendered["body"] == "Your order contains 2 items totaling $25.", (
        f"Unexpected body: {rendered['body']!r}"
    )
