import os
import socket
import subprocess

import pytest
import requests
from xprocess import ProcessStarter


PROJECT_DIR = "/home/user/app"
BRIDGE_URL = "http://localhost:3000/api/novu"
WORKFLOW_ID = "account-alert"
NOTIFY_STEP_ID = "notify"


@pytest.fixture(scope="session")
def start_app(xprocess):
    """Start the Novu Express bridge using `node index.js`."""

    if not os.path.isdir(os.path.join(PROJECT_DIR, "node_modules")):
        subprocess.run(
            ["npm", "install", "--no-audit", "--no-fund"],
            cwd=PROJECT_DIR,
            check=False,
        )

    class Starter(ProcessStarter):
        name = "novu_bridge"
        args = ["node", "index.js"]
        env = {
            **os.environ,
            "NODE_ENV": "development",
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
                return s.connect_ex(("localhost", 3000)) == 0

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _discover():
    resp = requests.get(f"{BRIDGE_URL}?action=discover", timeout=30)
    assert resp.status_code == 200, (
        f"discover request failed: status={resp.status_code} body={resp.text}"
    )
    return resp.json()


def _get_workflow(data):
    workflows = data.get("workflows", [])
    matching = [w for w in workflows if w.get("workflowId") == WORKFLOW_ID]
    assert matching, (
        f"Expected a workflow with workflowId='{WORKFLOW_ID}' in discover, got: {workflows}"
    )
    return matching[0]


def test_health_check(start_app):
    resp = requests.get(f"{BRIDGE_URL}?action=health-check", timeout=30)
    assert resp.status_code == 200, (
        f"health-check failed with status {resp.status_code}: {resp.text}"
    )
    body = resp.json()
    assert body.get("status") == "ok", (
        f"Expected health-check status 'ok', got: {body}"
    )
    workflows = body.get("discovered", {}).get("workflows", 0)
    assert workflows >= 1, (
        f"Expected at least 1 discovered workflow, got: {body}"
    )


def test_discover_lists_workflow_and_step(start_app):
    workflow = _get_workflow(_discover())
    steps = workflow.get("steps", [])
    assert len(steps) == 1, (
        f"Expected exactly one step in workflow '{WORKFLOW_ID}', got: {steps}"
    )
    step = steps[0]
    assert step.get("stepId") == NOTIFY_STEP_ID, (
        f"Expected stepId='{NOTIFY_STEP_ID}', got: {step.get('stepId')!r}"
    )
    assert step.get("type") == "in_app", (
        f"Expected step type='in_app', got: {step.get('type')!r}"
    )


def test_discover_payload_schema_shape(start_app):
    workflow = _get_workflow(_discover())
    payload_schema = workflow.get("payload")
    assert isinstance(payload_schema, dict), (
        f"Expected workflow.payload to be a JSON Schema object, got: {payload_schema!r}"
    )
    assert payload_schema.get("type") == "object", (
        f"Expected payload.type=='object', got: {payload_schema.get('type')!r}"
    )

    required = payload_schema.get("required")
    assert isinstance(required, list), (
        f"Expected payload.required to be a list, got: {required!r}"
    )
    assert set(required) == {"email", "severity"}, (
        f"Expected payload.required to be ['email','severity'] (any order), got: {required!r}"
    )

    properties = payload_schema.get("properties") or {}
    assert isinstance(properties, dict), (
        f"Expected payload.properties to be a dict, got: {properties!r}"
    )

    email_prop = properties.get("email") or {}
    assert email_prop.get("type") == "string", (
        f"Expected payload.properties.email.type=='string', got: {email_prop!r}"
    )

    severity_prop = properties.get("severity") or {}
    assert severity_prop.get("type") == "string", (
        f"Expected payload.properties.severity.type=='string', got: {severity_prop!r}"
    )
    severity_enum = severity_prop.get("enum")
    assert isinstance(severity_enum, list), (
        f"Expected payload.properties.severity.enum to be a list, got: {severity_enum!r}"
    )
    assert set(severity_enum) == {"low", "medium", "high"}, (
        f"Expected severity.enum=['low','medium','high'] (any order), got: {severity_enum!r}"
    )


def _preview(payload):
    body = {
        "action": "preview",
        "workflowId": WORKFLOW_ID,
        "stepId": NOTIFY_STEP_ID,
        "payload": payload,
        "controls": {},
        "inputs": {},
        "subscriber": {"subscriberId": "test-subscriber"},
        "state": [],
    }
    return requests.post(
        f"{BRIDGE_URL}?action=preview&workflowId={WORKFLOW_ID}&stepId={NOTIFY_STEP_ID}",
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )


def test_preview_with_valid_payload_alice(start_app):
    resp = _preview({"email": "alice@example.com", "severity": "medium"})
    assert resp.status_code == 200, (
        f"preview request failed: status={resp.status_code} body={resp.text}"
    )
    outputs = resp.json().get("outputs", {})
    assert outputs.get("body") == "Severity medium alert for alice@example.com", (
        f"Unexpected outputs.body: {outputs.get('body')!r}"
    )


def test_preview_with_valid_payload_bob(start_app):
    resp = _preview({"email": "bob@example.com", "severity": "high"})
    assert resp.status_code == 200, (
        f"preview request failed: status={resp.status_code} body={resp.text}"
    )
    outputs = resp.json().get("outputs", {})
    assert outputs.get("body") == "Severity high alert for bob@example.com", (
        f"Unexpected outputs.body: {outputs.get('body')!r}"
    )


def _execute(payload):
    body = {
        "action": "execute",
        "workflowId": WORKFLOW_ID,
        "stepId": NOTIFY_STEP_ID,
        "payload": payload,
        "controls": {},
        "inputs": {},
        "subscriber": {"subscriberId": "test-subscriber"},
        "state": [],
    }
    return requests.post(
        f"{BRIDGE_URL}?action=execute&workflowId={WORKFLOW_ID}&stepId={NOTIFY_STEP_ID}",
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )


def test_execute_rejects_missing_email(start_app):
    resp = _execute({"severity": "high"})
    assert resp.status_code >= 400, (
        f"Expected a 4xx/5xx response when 'email' is missing, got {resp.status_code}: {resp.text}"
    )
    text = resp.text.lower()
    assert any(token in text for token in ("email", "payload", "required", "validation")), (
        f"Expected error response to mention email/payload/required/validation, got: {resp.text}"
    )


def test_execute_rejects_bad_severity(start_app):
    resp = _execute({"email": "alice@example.com", "severity": "critical"})
    assert resp.status_code >= 400, (
        f"Expected a 4xx/5xx response for invalid severity, got {resp.status_code}: {resp.text}"
    )
    text = resp.text.lower()
    assert any(token in text for token in ("severity", "enum", "payload", "validation")), (
        f"Expected error response to mention severity/enum/payload/validation, got: {resp.text}"
    )
