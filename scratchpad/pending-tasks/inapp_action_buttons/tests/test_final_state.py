import os
import socket
import subprocess

import pytest
import requests
from xprocess import ProcessStarter


PROJECT_DIR = "/home/user/app"
BRIDGE_URL = "http://localhost:3000/api/novu"
WORKFLOW_ID = "approval-request"


@pytest.fixture(scope="session")
def start_app(xprocess):
    """Start the Novu Express bridge using `node index.js`."""

    # Best-effort dependency installation in case the executor didn't run npm install.
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


def _get_step_id():
    """Discover the in-app step id from the bridge."""
    resp = requests.get(f"{BRIDGE_URL}?action=discover", timeout=30)
    assert resp.status_code == 200, (
        f"discover request failed: status={resp.status_code} body={resp.text}"
    )
    data = resp.json()
    workflows = data.get("workflows", [])
    matching = [w for w in workflows if w.get("workflowId") == WORKFLOW_ID]
    assert matching, (
        f"Expected a workflow with workflowId='{WORKFLOW_ID}' in discover response, got: {workflows}"
    )
    steps = matching[0].get("steps", [])
    in_app_steps = [s for s in steps if s.get("type") == "in_app"]
    assert in_app_steps, (
        f"Expected at least one in_app step in workflow '{WORKFLOW_ID}', got steps: {steps}"
    )
    step_id = in_app_steps[0].get("stepId")
    assert step_id, f"in_app step has no stepId: {in_app_steps[0]}"
    return step_id


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


def test_discover_lists_workflow(start_app):
    step_id = _get_step_id()
    assert isinstance(step_id, str) and step_id, (
        f"Expected a non-empty stepId for the in_app step, got: {step_id!r}"
    )


def test_execute_returns_action_buttons(start_app):
    step_id = _get_step_id()
    body = {
        "action": "execute",
        "workflowId": WORKFLOW_ID,
        "stepId": step_id,
        "payload": {"requester": "Alice"},
        "controls": {},
        "inputs": {},
        "subscriber": {"subscriberId": "test-subscriber"},
        "state": [],
    }
    resp = requests.post(
        f"{BRIDGE_URL}?action=execute&workflowId={WORKFLOW_ID}&stepId={step_id}",
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    assert resp.status_code == 200, (
        f"execute request failed: status={resp.status_code} body={resp.text}"
    )
    payload = resp.json()
    outputs = payload.get("outputs", {})
    assert outputs.get("body") == "You have a new approval request from Alice.", (
        f"Unexpected outputs.body: {outputs.get('body')!r}"
    )
    primary = outputs.get("primaryAction") or {}
    assert primary.get("label") == "Approve", (
        f"Expected primaryAction.label='Approve', got: {primary}"
    )
    assert (primary.get("redirect") or {}).get("url") == "/requests/approve", (
        f"Expected primaryAction.redirect.url='/requests/approve', got: {primary}"
    )
    secondary = outputs.get("secondaryAction") or {}
    assert secondary.get("label") == "Decline", (
        f"Expected secondaryAction.label='Decline', got: {secondary}"
    )
    assert (secondary.get("redirect") or {}).get("url") == "/requests/decline", (
        f"Expected secondaryAction.redirect.url='/requests/decline', got: {secondary}"
    )


def test_execute_with_different_requester(start_app):
    step_id = _get_step_id()
    body = {
        "action": "execute",
        "workflowId": WORKFLOW_ID,
        "stepId": step_id,
        "payload": {"requester": "Bob"},
        "controls": {},
        "inputs": {},
        "subscriber": {"subscriberId": "test-subscriber"},
        "state": [],
    }
    resp = requests.post(
        f"{BRIDGE_URL}?action=execute&workflowId={WORKFLOW_ID}&stepId={step_id}",
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    assert resp.status_code == 200, (
        f"execute request failed: status={resp.status_code} body={resp.text}"
    )
    outputs = resp.json().get("outputs", {})
    assert outputs.get("body") == "You have a new approval request from Bob.", (
        f"Unexpected outputs.body for Bob: {outputs.get('body')!r}"
    )
    assert (outputs.get("primaryAction") or {}).get("label") == "Approve", (
        f"primaryAction.label changed unexpectedly: {outputs.get('primaryAction')}"
    )
    assert (outputs.get("secondaryAction") or {}).get("label") == "Decline", (
        f"secondaryAction.label changed unexpectedly: {outputs.get('secondaryAction')}"
    )


def test_execute_rejects_missing_requester(start_app):
    step_id = _get_step_id()
    body = {
        "action": "execute",
        "workflowId": WORKFLOW_ID,
        "stepId": step_id,
        "payload": {},
        "controls": {},
        "inputs": {},
        "subscriber": {"subscriberId": "test-subscriber"},
        "state": [],
    }
    resp = requests.post(
        f"{BRIDGE_URL}?action=execute&workflowId={WORKFLOW_ID}&stepId={step_id}",
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    assert resp.status_code >= 400, (
        f"Expected a 4xx/5xx response when 'requester' is missing, got {resp.status_code}: {resp.text}"
    )
    text = resp.text.lower()
    assert "requester" in text or "payload" in text, (
        f"Expected error response to mention 'requester' or 'payload', got: {resp.text}"
    )
