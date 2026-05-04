import os
import subprocess
import time
import socket
import pytest
import urllib.request
import json

PROJECT_DIR = "/home/user/novu-app"
INDEX_FILE = os.path.join(PROJECT_DIR, "index.js")

def wait_for_port(port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(2)
    return False

@pytest.fixture(scope="module")
def start_app():
    # Start the app
    process = subprocess.Popen(
        ["node", "index.js"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for the app to be ready
    if not wait_for_port(3000):
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on port 3000.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_index_file_exists():
    assert os.path.isfile(INDEX_FILE), f"index.js not found at {INDEX_FILE}"

def test_index_file_contains_steps():
    with open(INDEX_FILE, "r") as f:
        content = f.read()
    
    assert "notify-in-app" in content, "Expected 'notify-in-app' step in index.js."
    assert "send-email" in content, "Expected 'send-email' step in index.js."

def test_api_endpoint_response(start_app):
    try:
        req = urllib.request.Request("http://localhost:3000/api/novu")
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected status 200, got {response.status}"
            data = json.loads(response.read().decode())
            # The bridge endpoint GET request usually returns a list of workflows or framework info
            # We check if 'welcome-user' is in the stringified response
            data_str = json.dumps(data)
            assert "welcome-user" in data_str, f"Expected 'welcome-user' in API response, got {data_str}"
    except Exception as e:
        pytest.fail(f"Failed to fetch /api/novu: {e}")
