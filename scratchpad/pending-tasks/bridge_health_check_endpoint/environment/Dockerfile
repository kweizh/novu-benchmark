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
  "name": "novu-bridge-health-check",
  "version": "1.0.0",
  "private": true,
  "description": "Novu bridge endpoint health-check task",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "@novu/framework": "^2.6.0",
    "express": "^4.21.0"
  }
}
EOF

RUN cd /home/user/app && npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="Novu Framework bridge health-check task environment with Node.js v20, @novu/framework and express pre-installed in /home/user/app."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - additional pip3 packages for verification: requests, pytest-xprocess
#   - Node.js v20 (LTS) installed via NodeSource for running the Novu Bridge Express server
#   - /home/user/app: Express application directory with package.json declaring
#     `@novu/framework` and `express` as dependencies, and `node_modules` pre-installed
