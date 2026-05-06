import os
import subprocess
import time
import socket
import json
import pytest

PROJECT_DIR = "/home/user/novu-app"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(5)
    return False

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
    if not wait_for_port(3000):
        # Kill the process group before failing
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on port 3000.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=30)

def test_project_exists():
    assert os.path.isdir(PROJECT_DIR), f"Next.js project directory not found at {PROJECT_DIR}"

def test_dependencies_installed():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), "package.json not found"
    
    with open(package_json_path, 'r') as f:
        package_data = json.load(f)
        
    dependencies = package_data.get("dependencies", {})
    assert "@novu/framework" in dependencies, "@novu/framework is not installed in dependencies"
    assert "zod" in dependencies, "zod is not installed in dependencies"

def test_workflow_file_exports_sms_alert():
    workflows_path = os.path.join(PROJECT_DIR, "app/api/novu/workflows.ts")
    assert os.path.isfile(workflows_path), f"Workflow file not found at {workflows_path}"
    
    with open(workflows_path, 'r') as f:
        content = f.read()
    
    assert "smsAlert" in content, "Workflow file does not export 'smsAlert'"
    assert "step.sms" in content, "Workflow file does not use 'step.sms'"

def test_route_file_exports_handlers():
    route_path = os.path.join(PROJECT_DIR, "app/api/novu/route.ts")
    assert os.path.isfile(route_path), f"Route file not found at {route_path}"
    
    with open(route_path, 'r') as f:
        content = f.read()
    
    assert "GET" in content, "Route file does not export GET handler"
    assert "POST" in content, "Route file does not export POST handler"
    assert "OPTIONS" in content, "Route file does not export OPTIONS handler"

def test_bridge_endpoint_responding(start_app):
    result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:3000/api/novu"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"curl request failed: {result.stderr}"
    # Next.js might return 200 or 405 or 400 depending on the endpoint configuration, 
    # but it should respond and not be 404.
    http_code = result.stdout.strip()
    assert http_code != "404", "Bridge endpoint returned 404, expected it to be registered."
    assert http_code != "000", "Could not connect to the bridge endpoint."
