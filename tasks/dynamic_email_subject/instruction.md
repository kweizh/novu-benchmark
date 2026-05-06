# Dynamic Email Subject with Novu Framework

## Background
Novu is an open-source notification infrastructure platform. You can define workflows using code. In this task, you will create a simple workflow that dynamically sets the subject of an email notification based on the payload.

## Requirements
- Initialize a Node.js project in `/home/user/novu-project`.
- Install `@novu/framework`, `zod`, `express`, and `typescript`.
- Create a file `workflow.ts` that defines and exports a workflow named `dynamic-email`.
- The workflow should expect a payload with `orderId` (string) and `customerName` (string), validated using Zod.
- It must have an email step named `send-email`.
- The email subject must be dynamically generated as: `Order <orderId> confirmed for <customerName>`.
- The email body can be any string (e.g., "Hello").
- Create an `index.ts` that sets up an Express server and uses `serve` from `@novu/framework/express` to expose the workflow at `/api/novu`.
- The server should listen on port 3000.

## Implementation Guide
1. Create `/home/user/novu-project` and run `npm init -y`.
2. Install the necessary packages: `npm install @novu/framework zod express typescript @types/express tsx`.
3. Create `workflow.ts` with the workflow definition.
4. Create `index.ts` to serve the workflow.

## Constraints
- Project path: `/home/user/novu-project`
- Start command: `npx tsx index.ts`
- Port: 3000