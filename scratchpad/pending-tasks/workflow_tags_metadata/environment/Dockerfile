FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf pytest-xprocess requests && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/app && \
    cd /home/user/app && \
    cat >package.json <<'EOF'
{
  "name": "novu-marketing-campaign-bridge",
  "version": "1.0.0",
  "private": true,
  "type": "commonjs",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "@novu/framework": "^2.6.0",
    "express": "^4.19.2",
    "zod": "^3.23.8"
  }
}
EOF

RUN cd /home/user/app && npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="Novu Framework task environment with Node.js v20, Express, and @novu/framework pre-installed at /home/user/app."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - additional pip3 packages: pytest-xprocess, requests (used by initial/final state tests)
#   - Node.js v20 installed via NodeSource for running the Novu bridge
#   - /home/user/app: project directory with package.json declaring @novu/framework, express, and zod
#   - /home/user/app/node_modules: dependencies installed via `npm install`
