FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Next.js project pre-initialized for Novu Framework digest workflow task."

RUN cd /home/user && \
    npx create-next-app@14 app --ts --eslint --tailwind --app --src-dir=false --import-alias='@/*' --use-npm

# Container contents:
#   - Node.js v20 and npm installed.
#   - /home/user/app - Next.js project initialized with TypeScript and App Router.

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]
