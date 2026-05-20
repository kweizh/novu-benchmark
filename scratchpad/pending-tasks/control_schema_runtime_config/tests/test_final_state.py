import json
import os
import socket

import pytest
import requests
from xprocess import ProcessStarter


PROJECT_DIR = "/home/user/app"
BASE_URL = "http://localhost:3000"
BRIDGE_URL = f"{BASE_URL}/api/novu"


def _walk(node):
    """Yield every dict/list found anywhere in the tree."""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


def _find_workflow(discover_payload, workflow_id):
    for node in _walk(discover_payload):
        if isinstance(node, dict) and node.get("workflowId") == workflow_id:
            return node
    return None


def _find_step(workflow_node, step_id):
    for node in _walk(workflow_node):
        if isinstance(node, dict) and node.get("stepId") == step_id:
            return node
    return None


def _find_controls_schema(step_node):
    """Locate the JSON Schema for controls within a step entry.

    Different Novu versions place the resolved JSON Schema either at
    `step.controls.schema` or directly at `step.controls`. Search both.
    """
    controls = step_node.get("controls")
    candidates = []
    if isinstance(controls, dict):
        if isinstance(controls.get("schema"), dict):
            candidates.append(controls["schema"])
        candidates.append(controls)
    # Fallback - search any nested dict that exposes the expected properties.
    for node in _walk(step_node):
        if (
            isinstance(node, dict)
            and isinstance(node.get("properties"), dict)
            and "headline" in node["properties"]
            and "footer" in node["properties"]
        ):
            candidates.append(node)
    for cand in candidates:
        props = cand.get("properties")
        if isinstance(props, dict) and "headline" in props and "footer" in props:
            return cand
    return None


def _extract_outputs(preview_payload):
    """Return the dict that holds the resolved step outputs (subject, body, ...)."""
    for node in _walk(preview_payload):
        if (
            isinstance(node, dict)
            and "subject" in node
            and "body" in node
            and isinstance(node.get("subject"), str)
            and isinstance(node.get("body"), str)
        ):
            return node
    return None


@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "novu_bridge"
        args = ["node", "index.js"]
        env = {**os.environ, "NOVU_STRICT_AUTHENTICATION_ENABLED": "false"}
        popen_kwargs = {"cwd": PROJECT_DIR, "text": True}
        timeout = 120
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", 3000)) == 0

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def test_discover_shape(start_app):
    resp = requests.get(f"{BRIDGE_URL}?action=discover", timeout=30)
    assert resp.status_code == 200, (
        f"Expected 200 from discover, got {resp.status_code}: {resp.text[:500]}"
    )
    payload = resp.json()

    workflow = _find_workflow(payload, "daily-report")
    assert workflow is not None, (
        f"Workflow 'daily-report' not found in discover response: {json.dumps(payload)[:1000]}"
    )

    step = _find_step(workflow, "report-email")
    assert step is not None, (
        f"Step 'report-email' not found in workflow node: {json.dumps(workflow)[:1000]}"
    )

    step_type = step.get("type") or step.get("channel") or step.get("template", {}).get("type")
    assert (
        isinstance(step_type, str) and step_type.lower() == "email"
    ), f"Expected step type 'email', got {step_type!r}."

    schema = _find_controls_schema(step)
    assert schema is not None, (
        f"Could not find controls JSON Schema for step: {json.dumps(step)[:1000]}"
    )
    props = schema.get("properties", {})
    headline = props.get("headline", {})
    footer = props.get("footer", {})
    assert headline.get("type") == "string", (
        f"Expected headline to be type=string, got {headline!r}"
    )
    assert footer.get("type") == "string", (
        f"Expected footer to be type=string, got {footer!r}"
    )
    assert headline.get("default") == "Daily Report", (
        f"Expected headline.default='Daily Report', got {headline.get('default')!r}"
    )
    assert footer.get("default") == "Best, the Team", (
        f"Expected footer.default='Best, the Team', got {footer.get('default')!r}"
    )


def test_preview_with_defaults(start_app):
    url = (
        f"{BRIDGE_URL}?action=preview"
        "&workflowId=daily-report&stepId=report-email"
    )
    body = {"controls": {}, "payload": {"userName": "Alice"}}
    resp = requests.post(url, json=body, timeout=30)
    assert resp.status_code == 200, (
        f"Expected 200 from preview with defaults, got {resp.status_code}: {resp.text[:500]}"
    )
    payload = resp.json()
    outputs = _extract_outputs(payload)
    assert outputs is not None, (
        f"Could not find resolved outputs (subject/body) in preview response: "
        f"{json.dumps(payload)[:1000]}"
    )
    assert outputs["subject"] == "Daily Report", (
        f"Expected subject 'Daily Report' for defaults, got {outputs['subject']!r}"
    )
    assert outputs["body"].endswith("\nBest, the Team"), (
        f"Expected body to end with '\\nBest, the Team', got {outputs['body']!r}"
    )


def test_preview_with_overrides(start_app):
    url = (
        f"{BRIDGE_URL}?action=preview"
        "&workflowId=daily-report&stepId=report-email"
    )
    body = {
        "controls": {"headline": "Custom!", "footer": "Bye!"},
        "payload": {"userName": "Alice"},
    }
    resp = requests.post(url, json=body, timeout=30)
    assert resp.status_code == 200, (
        f"Expected 200 from preview with overrides, got {resp.status_code}: {resp.text[:500]}"
    )
    payload = resp.json()
    outputs = _extract_outputs(payload)
    assert outputs is not None, (
        f"Could not find resolved outputs (subject/body) in preview response: "
        f"{json.dumps(payload)[:1000]}"
    )
    assert outputs["subject"] == "Custom!", (
        f"Expected subject 'Custom!' for overrides, got {outputs['subject']!r}"
    )
    assert outputs["body"].endswith("\nBye!"), (
        f"Expected body to end with '\\nBye!', got {outputs['body']!r}"
    )


def test_preview_rejects_invalid_payload(start_app):
    url = (
        f"{BRIDGE_URL}?action=preview"
        "&workflowId=daily-report&stepId=report-email"
    )
    body = {"controls": {}, "payload": {}}
    resp = requests.post(url, json=body, timeout=30)
    assert resp.status_code != 200, (
        f"Expected non-200 status when payload is missing required 'userName', "
        f"got {resp.status_code}: {resp.text[:500]}"
    )
