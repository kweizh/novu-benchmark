FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep psmisc && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf requests pytest-xprocess && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/app && chmod 0755 /home/user/app

LABEL Author="generate-harbor-tasks"
LABEL Description="Novu Framework bridge endpoint task environment with Node.js v20 and Python pytest tooling."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - psmisc (for fuser, used to free port 3000 in tests)
#   - always required pip3 packages: pytest-json-ctrf
#   - additional pip3 packages: requests, pytest-xprocess (used by tests/test_final_state.py)
#   - Node.js v20 for the @novu/framework + Express bridge endpoint
#   - /home/user/app: empty project directory for the Novu bridge implementation
