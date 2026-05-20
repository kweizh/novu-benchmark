import os
import socket
import time

import pytest
import requests
from xprocess import ProcessStarter


PROJECT_DIR = "/home/user/app"
BRIDGE_URL = "http://localhost:3000/api/novu"


def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "novu_bridge"
        args = ["node", "index.js"]
        env = os.environ.copy()
        # The verifier wants the bridge to be reachable without a signed request.
        env["NOVU_STRICT_AUTHENTICATION_ENABLED"] = "false"
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 60
        terminate_on_interrupt = True

        def startup_check(self):
            return _port_open("localhost", 3000)

    xprocess.ensure(Starter.name, Starter)

    # Give the bridge a brief moment to finish handler registration.
    for _ in range(20):
        try:
            r = requests.get(BRIDGE_URL, params={"action": "discover"}, timeout=2)
            if r.status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(0.5)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()


@pytest.fixture(scope="session")
def discover_payload(start_app):
    response = requests.get(
        BRIDGE_URL, params={"action": "discover"}, timeout=10
    )
    assert response.status_code == 200, (
        "Expected discover endpoint to return 200, got "
        f"{response.status_code}: {response.text[:200]}"
    )
    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type, (
        f"Expected JSON content type from discover, got {content_type!r}"
    )
    return response.json()


def test_discover_returns_workflows_array(discover_payload):
    assert isinstance(discover_payload, dict), (
        "Expected discover response body to be a JSON object."
    )
    workflows = discover_payload.get("workflows")
    assert isinstance(workflows, list), (
        f"Expected 'workflows' to be a list in discover response, "
        f"got {type(workflows).__name__}."
    )
    assert len(workflows) == 1, (
        f"Expected exactly one workflow in discover response, got {len(workflows)}."
    )


def test_workflow_identity(discover_payload):
    workflow = discover_payload["workflows"][0]
    assert workflow.get("workflowId") == "security-alert", (
        f"Expected workflowId 'security-alert', got {workflow.get('workflowId')!r}."
    )


def test_workflow_steps(discover_payload):
    workflow = discover_payload["workflows"][0]
    steps = workflow.get("steps")
    assert isinstance(steps, list), (
        f"Expected 'steps' to be a list, got {type(steps).__name__}."
    )
    assert len(steps) == 2, (
        f"Expected exactly 2 steps in the security-alert workflow, got {len(steps)}."
    )

    assert steps[0].get("stepId") == "alert-email", (
        f"Expected first step stepId 'alert-email', got {steps[0].get('stepId')!r}."
    )
    assert steps[0].get("type") == "email", (
        f"Expected first step type 'email', got {steps[0].get('type')!r}."
    )

    assert steps[1].get("stepId") == "alert-sms", (
        f"Expected second step stepId 'alert-sms', got {steps[1].get('stepId')!r}."
    )
    assert steps[1].get("type") == "sms", (
        f"Expected second step type 'sms', got {steps[1].get('type')!r}."
    )


def test_workflow_is_critical(discover_payload):
    workflow = discover_payload["workflows"][0]
    preferences = workflow.get("preferences")
    assert isinstance(preferences, dict), (
        "Expected workflow.preferences to be an object in the discover response, "
        f"got {type(preferences).__name__}."
    )
    all_pref = preferences.get("all")
    assert isinstance(all_pref, dict), (
        "Expected workflow.preferences.all to be an object, "
        f"got {type(all_pref).__name__}."
    )
    assert all_pref.get("readOnly") is True, (
        "Expected workflow to be critical (preferences.all.readOnly === true), "
        f"got readOnly={all_pref.get('readOnly')!r}."
    )


def test_channel_default_values(discover_payload):
    workflow = discover_payload["workflows"][0]
    channels = workflow["preferences"].get("channels")
    assert isinstance(channels, dict), (
        "Expected workflow.preferences.channels to be an object, "
        f"got {type(channels).__name__}."
    )

    email = channels.get("email")
    assert isinstance(email, dict), (
        f"Expected channels.email to be an object, got {type(email).__name__}."
    )
    assert email.get("enabled") is True, (
        "Expected channels.email.enabled === true, "
        f"got {email.get('enabled')!r}."
    )

    sms = channels.get("sms")
    assert isinstance(sms, dict), (
        f"Expected channels.sms to be an object, got {type(sms).__name__}."
    )
    assert sms.get("enabled") is False, (
        "Expected channels.sms.enabled === false, "
        f"got {sms.get('enabled')!r}."
    )

    in_app = channels.get("inApp")
    assert isinstance(in_app, dict), (
        f"Expected channels.inApp to be an object, got {type(in_app).__name__}."
    )
    assert in_app.get("enabled") is True, (
        "Expected channels.inApp.enabled === true, "
        f"got {in_app.get('enabled')!r}."
    )
