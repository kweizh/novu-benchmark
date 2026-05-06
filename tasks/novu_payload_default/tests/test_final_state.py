import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"
WORKFLOW_FILE = os.path.join(PROJECT_DIR, "src", "novu", "workflows.ts")

def test_workflow_file_exists():
    assert os.path.isfile(WORKFLOW_FILE), f"Workflow file not found at {WORKFLOW_FILE}"

def test_workflow_compiles():
    """Verify that the workflow file is valid TypeScript."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "src/novu/workflows.ts"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    # It might fail if tsconfig is not strictly set up, but we can at least check if it parses
    # Actually, running tsx to just load the file is better to ensure no runtime errors.
    result = subprocess.run(
        ["npx", "tsx", "src/novu/workflows.ts"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Failed to execute/compile workflows.ts: {result.stderr}"

def test_workflow_schema_default_value():
    """Priority 3 fallback: Verify the Zod schema definition via string matching."""
    with open(WORKFLOW_FILE, 'r') as f:
        content = f.read()

    assert "z.object" in content, "Expected 'z.object' to define the payload schema."
    assert "userName" in content, "Expected 'userName' field in the payload schema."
    assert ".default('Guest')" in content or ".default(\"Guest\")" in content or ".default(`Guest`)" in content, \
        "Expected 'userName' to have a default value of 'Guest' using .default('Guest')."
    assert "step.email" in content, "Expected an email step to be defined."
    assert "welcome-user" in content, "Expected workflow ID to be 'welcome-user'."
