import os
import socket
import pytest
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/app"
BASE_URL = "http://localhost:3000"
BRIDGE_PATH = "/api/novu"


@pytest.fixture(scope="session")
def start_app(xprocess):
    """Start the Novu Bridge Express server and wait for port 3000."""

    class Starter(ProcessStarter):
        name = "novu_bridge"
        args = ["node", "index.js"]
        env = os.environ.copy()
        env["NOVU_STRICT_AUTHENTICATION_ENABLED"] = "false"
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 60
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", 3000)) == 0

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _find_workflow(workflows, workflow_id):
    for wf in workflows:
        if wf.get("workflowId") == workflow_id:
            return wf
    return None


def _find_step(workflow, step_id):
    for step in workflow.get("steps", []) or []:
        if step.get("stepId") == step_id:
            return step
    return None


def _step_type(step):
    """Return the channel type for a step, supporting both shapes."""
    if not step:
        return None
    if "type" in step and step["type"]:
        return step["type"]
    template = step.get("template") or {}
    return template.get("type")


def test_discover_endpoint_exposes_workflow_and_push_step(start_app):
    """Verify GET /api/novu?action=discover returns the workflow and push step."""
    resp = requests.get(f"{BASE_URL}{BRIDGE_PATH}", params={"action": "discover"}, timeout=15)
    assert resp.status_code == 200, (
        f"Expected status 200 from discover endpoint, got {resp.status_code}. Body: {resp.text}"
    )
    data = resp.json()
    workflows = data.get("workflows")
    assert isinstance(workflows, list) and len(workflows) > 0, (
        f"Expected 'workflows' to be a non-empty list. Response: {data}"
    )
    workflow = _find_workflow(workflows, "mobile-alert")
    assert workflow is not None, (
        f"Workflow 'mobile-alert' not found in discover response. Workflows: "
        f"{[w.get('workflowId') for w in workflows]}"
    )
    step = _find_step(workflow, "notify-push")
    assert step is not None, (
        f"Step 'notify-push' not found in workflow 'mobile-alert'. Steps: "
        f"{[s.get('stepId') for s in (workflow.get('steps') or [])]}"
    )
    step_type = _step_type(step)
    assert step_type == "push", (
        f"Expected step type 'push' for 'notify-push', got {step_type!r}. Step: {step}"
    )


def test_discover_endpoint_exposes_payload_schema_with_required_title_and_message(start_app):
    """Verify the workflow exposes a payload schema requiring title and message."""
    resp = requests.get(f"{BASE_URL}{BRIDGE_PATH}", params={"action": "discover"}, timeout=15)
    assert resp.status_code == 200, f"Discover endpoint failed with status {resp.status_code}."
    data = resp.json()
    workflow = _find_workflow(data.get("workflows") or [], "mobile-alert")
    assert workflow is not None, "Workflow 'mobile-alert' missing from discover response."

    # The framework may expose the payload schema under different keys depending on version.
    candidates = []
    for key in ("payload", "payloadSchema", "data"):
        node = workflow.get(key)
        if isinstance(node, dict):
            candidates.append(node)
            schema = node.get("schema")
            if isinstance(schema, dict):
                candidates.append(schema)

    schema = None
    for c in candidates:
        required = c.get("required")
        props = c.get("properties")
        if isinstance(required, list) and isinstance(props, dict):
            schema = c
            break

    assert schema is not None, (
        f"Could not locate payload JSON schema for workflow 'mobile-alert'. Workflow: {workflow}"
    )

    required = schema.get("required") or []
    assert "title" in required, f"Payload schema must require 'title'. Required: {required}"
    assert "message" in required, f"Payload schema must require 'message'. Required: {required}"

    props = schema.get("properties") or {}
    title_prop = props.get("title") or {}
    message_prop = props.get("message") or {}
    assert title_prop.get("type") == "string", (
        f"Payload property 'title' must be of type 'string'. Got: {title_prop}"
    )
    assert message_prop.get("type") == "string", (
        f"Payload property 'message' must be of type 'string'. Got: {message_prop}"
    )


def _preview(payload):
    body = {
        "inputs": {},
        "controls": {},
        "data": payload,
        "payload": payload,
        "state": [],
        "subscriber": {},
    }
    return requests.post(
        f"{BASE_URL}{BRIDGE_PATH}",
        params={
            "action": "preview",
            "workflowId": "mobile-alert",
            "stepId": "notify-push",
        },
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )


def test_preview_renders_hello_world(start_app):
    """Verify preview rendering with payload {title: 'Hello', message: 'World'}."""
    resp = _preview({"title": "Hello", "message": "World"})
    assert resp.status_code == 200, (
        f"Expected status 200 from preview endpoint, got {resp.status_code}. Body: {resp.text}"
    )
    data = resp.json()
    outputs = data.get("outputs")
    assert isinstance(outputs, dict), (
        f"Expected 'outputs' object in preview response. Response: {data}"
    )
    assert outputs.get("subject") == "Hello", (
        f"Expected outputs.subject == 'Hello' (Liquid interpolation of payload.title). Got: {outputs}"
    )
    assert outputs.get("body") == "World", (
        f"Expected outputs.body == 'World' (Liquid interpolation of payload.message). Got: {outputs}"
    )


def test_preview_renders_alternate_payload(start_app):
    """Verify preview rendering interpolates a different payload correctly."""
    resp = _preview({"title": "Build #42", "message": "Completed successfully"})
    assert resp.status_code == 200, (
        f"Expected status 200 from preview endpoint, got {resp.status_code}. Body: {resp.text}"
    )
    data = resp.json()
    outputs = data.get("outputs") or {}
    assert outputs.get("subject") == "Build #42", (
        f"Expected outputs.subject == 'Build #42'. Got: {outputs}"
    )
    assert outputs.get("body") == "Completed successfully", (
        f"Expected outputs.body == 'Completed successfully'. Got: {outputs}"
    )
