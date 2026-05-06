import subprocess
import time
import json
import urllib.request
import urllib.error

def test_bridge_endpoint():
    # Attempt to fetch the discover endpoint
    max_retries = 30
    discovered = None
    for _ in range(max_retries):
        try:
            req = urllib.request.Request("http://localhost:3000/api/novu?action=discover")
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    discovered = json.loads(data)
                    break
        except urllib.error.URLError:
            time.sleep(1)
    
    assert discovered is not None, "Failed to reach the Novu bridge endpoint at /api/novu?action=discover"
    
    workflows = discovered.get("workflows", [])
    assert len(workflows) > 0, "No workflows discovered"
    
    pref_workflow = next((w for w in workflows if w.get("workflowId") == "subscriber-preferences"), None)
    assert pref_workflow is not None, "Workflow 'subscriber-preferences' not found"
    
    # Check preferences
    prefs = pref_workflow.get("preferences", {})
    assert prefs, "Preferences not found on the workflow"
    
    channels = prefs.get("channels", {})
    all_prefs = prefs.get("all", {})
    
    assert channels.get("inApp", {}).get("enabled") is True, "inApp channel should be enabled"
    assert channels.get("email", {}).get("enabled") is False, "email channel should be disabled"
    assert all_prefs.get("readOnly") is False, "preferences should not be readOnly"
    
    # Check steps
    steps = pref_workflow.get("steps", [])
    step_types = [step.get("type") for step in steps]
    
    assert "inApp" in step_types, "Missing inApp step"
    assert "email" in step_types, "Missing email step"
