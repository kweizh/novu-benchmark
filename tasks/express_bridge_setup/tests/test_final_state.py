import os
import subprocess
import time
import socket
import pytest
import json
import urllib.request

PROJECT_DIR = "/home/user/myproject"

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

def test_dependencies_installed():
    """Priority 3: Check package.json for required dependencies."""
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), f"package.json not found at {package_json_path}"
    
    with open(package_json_path) as f:
        data = json.load(f)
        
    deps = data.get("dependencies", {})
    assert "express" in deps, "express not found in package.json dependencies."
    assert "@novu/framework" in deps, "@novu/framework not found in package.json dependencies."

def test_bridge_endpoint_discovery(start_app):
    """Priority 1: Verify the endpoint is live and returns the workflow discovery payload."""
    url = "http://localhost:3000/api/novu?action=discover"
    
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected 200 OK, got {response.status}"
            body = response.read().decode('utf-8')
            data = json.loads(body)
            
            # The structure returned by discover action typically includes a 'workflows' array
            assert "workflows" in data, "Response JSON does not contain 'workflows' key."
            
            # Find the test-workflow
            workflows = data["workflows"]
            workflow_names = [wf.get("workflowId") for wf in workflows]
            assert "test-workflow" in workflow_names, f"Expected 'test-workflow' in discovered workflows, got: {workflow_names}"
            
    except urllib.error.URLError as e:
        pytest.fail(f"Failed to fetch {url}: {e}")
