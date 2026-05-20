FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf pytest-xprocess && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user
RUN mkdir -p /home/user/app && chmod 0755 /home/user/app

LABEL Author="generate-harbor-tasks"
LABEL Description="Node.js v24 environment for scaffolding a Next.js App Router project that exposes a Novu Bridge Endpoint."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 packages: pytest-xprocess (used by test_final_state.py to manage the Next.js dev server)
#   - Node.js v24 (provides npm, npx) for installing and running Next.js and @novu/framework
#   - /home/user/app: empty project directory where the executor will scaffold the Next.js app
