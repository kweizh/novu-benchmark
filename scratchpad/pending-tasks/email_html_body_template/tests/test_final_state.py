import os
import socket
import time

import pytest
import requests
from xprocess import ProcessStarter


PROJECT_DIR = "/home/user/app"
BASE_URL = "http://localhost:3000/api/novu"

EXPECTED_WORKFLOW_ID = "order-confirmation"
EXPECTED_STEP_ID = "order-email"
EXPECTED_STEP_TYPE = "email"
EXPECTED_SUBJECT = "Order #{{ payload.orderId }} confirmed"
EXPECTED_BODY = (
    "<h1>Thanks {{ payload.customerName }}!</h1>"
    "<p>Your order #{{ payload.orderId }} totalling "
    "${{ payload.amount }} is confirmed.</p>"
)


@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "novu_bridge"
        args = ["node", "index.js"]
        env = os.environ.copy()
        # Make sure HMAC strict auth is disabled by keeping NODE_ENV
        # in development mode.
        env["NODE_ENV"] = env.get("NODE_ENV", "development")
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
            # Additionally wait for the bridge health-check endpoint
            # to respond 200.
            try:
                resp = requests.get(
                    f"{BASE_URL}?action=health-check",
                    timeout=5,
                )
                return resp.status_code == 200
            except requests.RequestException:
                return False

    xprocess.ensure(Starter.name, Starter)
    # Small buffer to make sure the handler has registered all workflows.
    time.sleep(1)

    yield

    info = xprocess.getinfo(Starter.name)
    info.terminate()


def test_discover_lists_order_confirmation_workflow(start_app):
    """GET ?action=discover should return the order-confirmation workflow
    with the expected email step."""
    resp = requests.get(f"{BASE_URL}?action=discover", timeout=10)
    assert resp.status_code == 200, (
        f"Expected 200 from discover endpoint, "
        f"got {resp.status_code}: {resp.text}"
    )
    data = resp.json()
    assert "workflows" in data and isinstance(data["workflows"], list), (
        f"Discover response must include a 'workflows' array, got: {data}"
    )

    matching = [
        wf for wf in data["workflows"]
        if wf.get("workflowId") == EXPECTED_WORKFLOW_ID
    ]
    assert len(matching) == 1, (
        f"Expected exactly one workflow with workflowId="
        f"'{EXPECTED_WORKFLOW_ID}', got: "
        f"{[wf.get('workflowId') for wf in data['workflows']]}"
    )
    workflow = matching[0]

    steps = workflow.get("steps", [])
    assert isinstance(steps, list) and steps, (
        f"Workflow '{EXPECTED_WORKFLOW_ID}' must define at least one step, "
        f"got: {steps}"
    )

    email_steps = [
        s for s in steps
        if s.get("stepId") == EXPECTED_STEP_ID
    ]
    assert len(email_steps) == 1, (
        f"Expected exactly one step with stepId='{EXPECTED_STEP_ID}' in "
        f"workflow '{EXPECTED_WORKFLOW_ID}', got: "
        f"{[s.get('stepId') for s in steps]}"
    )
    step = email_steps[0]
    assert step.get("type") == EXPECTED_STEP_TYPE, (
        f"Step '{EXPECTED_STEP_ID}' must have type='{EXPECTED_STEP_TYPE}', "
        f"got: {step.get('type')}"
    )


def test_execute_returns_expected_subject_and_html_body(start_app):
    """POST ?action=execute should return outputs whose subject and body
    are exactly the configured Liquid template strings."""
    url = (
        f"{BASE_URL}?action=execute"
        f"&workflowId={EXPECTED_WORKFLOW_ID}"
        f"&stepId={EXPECTED_STEP_ID}"
    )
    body = {
        "payload": {
            "orderId": "ORD-1",
            "customerName": "Alice",
            "amount": 42,
        },
        "subscriber": {"subscriberId": "sub_test"},
        "state": [],
        "inputs": {},
        "controls": {},
    }
    resp = requests.post(
        url,
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    assert resp.status_code == 200, (
        f"Expected 200 from execute endpoint, "
        f"got {resp.status_code}: {resp.text}"
    )
    data = resp.json()
    outputs = data.get("outputs")
    assert isinstance(outputs, dict), (
        f"Execute response must contain a dict 'outputs' field, "
        f"got: {data}"
    )

    actual_subject = outputs.get("subject")
    assert actual_subject == EXPECTED_SUBJECT, (
        f"Email step 'subject' must equal the Liquid template "
        f"'{EXPECTED_SUBJECT}', got: {actual_subject!r}"
    )

    actual_body = outputs.get("body")
    assert actual_body == EXPECTED_BODY, (
        f"Email step 'body' must equal the HTML+Liquid template "
        f"'{EXPECTED_BODY}', got: {actual_body!r}"
    )


def test_execute_rejects_invalid_payload(start_app):
    """Zod payload schema must reject payloads missing required fields."""
    url = (
        f"{BASE_URL}?action=execute"
        f"&workflowId={EXPECTED_WORKFLOW_ID}"
        f"&stepId={EXPECTED_STEP_ID}"
    )
    body = {
        "payload": {},
        "subscriber": {"subscriberId": "sub_test"},
        "state": [],
        "inputs": {},
        "controls": {},
    }
    resp = requests.post(
        url,
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    assert not (200 <= resp.status_code < 300), (
        f"Expected a non-2xx response when payload is invalid (Zod schema "
        f"requires orderId/customerName/amount), but got "
        f"{resp.status_code}: {resp.text}"
    )
