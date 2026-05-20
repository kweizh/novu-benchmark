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
        env = os.environ.copy()
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


@pytest.fixture(scope="session")
def discover_response(start_app):
    resp = requests.get(DISCOVER_URL, timeout=30)
    assert resp.status_code == 200, (
        f"Expected 200 from {DISCOVER_URL}, got {resp.status_code}: {resp.text}"
    )
    data = resp.json()
    return data


def _get_workflows(data):
    assert isinstance(data, dict), f"Discover response must be a JSON object, got: {type(data).__name__}"
    workflows = data.get("workflows")
    assert isinstance(workflows, list), (
        f"Discover response must contain a 'workflows' array, got: {workflows!r}"
    )
    return workflows


def _find_workflow(workflows, workflow_id):
    for wf in workflows:
        if not isinstance(wf, dict):
            continue
        if wf.get("workflowId") == workflow_id:
            return wf
    return None


def _find_step(workflow, step_id):
    steps = workflow.get("steps")
    assert isinstance(steps, list), (
        f"Workflow {workflow.get('workflowId')!r} must contain a 'steps' array, got: {steps!r}"
    )
    for st in steps:
        if isinstance(st, dict) and st.get("stepId") == step_id:
            return st
    return None


def test_discover_returns_three_workflows(discover_response):
    workflows = _get_workflows(discover_response)
    ids = [w.get("workflowId") for w in workflows if isinstance(w, dict)]
    assert len(workflows) == 3, (
        f"Expected exactly 3 workflows in discover response, found {len(workflows)}: {ids}"
    )
    for expected in ("welcome-user", "password-reset", "weekly-digest"):
        assert expected in ids, (
            f"Expected workflow id {expected!r} to be in discover response, got: {ids}"
        )


def test_welcome_user_workflow(discover_response):
    workflows = _get_workflows(discover_response)
    wf = _find_workflow(workflows, "welcome-user")
    assert wf is not None, "Workflow 'welcome-user' not found in discover response."
    step = _find_step(wf, "notify")
    assert step is not None, "Step 'notify' not found in workflow 'welcome-user'."
    assert step.get("type") == "in_app", (
        f"Step 'notify' in 'welcome-user' must be of type 'in_app', got: {step.get('type')!r}"
    )


def test_password_reset_workflow(discover_response):
    workflows = _get_workflows(discover_response)
    wf = _find_workflow(workflows, "password-reset")
    assert wf is not None, "Workflow 'password-reset' not found in discover response."
    step = _find_step(wf, "reset-email")
    assert step is not None, "Step 'reset-email' not found in workflow 'password-reset'."
    assert step.get("type") == "email", (
        f"Step 'reset-email' in 'password-reset' must be of type 'email', got: {step.get('type')!r}"
    )


def test_weekly_digest_workflow(discover_response):
    workflows = _get_workflows(discover_response)
    wf = _find_workflow(workflows, "weekly-digest")
    assert wf is not None, "Workflow 'weekly-digest' not found in discover response."
    steps = wf.get("steps")
    assert isinstance(steps, list), (
        f"'weekly-digest' must contain a 'steps' array, got: {steps!r}"
    )
    assert len(steps) == 2, (
        f"'weekly-digest' must have exactly 2 steps (digest then email), got {len(steps)}: {steps}"
    )
    first, second = steps[0], steps[1]
    assert first.get("stepId") == "batch", (
        f"First step of 'weekly-digest' must have stepId 'batch', got: {first.get('stepId')!r}"
    )
    assert first.get("type") == "digest", (
        f"First step of 'weekly-digest' must be of type 'digest', got: {first.get('type')!r}"
    )
    assert second.get("stepId") == "summary", (
        f"Second step of 'weekly-digest' must have stepId 'summary', got: {second.get('stepId')!r}"
    )
    assert second.get("type") == "email", (
        f"Second step of 'weekly-digest' must be of type 'email', got: {second.get('type')!r}"
    )
