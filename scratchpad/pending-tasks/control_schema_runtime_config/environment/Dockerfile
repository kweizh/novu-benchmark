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
RUN mkdir -p /home/user/app

RUN cd /home/user/app && \
    npm init -y >/dev/null && \
    npm install --no-audit --no-fund \
        @novu/framework@latest \
        express@^4.19.2 \
        zod@^3.23.8

ENV NOVU_STRICT_AUTHENTICATION_ENABLED=false

LABEL Author="generate-harbor-tasks"
LABEL Description="Novu Framework bridge environment (Node.js 20, Express, Zod) for control schema task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 packages: requests, pytest-xprocess (used by tests)
#   - Node.js v20 for running the Novu bridge
#   - /home/user/app: Node project pre-installed with @novu/framework, express, zod
#   - NOVU_STRICT_AUTHENTICATION_ENABLED=false to allow unauthenticated bridge calls locally
