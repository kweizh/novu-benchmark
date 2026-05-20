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
  "name": "novu-bulk-order-summary",
  "version": "1.0.0",
  "private": true,
  "description": "Novu Bridge with nested Zod payload schema (bulk-order-summary).",
  "dependencies": {
    "@novu/framework": "^2.6.0",
    "express": "^4.19.2",
    "zod": "^3.23.8"
  }
}
EOF

RUN cd /home/user/app && npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="Novu Framework + Express + Zod environment for the zod_payload_nested_arrays task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - pip3 packages for verifier: requests, pytest-xprocess
#   - Node.js v20 (NodeSource)
#   - /home/user/app: project directory pre-seeded with package.json
#   - /home/user/app/node_modules: pre-installed dependencies (@novu/framework, express, zod)
