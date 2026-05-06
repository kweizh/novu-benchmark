# Novu Workflow with Zod Validation

## Background
Create a multi-channel Novu workflow that sends an email and an in-app notification, using Zod to validate the payload.

## Requirements
- Initialize a Node.js project in `/home/user/myproject` with Express.
- Install `@novu/framework`, `express`, and `zod`.
- Create a file `novu/workflows.js` that exports a workflow named `welcome-user`.
- The workflow should have an `inApp` step named `notify-in-app` and an `email` step named `send-email`.
- Use Zod to define a `payloadSchema` that requires a `userName` (string, default: 'New User') and an optional `age` (number).
- Create `index.js` that sets up an Express server on port 3000 and exposes the Novu Bridge Endpoint at `/api/novu` serving the `welcome-user` workflow.

## Implementation Guide
1. `mkdir -p /home/user/myproject && cd /home/user/myproject`
2. `npm init -y`
3. `npm install express @novu/framework zod`
4. Write `novu/workflows.js` using `@novu/framework` and `zod`.
5. Write `index.js` using `@novu/framework/express`.

## Constraints
- Project path: /home/user/myproject
- Start command: `node index.js`
- Port: 3000