FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf requests pytest-xprocess && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/app && chmod 0755 /home/user/app

LABEL Author="generate-harbor-tasks"
LABEL Description="Node.js 20 + Python 3 environment for triggering a Novu workflow via the @novu/api SDK against a locally mocked /v1/events/trigger endpoint."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v20 (from NodeSource) for running the agent's trigger.js script and installing @novu/api via npm
#   - Python 3 with `requests` and `pytest-xprocess` for the verifier's mock-server orchestration and HTTP checks
#   - /home/user/app: empty project directory where the agent initialises the Node.js project
