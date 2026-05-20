import base64
import os
import socket

import pytest
import requests
from xprocess import ProcessStarter


PROJECT_DIR = "/home/user/app"
BASE_URL = "http://localhost:3000"
NOVU_ROUTE = "/api/novu"


@pytest.fixture(scope="session")
def start_app(xprocess):
    class Starter(ProcessStarter):
        name = "novu_email_attachments_app"
        args = ["node", "index.js"]
        env = os.environ.copy()
        env["NOVU_STRICT_AUTHENTICATION_ENABLED"] = "false"
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


def test_discover_returns_invoice_email_workflow(start_app):
    resp = requests.get(f"{BASE_URL}{NOVU_ROUTE}", params={"action": "discover"}, timeout=15)
    assert resp.status_code == 200, (
        f"GET discover returned status {resp.status_code}, body={resp.text}"
    )
    data = resp.json()
    workflows = data.get("workflows")
    assert isinstance(workflows, list) and len(workflows) >= 1, (
        f"Expected at least one workflow in discover response; got: {data}"
    )

    matched = [w for w in workflows if w.get("workflowId") == "invoice-email"]
    assert len(matched) == 1, (
        f"Expected exactly one workflow with workflowId 'invoice-email'; found: "
        f"{[w.get('workflowId') for w in workflows]}"
    )

    workflow = matched[0]
    steps = workflow.get("steps") or []
    email_steps = [
        s for s in steps
        if s.get("stepId") == "send-invoice" and s.get("type") == "email"
    ]
    assert len(email_steps) == 1, (
        f"Expected one email step with stepId 'send-invoice' on the workflow; "
        f"got steps: {steps}"
    )


def _preview_body(invoice_number: str) -> dict:
    return {
        "inputs": {},
        "controls": {},
        "data": {"invoiceNumber": invoice_number},
        "payload": {"invoiceNumber": invoice_number},
        "state": [],
        "subscriber": {},
    }


def test_preview_email_outputs_subject_body_attachment(start_app):
    params = {
        "action": "preview",
        "workflowId": "invoice-email",
        "stepId": "send-invoice",
    }
    resp = requests.post(
        f"{BASE_URL}{NOVU_ROUTE}",
        params=params,
        json=_preview_body("INV-1"),
        timeout=20,
    )
    assert resp.status_code == 200, (
        f"POST preview returned status {resp.status_code}, body={resp.text}"
    )

    data = resp.json()
    outputs = data.get("outputs")
    assert isinstance(outputs, dict), (
        f"Expected 'outputs' object in preview response; got: {data}"
    )

    assert outputs.get("subject") == "Your invoice INV-1", (
        f"Expected subject 'Your invoice INV-1', got: {outputs.get('subject')!r}"
    )
    assert outputs.get("body") == "Please find your invoice attached.", (
        f"Expected body 'Please find your invoice attached.', got: {outputs.get('body')!r}"
    )

    attachments = outputs.get("attachments")
    assert isinstance(attachments, list) and len(attachments) == 1, (
        f"Expected attachments to be a list of length 1; got: {attachments!r}"
    )

    attachment = attachments[0]
    assert attachment.get("name") == "invoice.txt", (
        f"Expected attachment name 'invoice.txt'; got: {attachment.get('name')!r}"
    )

    mime_value = attachment.get("mime") or attachment.get("contentType")
    assert mime_value == "text/plain", (
        f"Expected attachment MIME 'text/plain' (under 'mime' or 'contentType'); "
        f"got: mime={attachment.get('mime')!r}, contentType={attachment.get('contentType')!r}"
    )

    file_value = attachment.get("file")
    assert isinstance(file_value, str) and file_value, (
        f"Expected 'file' to be a non-empty base64 string; got: {file_value!r}"
    )
    try:
        decoded = base64.b64decode(file_value, validate=True).decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(
            f"Attachment 'file' was not valid base64-encoded UTF-8 text: {exc}; raw={file_value!r}"
        )
    assert decoded == "Sample invoice content", (
        f"Expected attachment file to decode to 'Sample invoice content'; got: {decoded!r}"
    )
