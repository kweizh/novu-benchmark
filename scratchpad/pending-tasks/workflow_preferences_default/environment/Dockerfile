FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf pytest-xprocess requests && \
    npm install -g @novu/framework@latest express@4 zod@3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/app && chmod 0755 /home/user/app

# Make the globally installed Node modules visible to `require()` resolution
# inside /home/user/app so a simple `node index.js` can import @novu/framework,
# express, and zod without needing a local package.json.
ENV NODE_PATH=/usr/lib/node_modules
ENV NOVU_STRICT_AUTHENTICATION_ENABLED=false

LABEL Author="generate-harbor-tasks"
LABEL Description="Novu Framework bridge environment with Node.js 20, @novu/framework, express, and zod preinstalled for the workflow_preferences_default task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - additional pip3 packages used by tests: pytest-xprocess, requests
#   - Node.js v20 for running the Novu Framework Express bridge
#   - Global npm packages: @novu/framework, express@4, zod@3
#   - NODE_PATH set so /home/user/app can resolve globally installed modules
#   - NOVU_STRICT_AUTHENTICATION_ENABLED=false so the discover endpoint accepts unsigned requests
#   - /home/user/app: project directory for the Novu bridge application
