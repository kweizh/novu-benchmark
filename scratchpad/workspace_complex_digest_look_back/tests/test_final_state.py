import os
import subprocess
import pytest
import json

PROJECT_DIR = "/home/user/app"

def test_project_builds():
    """Priority 1: Verify the project builds successfully."""
    # We run npm run build to ensure there are no TS errors and Next.js can compile it
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Next.js build failed: {result.stderr}\n{result.stdout}"

def test_api_route_exists():
    """Priority 3: Verify the API route file exists."""
    route_path = os.path.join(PROJECT_DIR, "app/api/novu/route.ts")
    assert os.path.isfile(route_path), f"API route not found at {route_path}"
    with open(route_path, "r") as f:
        content = f.read()
        assert "GET" in content, "GET handler not exported in route.ts"
        assert "POST" in content, "POST handler not exported in route.ts"
        assert "OPTIONS" in content, "OPTIONS handler not exported in route.ts"

def test_workflows_defined():
    """Priority 3: Verify the workflows are defined with the correct steps and configuration."""
    workflows_path = os.path.join(PROJECT_DIR, "app/novu/workflows.ts")
    assert os.path.isfile(workflows_path), f"Workflows file not found at {workflows_path}"
    
    with open(workflows_path, "r") as f:
        content = f.read()
        
        # Check first workflow
        assert "customer-requests-digest-workflow" in content, "customer-requests-digest-workflow not found"
        assert "digest-recent-requests" in content, "digest-recent-requests step not found"
        assert "5" in content and "minutes" in content, "5 minutes digest not found in first workflow"
        assert "in-app-summary" in content, "in-app-summary step not found"
        assert "New requests" in content, "In-App subject 'New requests' not found"
        assert "trigger-summary-workflow" in content, "trigger-summary-workflow custom step not found"
        
        # Check second workflow
        assert "llm-request-summary-workflow" in content, "llm-request-summary-workflow not found"
        assert "digest-llm-summary" in content, "digest-llm-summary step not found"
        assert "1" in content and "hours" in content, "1 hours digest not found in second workflow"
        assert "send-llm-summary" in content, "send-llm-summary email step not found"
        assert "LLM Feedback Digest" in content, "Email subject 'LLM Feedback Digest' not found"
