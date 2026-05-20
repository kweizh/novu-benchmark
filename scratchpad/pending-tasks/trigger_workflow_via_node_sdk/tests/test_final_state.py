import json
import os
import socket
import subprocess
import textwrap

import pytest
import requests
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/app"
RESULT_FILE = os.path.join(PROJECT_DIR, "result.json")
TRIGGER_SCRIPT = os.path.join(PROJECT_DIR, "trigger.js")
PACKAGE_JSON = os.path.join(PROJECT_DIR, "package.json")
NOVU_NODE_MODULE = os.path.join(PROJECT_DIR, "node_modules", "@novu", "api", "package.json")

MOCK_HOST = "127.0.0.1"
MOCK_PORT = 8000
MOCK_BASE_URL = f"http://{MOCK_HOST}:{MOCK_PORT}"
MOCK_SCRIPT_PATH = "/tmp/mock_novu_server.py"

MOCK_SERVER_SOURCE = textwrap.dedent(
    """
    import json
    import os
    import sys
    from http.server import BaseHTTPRequestHandler, HTTPServer

    HOST = "127.0.0.1"
    PORT = 8000
    LOG_PATH = "/tmp/mock_novu_requests.log"

    # Reset the request log on startup so each test sees a clean slate.
    try:
        if os.path.exists(LOG_PATH):
            os.remove(LOG_PATH)
    except OSError:
        pass


    class Handler(BaseHTTPRequestHandler):
        def _record(self, body_text):
            try:
                with open(LOG_PATH, "a", encoding="utf-8") as fh:
                    fh.write(
                        json.dumps(
                            {
                                "method": self.command,
                                "path": self.path,
                                "body": body_text,
                            }
                        )
                        + "\\n"
                    )
            except OSError:
                pass

        def do_POST(self):
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length) if length else b""
            try:
                body_text = raw.decode("utf-8")
            except UnicodeDecodeError:
                body_text = ""
            self._record(body_text)

            payload = {
                "acknowledged": True,
                "status": "processed",
                "transactionId": "mock-tx-123",
            }
            response = json.dumps(payload).encode("utf-8")
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def do_GET(self):
            # Lightweight readiness endpoint for the verifier.
            self._record("")
            response = b'{"ok":true}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def log_message(self, format, *args):  # noqa: A002 - signature required by base class
            sys.stderr.write("mock-novu " + (format % args) + "\\n")


    if __name__ == "__main__":
        server = HTTPServer((HOST, PORT), Handler)
        print(f"mock-novu listening on {HOST}:{PORT}", flush=True)
        server.serve_forever()
    """
).strip()


def _wait_for_port(host, port, timeout=30.0):
    import time

    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1.0)
            if sock.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.25)
    return False


@pytest.fixture(scope="session", autouse=True)
def mock_novu_server(xprocess):
    with open(MOCK_SCRIPT_PATH, "w", encoding="utf-8") as fh:
        fh.write(MOCK_SERVER_SOURCE)

    class Starter(ProcessStarter):
        name = "mock_novu_server"
        args = ["python3", MOCK_SCRIPT_PATH]
        timeout = 30
        terminate_on_interrupt = True
        max_read_lines = 200
        pattern = "mock-novu listening"

        def startup_check(self):  # type: ignore[override]
            return _wait_for_port(MOCK_HOST, MOCK_PORT, timeout=1.0)

    xprocess.ensure(Starter.name, Starter)
    # Double-check the port is responsive before yielding.
    assert _wait_for_port(MOCK_HOST, MOCK_PORT, timeout=15.0), (
        f"Mock Novu server did not become ready on {MOCK_BASE_URL}."
    )

    yield MOCK_BASE_URL

    info = xprocess.getinfo(Starter.name)
    info.terminate()


def test_package_json_lists_novu_api():
    assert os.path.isfile(PACKAGE_JSON), f"{PACKAGE_JSON} does not exist."
    with open(PACKAGE_JSON, "r", encoding="utf-8") as fh:
        pkg = json.load(fh)
    deps = {}
    for key in ("dependencies", "devDependencies"):
        if isinstance(pkg.get(key), dict):
            deps.update(pkg[key])
    assert "@novu/api" in pkg.get("dependencies", {}), (
        "Expected '@novu/api' to be declared under 'dependencies' in "
        f"{PACKAGE_JSON}; got dependencies={pkg.get('dependencies')!r}."
    )


def test_novu_api_module_installed():
    assert os.path.isfile(NOVU_NODE_MODULE), (
        f"Expected the '@novu/api' SDK to be installed at {NOVU_NODE_MODULE}; "
        "did the agent run 'npm install'?"
    )


def test_trigger_script_exists():
    assert os.path.isfile(TRIGGER_SCRIPT), f"{TRIGGER_SCRIPT} does not exist."


def test_trigger_script_runs_and_writes_result(mock_novu_server):
    # Ensure no stale result.json from a previous attempt.
    if os.path.exists(RESULT_FILE):
        os.remove(RESULT_FILE)

    # Reset the mock server's request log via the helper file used by the mock.
    request_log = "/tmp/mock_novu_requests.log"
    if os.path.exists(request_log):
        os.remove(request_log)

    env = os.environ.copy()
    env["NOVU_SECRET_KEY"] = "test-secret-key"
    env["NOVU_API_BASE_URL"] = mock_novu_server

    proc = subprocess.run(
        ["node", "trigger.js"],
        cwd=PROJECT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        "node trigger.js failed.\n"
        f"stdout:\n{proc.stdout}\n"
        f"stderr:\n{proc.stderr}"
    )

    assert os.path.isfile(RESULT_FILE), (
        f"Expected {RESULT_FILE} to be written by trigger.js.\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )


def test_mock_server_received_trigger_request():
    request_log = "/tmp/mock_novu_requests.log"
    assert os.path.isfile(request_log), (
        "Mock server did not record any requests; trigger.js may not be "
        f"directing traffic to {MOCK_BASE_URL}."
    )
    matched = False
    with open(request_log, "r", encoding="utf-8") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("method") == "POST" and "/v1/events/trigger" in entry.get("path", ""):
                matched = True
                break
    assert matched, (
        "Mock server received no POST to a path containing '/v1/events/trigger'. "
        "Confirm that the script uses NOVU_API_BASE_URL as the SDK server URL."
    )


def test_result_json_has_expected_fields():
    with open(RESULT_FILE, "r", encoding="utf-8") as fh:
        result = json.load(fh)

    assert isinstance(result, dict), (
        f"Expected {RESULT_FILE} to contain a JSON object, got {type(result).__name__}."
    )
    assert result.get("acknowledged") is True, (
        f"Expected result.acknowledged === true, got {result.get('acknowledged')!r}."
    )
    assert result.get("transactionId") == "mock-tx-123", (
        f"Expected result.transactionId === 'mock-tx-123', got {result.get('transactionId')!r}."
    )
    if "status" in result:
        assert result["status"] == "processed", (
            f"Expected result.status === 'processed' when present, got {result['status']!r}."
        )


def test_mock_server_is_reachable_directly(mock_novu_server):
    # Smoke check the mock server itself so failures elsewhere are easier to diagnose.
    response = requests.post(
        f"{mock_novu_server}/v1/events/trigger",
        json={"smoke": "test"},
        timeout=5,
    )
    assert response.status_code == 201, (
        f"Mock server returned unexpected status: {response.status_code}"
    )
    body = response.json()
    assert body.get("transactionId") == "mock-tx-123", (
        f"Mock server returned unexpected body: {body!r}"
    )
