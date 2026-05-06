# Multi-Channel Novu Workflow with Express

## Background
Novu provides a code-first framework to define notification workflows. You need to create a simple Express application that serves a Novu workflow with multiple channels (in-app and email).

## Requirements
- Initialize an Express application in `/home/user/novu-app`.
- Install `express` and `@novu/framework`.
- Create an `index.js` file that sets up an Express server.
- Define a workflow named `welcome-user` using `workflow` from `@novu/framework`.
- The workflow must include an `inApp` step named `notify-in-app` and an `email` step named `send-email`.
- Serve the workflow at the `/api/novu` endpoint using `serve` from `@novu/framework/express`.
- The server should listen on port 3000.

## Constraints
- Project path: `/home/user/novu-app`
- Start command: `node index.js`
- Port: 3000
- Ensure `express.json()` middleware is used before the Novu endpoint.