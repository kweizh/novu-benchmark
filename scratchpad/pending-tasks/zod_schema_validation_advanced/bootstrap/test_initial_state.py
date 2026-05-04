import os

def test_initial_state():
    # The project directory should not exist or should be empty
    project_path = "/home/user/myproject"
    if os.path.exists(project_path):
        assert len(os.listdir(project_path)) == 0, f"Directory {project_path} is not empty"
    else:
        assert True
