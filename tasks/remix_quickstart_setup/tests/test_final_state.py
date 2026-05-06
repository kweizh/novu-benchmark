import os
import subprocess
import time
import socket
import pytest
import urllib.request
import urllib.error

PROJECT_DIR = "/home/user/my-novu-app"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(5)
    return False

def test_package_json_has_novu():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    with open(package_json_path) as f:
        content = f.read()
    assert "@novu/framework" in content, "Expected @novu/framework to be installed in package.json."

def test_workflows_file_exists():
    workflows_path = os.path.join(PROJECT_DIR, "app/novu/workflows.ts")
    assert os.path.isfile(workflows_path), f"Workflows file {workflows_path} does not exist."
    with open(workflows_path) as f:
        content = f.read()
    assert "workflow(" in content, "Expected workflow definition in app/novu/workflows.ts."

def test_api_route_exists():
    api_route_path = os.path.join(PROJECT_DIR, "app/routes/api.novu.ts")
    assert os.path.isfile(api_route_path), f"API route file {api_route_path} does not exist."
    with open(api_route_path) as f:
        content = f.read()
    assert "action" in content and "loader" in content, \
        "Expected action and loader to be exported from app/routes/api.novu.ts."
    assert "@novu/framework/remix" in content, \
        "Expected @novu/framework/remix to be imported in app/routes/api.novu.ts."

def test_env_file_exists():
    env_path = os.path.join(PROJECT_DIR, ".env")
    assert os.path.isfile(env_path), f".env file {env_path} does not exist."
    with open(env_path) as f:
        content = f.read()
    assert "NOVU_SECRET_KEY=" in content, "Expected NOVU_SECRET_KEY in .env file."

@pytest.fixture(scope="module")
def start_app():
    # Start the app
    process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for the app to be ready
    if not wait_for_port(5173):
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on port 5173.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=30)

def test_api_endpoint_reachable(start_app):
    try:
        req = urllib.request.Request("http://localhost:5173/api/novu", method="GET")
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected 200 OK, got {response.status}"
    except urllib.error.HTTPError as e:
        # A 400 Bad Request or 405 Method Not Allowed could be returned by Novu framework,
        # but it shouldn't be a 404 Not Found.
        assert e.code != 404, "Endpoint /api/novu returned 404 Not Found, indicating route is not mounted."
    except urllib.error.URLError as e:
        pytest.fail(f"Failed to reach /api/novu endpoint: {e.reason}")
