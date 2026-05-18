FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g zod zod-to-json-schema
ENV NODE_PATH=/usr/lib/node_modules

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Node.js v24 environment for Novu Express app task."

RUN mkdir -p /home/user/novu-app && \
    cd /home/user/novu-app && \
    npm init -y

# Container contents:
#   - Node.js v24 installed.
#   - /home/user/novu-app — initialized Node.js project directory.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
