import json
import os
import socket
import subprocess

import pytest
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/app"
BRIDGE_URL = "http://localhost:3000/api/novu"


def _port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="session", autouse=True)
def start_bridge(xprocess):
    """Start the Novu bridge Express server before running tests."""
    # Ensure dependencies are installed.
    if not os.path.isdir(os.path.join(PROJECT_DIR, "node_modules")):
        subprocess.run(
            ["npm", "install"],
            cwd=PROJECT_DIR,
            check=True,
        )

    env = os.environ.copy()
    env["NOVU_STRICT_AUTHENTICATION_ENABLED"] = "false"

    class Starter(ProcessStarter):
        name = "novu_bridge"
        args = ["node", "index.js"]
        # xprocess will look for a server listening on the port.
        popen_kwargs = {"cwd": PROJECT_DIR, "text": True}
        timeout = 60
        terminate_on_interrupt = True
        env = env

        def startup_check(self):
            return _port_open("localhost", 3000)

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _find_step(steps, step_id):
    for s in steps:
        sid = s.get("stepId") or s.get("name") or s.get("id")
        if sid == step_id:
            return s
    return None


def test_discover_workflow_and_steps():
    resp = requests.get(BRIDGE_URL, params={"action": "discover"}, timeout=10)
    assert resp.status_code == 200, (
        f"Expected 200 from /api/novu?action=discover, got {resp.status_code}: {resp.text}"
    )
    data = resp.json()
    workflows = data.get("workflows") or data.get("data", {}).get("workflows")
    assert workflows is not None, f"No 'workflows' field in discover response: {data}"
    assert len(workflows) == 1, (
        f"Expected exactly 1 workflow, got {len(workflows)}: {[w.get('workflowId') for w in workflows]}"
    )
    wf = workflows[0]
    wf_id = wf.get("workflowId") or wf.get("name") or wf.get("id")
    assert wf_id == "reminder-flow", f"Expected workflowId 'reminder-flow', got {wf_id!r}."

    steps = wf.get("steps") or []
    assert len(steps) == 2, f"Expected exactly 2 steps, got {len(steps)}: {steps}"

    delay_step = steps[0]
    delay_id = delay_step.get("stepId") or delay_step.get("name") or delay_step.get("id")
    delay_type = delay_step.get("type") or delay_step.get("template", {}).get("type")
    assert delay_id == "wait-an-hour", (
        f"Expected first step id 'wait-an-hour', got {delay_id!r}."
    )
    assert delay_type == "delay", (
        f"Expected first step type 'delay', got {delay_type!r}."
    )

    email_step = steps[1]
    email_id = email_step.get("stepId") or email_step.get("name") or email_step.get("id")
    email_type = email_step.get("type") or email_step.get("template", {}).get("type")
    assert email_id == "reminder-email", (
        f"Expected second step id 'reminder-email', got {email_id!r}."
    )
    assert email_type == "email", (
        f"Expected second step type 'email', got {email_type!r}."
    )


def _preview(step_id: str):
    body = {
        "payload": {"userName": "Alice"},
        "controls": {},
        "data": {"userName": "Alice"},
        "inputs": {},
        "state": [],
        "subscriber": {},
        "steps": {},
    }
    resp = requests.post(
        BRIDGE_URL,
        params={
            "action": "preview",
            "workflowId": "reminder-flow",
            "stepId": step_id,
        },
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    assert resp.status_code == 200, (
        f"Expected 200 from preview of {step_id}, got {resp.status_code}: {resp.text}"
    )
    return resp.json()


def test_preview_delay_step_outputs():
    data = _preview("wait-an-hour")
    outputs = data.get("outputs") or data.get("output") or {}
    assert outputs.get("type") == "regular", (
        f"Expected delay type 'regular', got {outputs.get('type')!r} (full response: {json.dumps(data)[:500]})"
    )
    assert outputs.get("amount") == 1, (
        f"Expected delay amount 1, got {outputs.get('amount')!r}."
    )
    assert outputs.get("unit") == "hours", (
        f"Expected delay unit 'hours', got {outputs.get('unit')!r}."
    )


def test_preview_email_step_outputs():
    data = _preview("reminder-email")
    outputs = data.get("outputs") or data.get("output") or {}
    assert outputs.get("subject") == "Reminder: don't forget!", (
        f"Expected subject 'Reminder: don't forget!', got {outputs.get('subject')!r}."
    )
    assert outputs.get("body") == "It's been an hour, here's your reminder.", (
        f"Expected body 'It's been an hour, here's your reminder.', got {outputs.get('body')!r}."
    )
