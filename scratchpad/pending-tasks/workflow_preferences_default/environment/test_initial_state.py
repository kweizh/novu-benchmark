import os
import shutil
import subprocess


PROJECT_DIR = "/home/user/app"


def test_node_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."


def test_npm_available():
    assert shutil.which("npm") is not None, "npm binary not found in PATH."


def test_node_version_at_least_20():
    result = subprocess.run(
        ["node", "--version"], capture_output=True, text=True, check=True
    )
    version = result.stdout.strip().lstrip("v")
    major = int(version.split(".")[0])
    assert major >= 20, f"Expected Node.js >= 20, got {version}."


def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_strict_authentication_env_disabled():
    value = os.environ.get("NOVU_STRICT_AUTHENTICATION_ENABLED")
    assert value == "false", (
        "Expected NOVU_STRICT_AUTHENTICATION_ENABLED=false in the environment, "
        f"got {value!r}."
    )


def test_novu_framework_installed_globally_or_locally():
    # @novu/framework must be available either globally or already cached
    # under a known node_modules so that `node index.js` can require it.
    candidate_dirs = [
        "/usr/lib/node_modules/@novu/framework",
        "/usr/local/lib/node_modules/@novu/framework",
        os.path.join(PROJECT_DIR, "node_modules", "@novu", "framework"),
    ]
    assert any(os.path.isdir(p) for p in candidate_dirs), (
        "@novu/framework is not installed in any of the expected locations: "
        f"{candidate_dirs}"
    )


def test_express_available():
    candidate_dirs = [
        "/usr/lib/node_modules/express",
        "/usr/local/lib/node_modules/express",
        os.path.join(PROJECT_DIR, "node_modules", "express"),
    ]
    assert any(os.path.isdir(p) for p in candidate_dirs), (
        "express is not installed in any of the expected locations: "
        f"{candidate_dirs}"
    )


def test_zod_available():
    candidate_dirs = [
        "/usr/lib/node_modules/zod",
        "/usr/local/lib/node_modules/zod",
        os.path.join(PROJECT_DIR, "node_modules", "zod"),
    ]
    assert any(os.path.isdir(p) for p in candidate_dirs), (
        "zod is not installed in any of the expected locations: "
        f"{candidate_dirs}"
    )
