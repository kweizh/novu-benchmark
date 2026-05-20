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

RUN mkdir -p /home/user/app && \
    cd /home/user/app && \
    cat >package.json <<'EOF'
{
  "name": "novu-multi-workflow-bridge",
  "version": "1.0.0",
  "private": true,
  "type": "commonjs",
  "dependencies": {
    "@novu/framework": "^2.6.0",
    "express": "^4.19.2",
    "zod": "^3.23.8"
  }
}
EOF

RUN cd /home/user/app && npm install --no-audit --no-fund

LABEL Author="generate-harbor-tasks"
LABEL Description="Novu Framework Bridge Endpoint task environment with Node.js 20 and @novu/framework, express, zod preinstalled in /home/user/app."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - additional pip3 packages: requests, pytest-xprocess (for final state verification)
#   - Node.js v20 for the Novu Framework bridge endpoint task
#   - /home/user/app: Node.js project directory with package.json
#   - /home/user/app/node_modules: pre-installed @novu/framework, express, zod
