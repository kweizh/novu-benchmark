FROM node:20-bullseye

RUN npm install -g zod zod-to-json-schema
ENV NODE_PATH=/usr/local/lib/node_modules

RUN useradd -m -s /bin/bash user

USER user
WORKDIR /home/user

# The test script will run as the root or user, but the project is under /home/user
