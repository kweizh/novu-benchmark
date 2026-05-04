FROM node:20-bullseye

RUN useradd -m -s /bin/bash user

USER user
WORKDIR /home/user

# The test script will run as the root or user, but the project is under /home/user
