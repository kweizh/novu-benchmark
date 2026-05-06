import os
import subprocess
import time
import socket
import pytest
import urllib.request

PROJECT_DIR = "/home/user/novu-project"
WORKFLOW_FILE = os.path.join(PROJECT_DIR, "workflow.ts")
INDEX_FILE = os.path.join(PROJECT_DIR, "index.ts")

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
    env = os.environ.copy()
    env["NOVU_SECRET_KEY"] = "dummy"
    
    process = subprocess.Popen(
        ["npx", "tsx", "index.ts"],
        cwd=PROJECT_DIR,
        env=env,
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

def test_bridge_endpoint(start_app):
    """Priority 3: Check bridge endpoint is accessible."""
    try:
        req = urllib.request.Request("http://localhost:3000/api/novu")
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected status 200, got {response.status}"
    except Exception as e:
        pytest.fail(f"Failed to reach bridge endpoint: {e}")

def test_workflow_file_exists():
    """Priority 3: Check workflow.ts exists."""
    assert os.path.isfile(WORKFLOW_FILE), f"workflow.ts not found at {WORKFLOW_FILE}"

def test_index_file_exists():
    """Priority 3: Check index.ts exists."""
    assert os.path.isfile(INDEX_FILE), f"index.ts not found at {INDEX_FILE}"

def test_workflow_definition():
    """Priority 3: Check workflow definition."""
    with open(WORKFLOW_FILE, "r") as f:
        content = f.read()
        
    assert "dynamic-email" in content, "Expected 'dynamic-email' workflow name in workflow.ts"
    assert "orderId" in content, "Expected 'orderId' in workflow.ts"
    assert "customerName" in content, "Expected 'customerName' in workflow.ts"
    assert "z.object" in content or "zod.object" in content, "Expected Zod schema in workflow.ts"
    
    # Check dynamic subject
    assert "payload.orderId" in content, "Expected payload.orderId to be used in subject"
    assert "payload.customerName" in content, "Expected payload.customerName to be used in subject"
    assert "Order" in content and "confirmed for" in content, "Expected the subject format 'Order <orderId> confirmed for <customerName>'"
