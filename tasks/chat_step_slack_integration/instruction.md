# Novu Chat Step Slack Integration

## Background
Create an Express.js application that serves a Novu Bridge Endpoint containing a workflow. The workflow should use the Chat step to send a notification, specifically simulating a Slack integration.

## Requirements
- Initialize a Node.js project in `/home/user/myproject`.
- Install `express` and `@novu/framework`.
- Create a workflow named `slack-notification`.
- The workflow must contain a chat step with the ID `send-to-slack`.
- The chat step must return a `body` with the text `"Hello from Novu!"`.
- Configure an Express server to serve the Novu endpoint at `/api/novu`.
- The Express server must listen on port 3000.

## Implementation Guide
1. Run `npm init -y` in `/home/user/myproject`.
2. Install the required packages: `npm install express @novu/framework`.
3. Create a `novu/workflows.js` file and define the `slack-notification` workflow using `@novu/framework`.
4. Create an `index.js` file to set up the Express server and serve the workflow at `/api/novu` using `serve` from `@novu/framework/express`.

## Constraints
- Project path: `/home/user/myproject`
- Start command: `node index.js`
- Port: 3000
- The workflow must be exported so it can be served.

## Integrations
- None