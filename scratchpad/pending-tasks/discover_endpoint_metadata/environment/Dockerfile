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
  "name": "discover-endpoint-metadata",
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

RUN cd /home/user/app && npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="Novu Bridge discover endpoint task: Express + @novu/framework + zod pre-installed."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - additional pip3 packages for verification: pytest-xprocess, requests
#   - Node.js v20 (LTS) for running the Express + Novu bridge server
#   - /home/user/app: project directory with package.json and node_modules including
#       @novu/framework, express, and zod pre-installed
