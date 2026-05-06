# Novu Workflow Error Handling

## Background
Novu provides a code-first framework for defining notification workflows. It supports payload validation using Zod and allows you to write custom code in custom steps. This task focuses on implementing a workflow that validates its payload and correctly surfaces errors from custom steps.

## Requirements
- Create an Express.js application that serves a Novu Bridge endpoint.
- Define a Novu workflow named `error-handling-workflow`.
- The workflow must use a Zod schema for payload validation, requiring `userId` (string) and `simulateError` (boolean, defaults to false).
- Implement a custom step named `fetch-data`. If `payload.simulateError` is true, the step must throw an `Error` with the message `"External API Failed"`. If false, it returns `{ status: "ok" }`.
- Implement an `email` step named `send-email` that sends an email with the subject `"Process Complete"` and a body containing the status from the custom step.

## Implementation Guide
1. Initialize a Node.js project in `/home/user/novu-app`.
2. Install `express`, `@novu/framework`, and `zod`.
3. Create `index.js`.
4. Define the workflow using the `@novu/framework` `workflow` function.
5. Set up an Express server and mount the Novu Bridge using the `serve` function from `@novu/framework/express` at the `/api/novu` route.
6. Ensure the server listens on port 3000.

## Constraints
- Project path: `/home/user/novu-app`
- Start command: `node index.js`
- Port: 3000