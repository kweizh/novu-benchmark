import json
import os
import socket
import subprocess

import pytest
import requests
from xprocess import ProcessStarter


PROJECT_DIR = "/home/user/app"
BASE_URL = "http://127.0.0.1:3000"
BRIDGE_PATH = "/api/novu"


@pytest.fixture(scope="session")
def start_app(xprocess):
    """Start the Hono server with the Novu Bridge Endpoint and wait for readiness."""

    # Make sure dependencies are installed before launching.
    if not os.path.isdir(os.path.join(PROJECT_DIR, "node_modules")):
        subprocess.run(
            ["npm", "install"],
            cwd=PROJECT_DIR,
            check=True,
            capture_output=True,
            text=True,
        )

    class Starter(ProcessStarter):
        name = "novu_hono_app"
        args = ["npm", "start"]
        env = os.environ.copy()
        popen_kwargs = {
            "cwd": PROJECT_DIR,
            "text": True,
        }
        timeout = 180
        terminate_on_interrupt = True

        def startup_check(self):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("127.0.0.1", 3000)) != 0:
                    return False
            try:
                response = requests.get(BASE_URL + BRIDGE_PATH, timeout=2)
            except requests.RequestException:
                return False
            return response.status_code == 200

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _find_workflow(payload, workflow_id):
    """Search a deeply nested JSON structure for a workflow with the given id."""
    candidates = []

    def walk(node):
        if isinstance(node, dict):
            # A workflow-like object typically has a workflow id and a list of steps.
            possible_id = (
                node.get("workflowId")
                or node.get("id")
                or node.get("name")
            )
            steps = node.get("steps")
            if possible_id == workflow_id and isinstance(steps, list):
                candidates.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return candidates[0] if candidates else None


def _find_step(workflow_obj, step_id):
    steps = workflow_obj.get("steps") or []
    for step in steps:
        if not isinstance(step, dict):
            continue
        candidate_id = step.get("stepId") or step.get("id") or step.get("name")
        if candidate_id == step_id:
            return step
    return None


def test_package_json_lists_required_dependencies():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), (
        f"Expected {package_json_path} to exist."
    )
    with open(package_json_path) as f:
        pkg = json.load(f)
    deps = {}
    deps.update(pkg.get("dependencies") or {})
    deps.update(pkg.get("devDependencies") or {})
    for name in ("hono", "@hono/node-server", "@novu/framework"):
        assert name in deps, (
            f"Expected '{name}' to be declared as a dependency in {package_json_path}, "
            f"found dependencies: {sorted(deps.keys())}"
        )


def test_node_modules_contain_real_packages():
    for name in ("hono", "@hono/node-server", "@novu/framework"):
        path = os.path.join(PROJECT_DIR, "node_modules", *name.split("/"))
        assert os.path.isdir(path), (
            f"Expected the real package '{name}' to be installed at {path}."
        )


def test_bridge_discover_endpoint_returns_workflow(start_app):
    response = requests.get(BASE_URL + BRIDGE_PATH, timeout=10)
    assert response.status_code == 200, (
        f"GET {BRIDGE_PATH} returned status {response.status_code}, "
        f"body: {response.text[:500]}"
    )
    try:
        payload = response.json()
    except ValueError as exc:
        pytest.fail(
            f"GET {BRIDGE_PATH} did not return JSON: {exc}; "
            f"body: {response.text[:500]}"
        )

    workflow = _find_workflow(payload, "greet-hono")
    assert workflow is not None, (
        "Expected the discover response to contain a workflow with id 'greet-hono'. "
        f"Got payload keys: {list(payload.keys()) if isinstance(payload, dict) else type(payload).__name__}"
    )

    step = _find_step(workflow, "welcome-email")
    assert step is not None, (
        "Expected workflow 'greet-hono' to include a step with id 'welcome-email'. "
        f"Got steps: {workflow.get('steps')}"
    )

    step_type = (
        step.get("type")
        or step.get("channel")
        or step.get("template", {}).get("type")
        or step.get("stepType")
    )
    assert step_type == "email", (
        f"Expected step 'welcome-email' to be an email step, got type/channel={step_type!r}. "
        f"Step payload: {step}"
    )


def _extract_outputs(payload):
    """Find a dict containing both 'subject' and 'body' keys in a nested payload."""
    if isinstance(payload, dict):
        if "subject" in payload and "body" in payload:
            return payload
        for value in payload.values():
            found = _extract_outputs(value)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for item in payload:
            found = _extract_outputs(item)
            if found is not None:
                return found
    return None


def test_bridge_execute_endpoint_returns_email_content(start_app):
    body = {
        "action": "execute",
        "workflowId": "greet-hono",
        "stepId": "welcome-email",
        "subscriber": {"subscriberId": "verify-user"},
        "payload": {},
        "controls": {},
        "state": [],
        "inputs": {},
    }

    response = requests.post(
        BASE_URL + BRIDGE_PATH + "?action=execute",
        json=body,
        timeout=15,
    )
    assert response.status_code == 200, (
        f"POST {BRIDGE_PATH} returned status {response.status_code}, "
        f"body: {response.text[:500]}"
    )

    try:
        payload = response.json()
    except ValueError as exc:
        pytest.fail(
            f"POST {BRIDGE_PATH} did not return JSON: {exc}; "
            f"body: {response.text[:500]}"
        )

    outputs = _extract_outputs(payload)
    assert outputs is not None, (
        "Expected execute response to contain an object with 'subject' and 'body'. "
        f"Got payload: {json.dumps(payload)[:500]}"
    )
    assert outputs.get("subject") == "Welcome via Hono", (
        f"Expected subject 'Welcome via Hono', got {outputs.get('subject')!r}"
    )
    assert outputs.get("body") == "Greetings from a Hono-powered Novu app.", (
        f"Expected body 'Greetings from a Hono-powered Novu app.', got {outputs.get('body')!r}"
    )
