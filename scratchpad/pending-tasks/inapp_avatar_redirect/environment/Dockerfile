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
    npm init -y >/dev/null 2>&1 && \
    npm install --silent --save \
        @novu/framework \
        express \
        zod

LABEL Author="generate-harbor-tasks"
LABEL Description="Novu @novu/framework Express bridge task environment on Node.js v20."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - verification pip3 packages: requests, pytest-xprocess
#   - Node.js v20 for the Novu Express bridge
#   - /home/user/app: project directory with @novu/framework, express, zod preinstalled
