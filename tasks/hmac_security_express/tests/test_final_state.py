import os
import subprocess
import time
import socket
import json
import pytest
import urllib.request
import urllib.error

PROJECT_DIR = "/home/user/app"

def wait_for_port(port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

@pytest.fixture(scope="module")
def start_app():
    env = os.environ.copy()
    env["NOVU_SECRET_KEY"] = "test_secret_123"
    
    process = subprocess.Popen(
        ["npm", "start"],
        cwd=PROJECT_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    if not wait_for_port(3000):
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on port 3000.")

    yield

    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_endpoint_mounted(start_app):
    """Priority 3: Send a GET request to verify the endpoint is mounted."""
    try:
        req = urllib.request.Request("http://localhost:3000/api/novu")
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected 200 OK from GET /api/novu, got {response.status}"
    except urllib.error.HTTPError as e:
        pytest.fail(f"GET /api/novu returned HTTPError: {e.code}")
    except Exception as e:
        pytest.fail(f"Failed to connect to /api/novu: {e}")

def test_hmac_verification_enforced(start_app):
    """Priority 3: Send a POST request without HMAC signature to verify it is rejected."""
    data = json.dumps({
        "name": "test-workflow",
        "to": "subscriber-id",
        "payload": {}
    }).encode('utf-8')
    
    req = urllib.request.Request(
        "http://localhost:3000/api/novu",
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            pytest.fail("Expected POST /api/novu without signature to be rejected, but it succeeded.")
    except urllib.error.HTTPError as e:
        assert e.code in [400, 401, 403], f"Expected 400/401/403 rejection from POST /api/novu without signature, got {e.code}"
    except Exception as e:
        pytest.fail(f"Failed to connect to /api/novu: {e}")
