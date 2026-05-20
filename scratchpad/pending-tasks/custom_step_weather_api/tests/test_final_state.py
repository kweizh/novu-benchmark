import os
import socket
import pytest
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/app"
PORT = 3000
BASE_URL = f"http://localhost:{PORT}"
NOVU_URL = f"{BASE_URL}/api/novu"


@pytest.fixture(scope="session")
def start_app(xprocess):
    """Start the Express + Novu bridge app and wait until port 3000 accepts connections."""

    class Starter(ProcessStarter):
        name = "start_app"
        args = ["node", "index.js"]
        env = {
            **os.environ.copy(),
            "NOVU_STRICT_AUTHENTICATION_ENABLED": "false",
        }
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("localhost", PORT)) != 0:
                    return False
            try:
                r = requests.get(f"{BASE_URL}/api/weather", params={"city": "ping"}, timeout=2)
                return r.status_code == 200
            except Exception:
                return False

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def test_mock_weather_endpoint(start_app):
    resp = requests.get(f"{BASE_URL}/api/weather", params={"city": "Paris"}, timeout=10)
    assert resp.status_code == 200, (
        f"GET /api/weather?city=Paris expected 200, got {resp.status_code}: {resp.text}"
    )
    data = resp.json()
    assert data == {"city": "Paris", "tempC": 22, "conditions": "Sunny"}, (
        f"Unexpected mock weather payload: {data}"
    )


def test_bridge_discover_lists_workflow_and_steps(start_app):
    resp = requests.get(NOVU_URL, params={"action": "discover"}, timeout=15)
    assert resp.status_code == 200, (
        f"GET /api/novu?action=discover expected 200, got {resp.status_code}: {resp.text}"
    )
    data = resp.json()

    workflows = data.get("workflows")
    assert isinstance(workflows, list) and len(workflows) > 0, (
        f"Discover response missing workflows list: {data}"
    )

    target = None
    for wf in workflows:
        if wf.get("workflowId") == "weather-update":
            target = wf
            break
    assert target is not None, (
        f"Discover response does not include workflow 'weather-update': {workflows}"
    )

    steps = target.get("steps", [])
    step_ids = [s.get("stepId") for s in steps]
    assert "fetch-weather" in step_ids, (
        f"Workflow 'weather-update' is missing step 'fetch-weather'. Steps: {step_ids}"
    )
    assert "weather-email" in step_ids, (
        f"Workflow 'weather-update' is missing step 'weather-email'. Steps: {step_ids}"
    )
    assert step_ids.index("fetch-weather") < step_ids.index("weather-email"), (
        f"Expected 'fetch-weather' before 'weather-email'. Steps: {step_ids}"
    )

    types_by_id = {s.get("stepId"): s.get("type") for s in steps}
    assert types_by_id.get("fetch-weather") == "custom", (
        f"Expected 'fetch-weather' to be type 'custom', got {types_by_id.get('fetch-weather')}"
    )
    assert types_by_id.get("weather-email") == "email", (
        f"Expected 'weather-email' to be type 'email', got {types_by_id.get('weather-email')}"
    )


def test_execute_fetch_weather_step(start_app):
    body = {
        "inputs": {},
        "controls": {},
        "payload": {"city": "Paris"},
        "state": [],
        "subscriber": {"subscriberId": "test-subscriber"},
        "workflowId": "weather-update",
        "stepId": "fetch-weather",
        "action": "execute",
    }
    resp = requests.post(
        NOVU_URL,
        params={
            "action": "execute",
            "workflowId": "weather-update",
            "stepId": "fetch-weather",
        },
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=20,
    )
    assert resp.status_code == 200, (
        f"Execute fetch-weather expected 200, got {resp.status_code}: {resp.text}"
    )
    data = resp.json()
    outputs = data.get("outputs")
    assert outputs == {"city": "Paris", "tempC": 22, "conditions": "Sunny"}, (
        f"Unexpected outputs from fetch-weather: {outputs}. Full response: {data}"
    )


def test_execute_weather_email_step_with_prior_state(start_app):
    body = {
        "inputs": {},
        "controls": {},
        "payload": {"city": "Paris"},
        "state": [
            {
                "stepId": "fetch-weather",
                "outputs": {"city": "Paris", "tempC": 22, "conditions": "Sunny"},
                "state": {"status": "completed"},
            }
        ],
        "subscriber": {"subscriberId": "test-subscriber"},
        "workflowId": "weather-update",
        "stepId": "weather-email",
        "action": "execute",
    }
    resp = requests.post(
        NOVU_URL,
        params={
            "action": "execute",
            "workflowId": "weather-update",
            "stepId": "weather-email",
        },
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=20,
    )
    assert resp.status_code == 200, (
        f"Execute weather-email expected 200, got {resp.status_code}: {resp.text}"
    )
    data = resp.json()
    outputs = data.get("outputs", {})
    assert outputs.get("subject") == "Weather for Paris", (
        f"Expected subject 'Weather for Paris', got {outputs.get('subject')!r}. Full response: {data}"
    )
    assert outputs.get("body") == "It's 22°C and Sunny.", (
        f"Expected body \"It's 22°C and Sunny.\", got {outputs.get('body')!r}. Full response: {data}"
    )
