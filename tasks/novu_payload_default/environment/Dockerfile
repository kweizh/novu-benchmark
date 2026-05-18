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
LABEL Description="Node.js environment with @novu/framework and zod installed for workflow creation."

RUN mkdir -p /home/user/project && \
    cd /home/user/project && \
    npm init -y && \
    npm install @novu/framework zod typescript @types/node tsx -D

# Container contents:
#   - Node.js v24 installed
#   - /home/user/project: initialized Node.js project with @novu/framework and zod

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
