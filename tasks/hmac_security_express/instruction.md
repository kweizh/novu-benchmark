# Secure Novu Bridge Endpoint in Express.js

## Background
Novu Framework allows you to define workflows in your code and expose them via a Bridge Endpoint. In production, this endpoint must be secured using HMAC verification to ensure only Novu Cloud can trigger your workflows.

## Requirements
- Initialize a Node.js Express application.
- Create a Novu workflow named `test-workflow` that sends an email.
- Expose this workflow via a Novu Bridge Endpoint at `/api/novu`.
- Configure the application to run in production mode (`NODE_ENV=production`) so that HMAC verification is enforced by default.
- Use `NOVU_SECRET_KEY` from the environment for HMAC verification.

## Implementation Guide
1. Initialize a new Node.js project in `/home/user/app`.
2. Install `express` and `@novu/framework`.
3. Create `index.js` that sets up an Express server listening on port 3000.
4. Define a workflow using `@novu/framework` and expose it at `/api/novu` using the `serve` function from `@novu/framework/express`.
5. Start the server using the command `npm start` which should execute `NODE_ENV=production node index.js`.

## Constraints
- Project path: /home/user/app
- Start command: npm start
- Port: 3000
- The server must read `NOVU_SECRET_KEY` from the environment.