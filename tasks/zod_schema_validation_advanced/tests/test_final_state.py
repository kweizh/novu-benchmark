import os
import time
import requests
import subprocess
import json

def test_express_app_and_novu_endpoint():
    project_path = "/home/user/myproject"
    assert os.path.exists(project_path), f"Project directory {project_path} does not exist"
    
    # Start the server
    process = subprocess.Popen(
        ["node", "index.js"],
        cwd=project_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Wait for the server to start
        time.sleep(4)
        
        # Test the endpoint
        response = requests.get("http://localhost:3000/api/novu")
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
        
        data = response.json()
        assert "workflows" in data, "Response does not contain 'workflows'"
        
        workflows = data["workflows"]
        welcome_workflow = next((w for w in workflows if w["workflowId"] == "welcome-user"), None)
        assert welcome_workflow is not None, "Workflow 'welcome-user' not found"
        
        # Check payload schema
        payload_schema_str = json.dumps(welcome_workflow.get("payloadSchema", {}))
        assert "userName" in payload_schema_str, "Payload schema is missing 'userName'"
        assert "age" in payload_schema_str, "Payload schema is missing 'age'"
        
        # Check steps
        steps = welcome_workflow.get("steps", [])
        step_ids = [step.get("stepId") for step in steps]
        assert "notify-in-app" in step_ids, "Missing 'notify-in-app' step"
        assert "send-email" in step_ids, "Missing 'send-email' step"

    finally:
        process.terminate()
        process.wait()
