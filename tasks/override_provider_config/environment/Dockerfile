FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm i -g @getpochi/cli tsx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g zod zod-to-json-schema
ENV NODE_PATH=/usr/lib/node_modules

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Next.js app with Novu framework installed for the override_provider_config task."

RUN cd /home/user && \
    npx create-next-app@latest app --typescript --eslint --tailwind --no-src-dir --app --import-alias "@/*" --use-npm && \
    cd app && \
    npm install @novu/framework zod zod-to-json-schema && \
    mkdir -p app/api/novu && \
    cat > app/api/novu/workflows.ts <<'EOF'
import { workflow } from '@novu/framework';
import { z } from 'zod';

// TODO: Implement dynamic-provider workflow here
EOF

# Container contents:
#   - Node.js v24 installed
#   - /home/user/app: Next.js project with @novu/framework and zod installed
#   - /home/user/app/app/api/novu/workflows.ts: Initial workflows file

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]