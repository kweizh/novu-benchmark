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
    """Start the Novu Bridge Express server and wait until port 3000 is open."""

    class Starter(ProcessStarter):
        name = "novu_bridge_app"
        args = ["npm", "start"]
        env = {
            **os.environ,
            "NOVU_SECRET_KEY": os.environ.get(
                "NOVU_SECRET_KEY", "test-secret-key"
            ),
            "NOVU_STRICT_AUTHENTICATION_ENABLED": "false",
            "NODE_ENV": "development",
            "PORT": "3000",
        }
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("localhost", 3000)) != 0:
                    return False
            try:
                r = requests.get(BASE_URL + BRIDGE_PATH, timeout=5)
                return r.status_code == 200
            except requests.RequestException:
                return False

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def test_health_check_returns_200(start_app):
    response = requests.get(BASE_URL + BRIDGE_PATH, timeout=10)
    assert response.status_code == 200, (
        f"Expected 200 from health check, got {response.status_code}: "
        f"{response.text}"
    )
    # Health response should be valid JSON.
    try:
        response.json()
    except ValueError as exc:
        raise AssertionError(
            f"Health check response was not valid JSON: {response.text}"
        ) from exc


def test_discover_lists_notification_digest_workflow(start_app):
    response = requests.get(
        BASE_URL + BRIDGE_PATH,
        params={"action": "discover"},
        timeout=10,
    )
    assert response.status_code == 200, (
        f"Expected 200 from discover, got {response.status_code}: "
        f"{response.text}"
    )
    data = response.json()
    workflows = data.get("workflows")
    assert isinstance(workflows, list), (
        f"Expected 'workflows' to be a list in discover output, got: {data}"
    )

    target = next(
        (w for w in workflows if w.get("workflowId") == "notification-digest"),
        None,
    )
    assert target is not None, (
        "Expected a workflow with workflowId 'notification-digest' in discover "
        f"output, got: {[w.get('workflowId') for w in workflows]}"
    )

    steps = target.get("steps") or []
    assert len(steps) == 2, (
        f"Expected 2 steps in 'notification-digest' workflow, got {len(steps)}: "
        f"{steps}"
    )
    assert steps[0].get("stepId") == "batch-events", (
        f"Expected first stepId 'batch-events', got: {steps[0].get('stepId')}"
    )
    assert steps[0].get("type") == "digest", (
        f"Expected first step type 'digest', got: {steps[0].get('type')}"
    )
    assert steps[1].get("stepId") == "summary-email", (
        f"Expected second stepId 'summary-email', got: {steps[1].get('stepId')}"
    )
    assert steps[1].get("type") == "email", (
        f"Expected second step type 'email', got: {steps[1].get('type')}"
    )


def test_digest_step_preview_returns_lookback_window_config(start_app):
    body = {
        "payload": {},
        "subscriber": {},
        "state": [],
        "controls": {},
        "context": {},
        "env": {},
    }
    response = requests.post(
        BASE_URL + BRIDGE_PATH,
        params={
            "action": "preview",
            "workflowId": "notification-digest",
            "stepId": "batch-events",
        },
        json=body,
        timeout=15,
    )
    assert response.status_code == 200, (
        f"Expected 200 from digest preview, got {response.status_code}: "
        f"{response.text}"
    )
    data = response.json()
    outputs = data.get("outputs")
    assert isinstance(outputs, dict), (
        f"Expected 'outputs' object in digest preview response, got: {data}"
    )
    assert outputs.get("amount") == 5, (
        f"Expected digest amount=5, got: {outputs.get('amount')}"
    )
    assert outputs.get("unit") == "seconds", (
        f"Expected digest unit='seconds', got: {outputs.get('unit')}"
    )
    look_back = outputs.get("lookBackWindow")
    assert isinstance(look_back, dict), (
        "Expected 'lookBackWindow' object on digest step outputs, got: "
        f"{outputs.get('lookBackWindow')}"
    )
    assert look_back.get("amount") == 10, (
        f"Expected lookBackWindow.amount=10, got: {look_back.get('amount')}"
    )
    assert look_back.get("unit") == "minutes", (
        f"Expected lookBackWindow.unit='minutes', got: {look_back.get('unit')}"
    )


def test_email_step_preview_renders_subject_with_event_count(start_app):
    body = {
        "payload": {},
        "subscriber": {},
        "state": [
            {
                "stepId": "batch-events",
                "outputs": {
                    "events": [
                        {
                            "id": "evt-1",
                            "time": "2024-01-01T00:00:00.000Z",
                            "payload": {},
                        },
                        {
                            "id": "evt-2",
                            "time": "2024-01-01T00:00:01.000Z",
                            "payload": {},
                        },
                        {
                            "id": "evt-3",
                            "time": "2024-01-01T00:00:02.000Z",
                            "payload": {},
                        },
                    ]
                },
                "state": {"status": "completed"},
            }
        ],
        "controls": {},
        "context": {},
        "env": {},
    }
    response = requests.post(
        BASE_URL + BRIDGE_PATH,
        params={
            "action": "preview",
            "workflowId": "notification-digest",
            "stepId": "summary-email",
        },
        json=body,
        timeout=15,
    )
    assert response.status_code == 200, (
        f"Expected 200 from email preview, got {response.status_code}: "
        f"{response.text}"
    )
    data = response.json()
    outputs = data.get("outputs")
    assert isinstance(outputs, dict), (
        f"Expected 'outputs' object in email preview response, got: {data}"
    )
    assert outputs.get("subject") == "You have 3 new notifications", (
        "Expected email subject 'You have 3 new notifications', got: "
        f"{outputs.get('subject')}"
    )
    assert outputs.get("body") == "Check them out in your dashboard.", (
        f"Expected email body 'Check them out in your dashboard.', got: "
        f"{outputs.get('body')}"
    )
