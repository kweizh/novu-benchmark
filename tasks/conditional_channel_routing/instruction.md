# Novu Conditional Channel Routing

## Background
Novu is an open-source notification infrastructure platform. The Novu Framework allows developers to define notification workflows in code. In many cases, you want to conditionally send notifications across certain channels based on the payload data (e.g., only send an email if the notification is marked as critical).

## Requirements
- Initialize a Node.js Express application in `/home/user/project`.
- Install `express`, `@novu/framework`, and `zod`.
- Create a Novu Bridge Endpoint at `/api/novu` using `@novu/framework/express`.
- Define a workflow named `conditional-routing`.
- The workflow must accept a payload validated by Zod with `userName` (string) and `critical` (boolean).
- The workflow must contain two steps:
  1. An `inApp` step named `notify-in-app` that always runs.
  2. An `email` step named `send-email` that is skipped if `payload.critical` is false.

## Implementation Guide
1. Initialize a Node project in `/home/user/project`.
2. Install required dependencies.
3. Create an `index.js` file.
4. Define the workflow using `@novu/framework`.
5. Use the `skip` option in the `email` step to evaluate `payload.critical`.
6. Expose the workflow via an Express route `/api/novu` using `serve` from `@novu/framework/express`.
7. Start the server on port 3000.

## Constraints
- Project path: `/home/user/project`
- Start command: `node index.js`
- Port: 3000
- The server must listen on port 3000.