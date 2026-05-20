import os
import socket

import pytest
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/app"
PORT = 3000
BASE_URL = f"http://localhost:{PORT}"
BRIDGE_PATH = "/api/novu"


@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "novu_bridge_app"
        args = ["node", "index.js"]
        env = os.environ.copy()
        env.setdefault("NOVU_STRICT_AUTHENTICATION_ENABLED", "false")
        env.setdefault("PORT", str(PORT))
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 60
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", PORT)) == 0

    xprocess.ensure(Starter.name, Starter)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()


def test_health_check_endpoint_returns_ok(start_app):
    url = f"{BASE_URL}{BRIDGE_PATH}"
    response = requests.get(url, params={"action": "health-check"}, timeout=15)
    assert response.status_code == 200, (
        f"Expected HTTP 200 from health-check, got {response.status_code}. Body: {response.text!r}"
    )
    body = response.json()
    assert isinstance(body, dict), f"Expected JSON object from health-check, got: {body!r}"
    assert body.get("status") == "ok", (
        f"Expected health-check 'status' == 'ok', got: {body.get('status')!r} in {body!r}"
    )


def test_health_check_reports_sdk_and_framework_versions(start_app):
    url = f"{BASE_URL}{BRIDGE_PATH}"
    response = requests.get(url, params={"action": "health-check"}, timeout=15)
    assert response.status_code == 200, (
        f"Expected HTTP 200, got {response.status_code}. Body: {response.text!r}"
    )
    body = response.json()
    sdk_version = body.get("sdkVersion")
    framework_version = body.get("frameworkVersion")
    assert isinstance(sdk_version, str) and sdk_version, (
        f"Expected non-empty 'sdkVersion' string, got: {sdk_version!r}"
    )
    assert isinstance(framework_version, str) and framework_version, (
        f"Expected non-empty 'frameworkVersion' string, got: {framework_version!r}"
    )


def test_health_check_reports_discovered_counts(start_app):
    url = f"{BASE_URL}{BRIDGE_PATH}"
    response = requests.get(url, params={"action": "health-check"}, timeout=15)
    assert response.status_code == 200, (
        f"Expected HTTP 200, got {response.status_code}. Body: {response.text!r}"
    )
    body = response.json()
    discovered = body.get("discovered")
    assert isinstance(discovered, dict), (
        f"Expected 'discovered' object in health-check response, got: {discovered!r}"
    )
    workflow_count = discovered.get("workflows")
    step_count = discovered.get("steps")
    assert isinstance(workflow_count, int) and workflow_count >= 1, (
        f"Expected 'discovered.workflows' to be an int >= 1, got: {workflow_count!r}"
    )
    assert isinstance(step_count, int) and step_count >= 1, (
        f"Expected 'discovered.steps' to be an int >= 1, got: {step_count!r}"
    )


def test_discover_endpoint_returns_system_ping_workflow(start_app):
    url = f"{BASE_URL}{BRIDGE_PATH}"
    response = requests.get(url, params={"action": "discover"}, timeout=15)
    assert response.status_code == 200, (
        f"Expected HTTP 200 from discover, got {response.status_code}. Body: {response.text!r}"
    )
    body = response.json()
    workflows = body.get("workflows")
    assert isinstance(workflows, list) and len(workflows) >= 1, (
        f"Expected non-empty 'workflows' array in discover response, got: {workflows!r}"
    )
    matching = [w for w in workflows if w.get("workflowId") == "system-ping"]
    assert len(matching) == 1, (
        f"Expected exactly one workflow with workflowId 'system-ping', got: "
        f"{[w.get('workflowId') for w in workflows]!r}"
    )
    workflow = matching[0]
    steps = workflow.get("steps")
    assert isinstance(steps, list) and len(steps) >= 1, (
        f"Expected 'steps' array on 'system-ping' workflow, got: {steps!r}"
    )
    matching_steps = [s for s in steps if s.get("stepId") == "ping-step"]
    assert len(matching_steps) == 1, (
        f"Expected exactly one step with stepId 'ping-step' on workflow 'system-ping', "
        f"got: {[s.get('stepId') for s in steps]!r}"
    )
    step = matching_steps[0]
    assert step.get("type") == "in_app", (
        f"Expected 'ping-step' to be of type 'in_app', got: {step.get('type')!r}"
    )
