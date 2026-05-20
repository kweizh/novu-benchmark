import os
import socket
import subprocess

import pytest
import requests
from xprocess import ProcessStarter


PROJECT_DIR = "/home/user/app"
PORT = 3000
BASE_URL = f"http://localhost:{PORT}"
WORKFLOW_ID = "quiet-hours-notifier"
STEP_INAPP = "notify-inapp"
STEP_PUSH = "notify-push"


@pytest.fixture(scope="session")
def start_app(xprocess):
    """Start the Novu Bridge Express server and wait until it is ready."""

    # Make sure no leftover process is bound to the port from a previous run.
    subprocess.run(
        ["bash", "-lc", f"fuser -k {PORT}/tcp || true"],
        check=False,
        capture_output=True,
    )

    class Starter(ProcessStarter):
        name = "novu_bridge"
        args = ["node", "index.js"]
        env = os.environ.copy()
        env.setdefault("NOVU_STRICT_AUTHENTICATION_ENABLED", "false")
        env["NODE_ENV"] = env.get("NODE_ENV", "development")
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", PORT)) == 0

    xprocess.ensure(Starter.name, Starter)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _execute_push(payload, state=None):
    if state is None:
        state = [
            {
                "stepId": STEP_INAPP,
                "outputs": {"body": f"Heads up: {payload.get('message', '')}"},
            }
        ]
    body = {
        "payload": payload,
        "controls": {},
        "state": state,
        "subscriber": {"subscriberId": "sub_test"},
    }
    return requests.post(
        f"{BASE_URL}/",
        params={
            "action": "execute",
            "workflowId": WORKFLOW_ID,
            "stepId": STEP_PUSH,
        },
        json=body,
        timeout=30,
    )


def test_discover_endpoint_lists_workflow_and_steps(start_app):
    response = requests.get(
        f"{BASE_URL}/", params={"action": "discover"}, timeout=30
    )
    assert response.status_code == 200, (
        f"GET /?action=discover returned status {response.status_code}, "
        f"body: {response.text}"
    )

    data = response.json()
    workflows = data.get("workflows")
    assert isinstance(workflows, list) and len(workflows) > 0, (
        f"Expected 'workflows' to be a non-empty list, got: {workflows!r}"
    )

    matching = [w for w in workflows if w.get("workflowId") == WORKFLOW_ID]
    assert matching, (
        f"Expected a workflow with workflowId '{WORKFLOW_ID}', got workflows: "
        f"{[w.get('workflowId') for w in workflows]}"
    )

    workflow = matching[0]
    steps = workflow.get("steps")
    assert isinstance(steps, list), (
        f"Expected workflow 'steps' to be a list, got: {steps!r}"
    )

    step_ids = [s.get("stepId") for s in steps]
    assert step_ids == [STEP_INAPP, STEP_PUSH], (
        f"Expected steps in order [{STEP_INAPP!r}, {STEP_PUSH!r}], got: {step_ids!r}"
    )

    by_id = {s.get("stepId"): s for s in steps}
    assert by_id[STEP_INAPP].get("type") == "in_app", (
        f"Expected step '{STEP_INAPP}' to have type 'in_app', "
        f"got: {by_id[STEP_INAPP].get('type')!r}"
    )
    assert by_id[STEP_PUSH].get("type") == "push", (
        f"Expected step '{STEP_PUSH}' to have type 'push', "
        f"got: {by_id[STEP_PUSH].get('type')!r}"
    )


def test_push_step_runs_when_quiet_hours_false(start_app):
    response = _execute_push({"message": "Hello", "quietHours": False})
    assert response.status_code == 200, (
        f"Expected status 200, got {response.status_code}, body: {response.text}"
    )

    data = response.json()
    options = data.get("options") or {}
    outputs = data.get("outputs") or {}

    assert options.get("skip") is False, (
        f"Expected options.skip to be False when quietHours=false, "
        f"got: {options!r} (full response: {data!r})"
    )
    assert outputs.get("subject") == "Notification", (
        f"Expected outputs.subject == 'Notification', got: {outputs.get('subject')!r}"
    )
    assert outputs.get("body") == "Hello", (
        f"Expected outputs.body == 'Hello' (templated from payload.message), "
        f"got: {outputs.get('body')!r}"
    )


def test_push_step_skipped_when_quiet_hours_true(start_app):
    response = _execute_push({"message": "Hello", "quietHours": True})
    assert response.status_code == 200, (
        f"Expected status 200, got {response.status_code}, body: {response.text}"
    )

    data = response.json()
    options = data.get("options") or {}
    outputs = data.get("outputs")

    assert options.get("skip") is True, (
        f"Expected options.skip to be True when quietHours=true, "
        f"got: {options!r} (full response: {data!r})"
    )
    assert outputs == {} or outputs is None, (
        f"Expected outputs to be empty when the step is skipped, got: {outputs!r}"
    )


def test_payload_validation_rejects_missing_quiet_hours(start_app):
    body = {
        "payload": {"message": "Hello"},
        "controls": {},
        "state": [
            {"stepId": STEP_INAPP, "outputs": {"body": "Heads up: Hello"}}
        ],
        "subscriber": {"subscriberId": "sub_test"},
    }
    response = requests.post(
        f"{BASE_URL}/",
        params={
            "action": "execute",
            "workflowId": WORKFLOW_ID,
            "stepId": STEP_PUSH,
        },
        json=body,
        timeout=30,
    )

    assert response.status_code >= 400, (
        "Expected a >=400 status code when the payload is missing 'quietHours', "
        f"got {response.status_code}, body: {response.text}"
    )
