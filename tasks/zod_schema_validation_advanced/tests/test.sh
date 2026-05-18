#!/bin/bash

# Use this file to install test dependencies and run the tests.
# It will be copied to /tests/test.sh and run from the working directory.

curl -LsSf https://astral.sh/uv/0.9.7/install.sh | sh

source $HOME/.local/bin/env

# Ensure @novu/framework peer deps (zod, zod-to-json-schema) are installed in
# the agent's project dir. @novu/framework lists them as peer deps; npm v10
# does not auto-install peers, and ESM dynamic import does not consult NODE_PATH,
# so we must place them inside the project node_modules.
for d in /home/user/*/; do
  if [ -f "${d}package.json" ] && grep -q "@novu/framework" "${d}package.json"; then
    (cd "$d" && npm install --no-save --no-audit --no-fund zod zod-to-json-schema >/dev/null 2>&1)
  fi
done
# CTRF produces a standard test report in JSON format which is useful for logging.
uvx \
  --with pytest==8.4.1 \
  --with pytest-json-ctrf==0.3.5 \
  --with pochi-verifier \
  --with requests \
  pytest --ctrf /logs/verifier/ctrf.json /tests/test_final_state.py -rA
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
