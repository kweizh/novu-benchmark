import json
import os
import re
import socket
import urllib.error
import urllib.request

import pytest
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/app"
ROUTE_FILE = os.path.join(PROJECT_DIR, "app", "api", "novu", "route.ts")
PACKAGE_JSON = os.path.join(PROJECT_DIR, "package.json")
PORT = 3000
DISCOVER_URL = f"http://localhost:{PORT}/api/novu?action=discover"


def _wait_for_port(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        return s.connect_ex(("localhost", port)) == 0


def _http_get_json(url: str, timeout: int = 30):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, json.loads(body)


def _http_post_json(url: str, payload: dict, timeout: int = 30):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, json.loads(body) if body else {}


@pytest.fixture(scope="session")
def start_app(xprocess):
    """Start the Next.js dev server."""

    class Starter(ProcessStarter):
        name = "nextjs_app"
        args = ["npm", "run", "dev"]
        env = os.environ.copy()
        popen_kwargs = {"cwd": PROJECT_DIR, "text": True}
        timeout = 300
        terminate_on_interrupt = True
        max_read_lines = 5000

        def startup_check(self):
            if not _wait_for_port(PORT):
                return False
            # Also ensure the route is responsive (Next.js compiles routes lazily).
            try:
                req = urllib.request.Request(DISCOVER_URL, method="GET")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    return resp.status == 200
            except Exception:
                return False

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def test_route_file_exists():
    """The Next.js App Router route file must exist at the expected path."""
    assert os.path.isfile(ROUTE_FILE), f"Route file not found at {ROUTE_FILE}"


def test_route_file_uses_novu_next_serve_and_exports_handlers():
    """The route file must import `serve` from `@novu/framework/next` and export GET/POST/OPTIONS."""
    with open(ROUTE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    assert re.search(
        r"from\s+['\"]@novu/framework/next['\"]", content
    ), "route.ts must import from '@novu/framework/next'."
    assert re.search(
        r"\bserve\b", content
    ), "route.ts must reference the `serve` helper."
    for method in ("GET", "POST", "OPTIONS"):
        assert re.search(
            rf"\b{method}\b", content
        ), f"route.ts must export an `{method}` handler."


def test_package_json_dependencies():
    """package.json must declare `next` and `@novu/framework`."""
    assert os.path.isfile(PACKAGE_JSON), f"package.json not found at {PACKAGE_JSON}"
    with open(PACKAGE_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    deps = {}
    deps.update(data.get("dependencies", {}) or {})
    deps.update(data.get("devDependencies", {}) or {})

    assert "next" in deps, "`next` is missing from package.json dependencies."
    assert "@novu/framework" in deps, (
        "`@novu/framework` is missing from package.json dependencies."
    )


def test_discover_returns_hello_world_workflow(start_app):
    """GET /api/novu?action=discover must return a workflow named 'hello-world'."""
    status, data = _http_get_json(DISCOVER_URL, timeout=60)
    assert status == 200, f"Expected 200 OK from discover, got {status}"
    assert isinstance(data, dict), f"Discover response must be a JSON object, got: {type(data)}"
    workflows = data.get("workflows")
    assert isinstance(workflows, list) and workflows, (
        f"Discover response must contain a non-empty 'workflows' array, got: {data}"
    )
    matching = [w for w in workflows if w.get("workflowId") == "hello-world"]
    assert len(matching) == 1, (
        f"Expected exactly one workflow with workflowId 'hello-world', found {len(matching)}: "
        f"{[w.get('workflowId') for w in workflows]}"
    )


def test_hello_world_has_in_app_step(start_app):
    """The 'hello-world' workflow must contain at least one in-app step."""
    _, data = _http_get_json(DISCOVER_URL, timeout=60)
    workflows = data.get("workflows", [])
    workflow = next((w for w in workflows if w.get("workflowId") == "hello-world"), None)
    assert workflow is not None, "Workflow 'hello-world' not found in discover response."
    steps = workflow.get("steps") or []
    assert isinstance(steps, list) and steps, (
        f"'hello-world' must have a non-empty 'steps' array, got: {workflow}"
    )
    in_app_steps = [s for s in steps if s.get("type") == "in_app"]
    assert in_app_steps, (
        f"'hello-world' must contain at least one in_app step, got step types: "
        f"{[s.get('type') for s in steps]}"
    )


def test_in_app_step_body_is_hello_from_nextjs(start_app):
    """
    Verify the in-app step body is exactly 'Hello from Next.js'.

    Primary path: invoke the Novu Bridge preview action via POST. If the bridge
    surface signature differs across @novu/framework versions, fall back to
    scanning the workflow source files for the literal body string inside a
    step.inApp(...) call.
    """
    _, data = _http_get_json(DISCOVER_URL, timeout=60)
    workflow = next(
        (w for w in data.get("workflows", []) if w.get("workflowId") == "hello-world"),
        None,
    )
    assert workflow is not None, "Workflow 'hello-world' not found."
    in_app_steps = [s for s in (workflow.get("steps") or []) if s.get("type") == "in_app"]
    assert in_app_steps, "No in_app step on 'hello-world'."
    step_id = in_app_steps[0].get("stepId")
    assert step_id, f"In-app step is missing stepId: {in_app_steps[0]}"

    body_value = None

    # Primary verification: query the Bridge preview action.
    preview_url = (
        f"http://localhost:{PORT}/api/novu?action=preview"
        f"&workflowId=hello-world&stepId={step_id}"
    )
    preview_payload = {
        "data": {},
        "controls": {},
        "payload": {},
        "subscriber": {"subscriberId": "test-subscriber"},
        "state": [],
    }
    try:
        _, preview = _http_post_json(preview_url, preview_payload, timeout=60)
        # Navigate common shapes for the preview response.
        candidates = []
        if isinstance(preview, dict):
            candidates.append(preview.get("outputs"))
            candidates.append(preview.get("output"))
            candidates.append(preview.get("body"))
            if isinstance(preview.get("outputs"), dict):
                candidates.append(preview["outputs"].get("body"))
            if isinstance(preview.get("result"), dict):
                candidates.append(preview["result"].get("outputs"))
        for candidate in candidates:
            if isinstance(candidate, str) and candidate == "Hello from Next.js":
                body_value = candidate
                break
            if isinstance(candidate, dict) and candidate.get("body") == "Hello from Next.js":
                body_value = candidate["body"]
                break
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        body_value = None

    if body_value == "Hello from Next.js":
        return

    # Fallback: scan workflow source for the literal in-app body string.
    found = False
    for root, _dirs, files in os.walk(PROJECT_DIR):
        # Skip dependency and build directories for speed.
        if any(skip in root for skip in (os.sep + "node_modules", os.sep + ".next")):
            continue
        for name in files:
            if not name.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")):
                continue
            path = os.path.join(root, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    src = f.read()
            except (OSError, UnicodeDecodeError):
                continue
            if "step.inApp" in src and "Hello from Next.js" in src:
                found = True
                break
        if found:
            break

    assert found, (
        "Could not verify in-app body. Expected the literal string "
        "'Hello from Next.js' inside a step.inApp(...) call in a project source file, "
        "or in the bridge preview output."
    )
