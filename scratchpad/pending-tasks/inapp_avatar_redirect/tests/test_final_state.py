import os
import socket
import pytest
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/app"
BASE_URL = "http://localhost:3000"
NOVU_PATH = "/api/novu"


@pytest.fixture(scope="session")
def start_app(xprocess):
    """Start the Novu bridge Express server and wait for it to listen on port 3000."""

    class Starter(ProcessStarter):
        name = "start_app"
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
                return s.connect_ex(("localhost", 3000)) == 0

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _discover(timeout=30):
    return requests.get(
        f"{BASE_URL}{NOVU_PATH}",
        params={"action": "discover"},
        timeout=timeout,
    )


def _preview(payload, timeout=30):
    return requests.post(
        f"{BASE_URL}{NOVU_PATH}",
        params={
            "action": "preview",
            "workflowId": "comment-mention",
            "stepId": "notify-mention",
        },
        json={"data": payload},
        headers={"Content-Type": "application/json"},
        timeout=timeout,
    )


def test_discover_lists_workflow_and_step(start_app):
    response = _discover()
    assert response.status_code == 200, (
        f"Discover endpoint returned {response.status_code}: {response.text}"
    )
    payload = response.json()
    workflows = payload.get("workflows") or payload.get("data", {}).get("workflows")
    assert isinstance(workflows, list) and workflows, (
        f"Discover response should contain non-empty 'workflows' array, got: {payload}"
    )
    workflow = next(
        (w for w in workflows if w.get("workflowId") == "comment-mention"),
        None,
    )
    assert workflow is not None, (
        f"Expected workflow with workflowId 'comment-mention' in discover response. Got workflows: {workflows}"
    )
    steps = workflow.get("steps") or []
    step = next((s for s in steps if s.get("stepId") == "notify-mention"), None)
    assert step is not None, (
        f"Expected step 'notify-mention' inside workflow 'comment-mention'. Got steps: {steps}"
    )
    step_type = step.get("type") or step.get("stepType")
    assert step_type == "in_app", (
        f"Expected step type 'in_app' for 'notify-mention', got: {step_type}"
    )


def test_preview_outputs_with_valid_payload(start_app):
    payload = {
        "commenter": "Alice",
        "threadTitle": "Design Review",
        "threadId": "t-42",
    }
    response = _preview(payload)
    assert response.status_code == 200, (
        f"Preview returned {response.status_code}: {response.text}"
    )
    body = response.json()
    outputs = body.get("outputs") or body.get("data", {}).get("outputs")
    assert isinstance(outputs, dict), (
        f"Preview response must contain an 'outputs' object. Got: {body}"
    )
    assert outputs.get("subject") == "New mention", (
        f"Expected outputs.subject == 'New mention', got: {outputs.get('subject')}"
    )
    assert outputs.get("body") == "Alice mentioned you in Design Review", (
        f"Expected interpolated body, got: {outputs.get('body')}"
    )
    assert outputs.get("avatar") == "https://cdn.example.com/avatar.png", (
        f"Expected avatar URL, got: {outputs.get('avatar')}"
    )
    redirect = outputs.get("redirect")
    assert isinstance(redirect, dict), (
        f"Expected outputs.redirect to be an object, got: {redirect}"
    )
    assert redirect.get("url") == "/threads/t-42", (
        f"Expected redirect.url == '/threads/t-42', got: {redirect.get('url')}"
    )
    assert redirect.get("target") == "_self", (
        f"Expected redirect.target == '_self', got: {redirect.get('target')}"
    )


def test_preview_rejects_invalid_payload(start_app):
    response = _preview({"commenter": "Bob"})
    if 200 <= response.status_code < 300:
        body = {}
        try:
            body = response.json()
        except Exception:
            body = {"raw": response.text}
        text = str(body).lower()
        assert (
            "error" in text
            or "issue" in text
            or "invalid" in text
            or "required" in text
            or "validation" in text
        ), (
            f"Invalid payload should fail validation, but got 2xx with body: {body}"
        )
    else:
        assert response.status_code >= 400, (
            f"Expected non-2xx for invalid payload, got: {response.status_code}"
        )
