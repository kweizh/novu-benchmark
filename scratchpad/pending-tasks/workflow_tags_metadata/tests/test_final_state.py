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
def start_bridge(xprocess):
    class Starter(ProcessStarter):
        name = "novu_bridge"
        args = ["node", "index.js"]
        env = {
            **os.environ.copy(),
            "NOVU_STRICT_AUTHENTICATION_ENABLED": "false",
            "PORT": str(PORT),
        }
        popen_kwargs = {"cwd": PROJECT_DIR, "text": True}
        timeout = 60
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(("localhost", PORT)) == 0

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _get_discover(start_bridge):
    url = f"{BASE_URL}{BRIDGE_PATH}"
    response = requests.get(url, params={"action": "discover"}, timeout=30)
    assert response.status_code == 200, (
        f"Discover endpoint did not return 200. Got {response.status_code}: {response.text}"
    )
    body = response.json()
    assert isinstance(body, dict), "Discover response must be a JSON object."
    assert "workflows" in body and isinstance(body["workflows"], list), (
        "Discover response must contain a 'workflows' array."
    )
    return body


def _find_marketing_workflow(discover_body):
    workflows = discover_body["workflows"]
    matches = [w for w in workflows if w.get("workflowId") == "marketing-campaign"]
    assert len(matches) == 1, (
        f"Expected exactly one workflow with workflowId 'marketing-campaign', "
        f"found {len(matches)}. Workflows: {workflows}"
    )
    return matches[0]


def test_discover_returns_marketing_campaign_workflow(start_bridge):
    body = _get_discover(start_bridge)
    workflow = _find_marketing_workflow(body)
    assert workflow.get("workflowId") == "marketing-campaign", (
        f"workflowId must be 'marketing-campaign', got {workflow.get('workflowId')!r}."
    )


def test_workflow_name_is_marketing_campaign(start_bridge):
    body = _get_discover(start_bridge)
    workflow = _find_marketing_workflow(body)
    assert workflow.get("name") == "Marketing Campaign", (
        f"workflow.name must be 'Marketing Campaign', got {workflow.get('name')!r}."
    )


def test_workflow_description_matches(start_bridge):
    body = _get_discover(start_bridge)
    workflow = _find_marketing_workflow(body)
    expected = "Promotional emails for new product launches."
    assert workflow.get("description") == expected, (
        f"workflow.description must be {expected!r}, got {workflow.get('description')!r}."
    )


def test_workflow_tags_match_exactly(start_bridge):
    body = _get_discover(start_bridge)
    workflow = _find_marketing_workflow(body)
    expected_tags = ["marketing", "promotion", "product-launch"]
    tags = workflow.get("tags")
    assert isinstance(tags, list), f"workflow.tags must be a list, got {type(tags).__name__}."
    assert tags == expected_tags, (
        f"workflow.tags must equal {expected_tags!r} (exact order), got {tags!r}."
    )


def test_workflow_has_single_email_step(start_bridge):
    body = _get_discover(start_bridge)
    workflow = _find_marketing_workflow(body)
    steps = workflow.get("steps")
    assert isinstance(steps, list), "workflow.steps must be a list."
    assert len(steps) == 1, f"Expected exactly one step in workflow, got {len(steps)}: {steps}"
    step = steps[0]
    assert step.get("stepId") == "promo-email", (
        f"Step stepId must be 'promo-email', got {step.get('stepId')!r}."
    )
    assert step.get("type") == "email", (
        f"Step type must be 'email', got {step.get('type')!r}."
    )


def test_email_step_preview_outputs_subject_and_body(start_bridge):
    url = f"{BASE_URL}{BRIDGE_PATH}"
    payload = {
        "inputs": {},
        "controls": {},
        "payload": {},
        "data": {},
        "state": [],
        "subscriber": {"subscriberId": "verifier"},
    }
    response = requests.post(
        url,
        params={
            "action": "preview",
            "workflowId": "marketing-campaign",
            "stepId": "promo-email",
        },
        json=payload,
        timeout=30,
    )
    assert response.status_code == 200, (
        f"Preview endpoint did not return 200. Got {response.status_code}: {response.text}"
    )
    body = response.json()

    # Find subject/body anywhere within the outputs object (Novu may return
    # them under `outputs` or nested keys).
    def _flatten(obj):
        flat = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    flat.update(_flatten(v))
                else:
                    flat[k] = v
        elif isinstance(obj, list):
            for item in obj:
                flat.update(_flatten(item))
        return flat

    flat = _flatten(body)
    assert flat.get("subject") == "Big launch!", (
        f"Email step subject must be 'Big launch!', got {flat.get('subject')!r}. "
        f"Full response: {body}"
    )
    assert flat.get("body") == "Check out our new product.", (
        f"Email step body must be 'Check out our new product.', got {flat.get('body')!r}. "
        f"Full response: {body}"
    )
