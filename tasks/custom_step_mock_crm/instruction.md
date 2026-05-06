# Novu Custom Step with Mock CRM

## Background
You have an Express.js application that serves as both a mock CRM and a Novu Bridge. Novu provides a `step.custom` feature that allows workflows to fetch external data and use it in subsequent steps. Your task is to implement a Novu workflow that uses `step.custom` to fetch user details from a mock CRM API and then sends an email notification using that data.

## Requirements
1. Initialize an Express.js project in `/home/user/app`.
2. Install `@novu/framework`, `@novu/node`, `express`, and `zod`.
3. Create an Express server in `/home/user/app/index.js` running on port 3000.
4. Create a mock CRM endpoint `GET /api/crm/users/:id` that returns a JSON object `{ "name": "Alice", "company": "Acme Corp" }` for any ID.
5. Define a Novu workflow named `crm-notification` with a payload schema requiring `userId` (string).
6. In the workflow, add a `step.custom` named `fetch-crm-data` that makes an HTTP GET request (e.g., using `fetch`) to `http://localhost:3000/api/crm/users/${payload.userId}` and returns the JSON response. Define the `outputSchema` for the custom step to expect `name` and `company` as strings.
7. Add a `step.email` named `send-email` that uses the data returned from the custom step. The email subject should be `"Welcome to ${company}!"` and the body should be `"Hello ${name}, welcome to ${company}."`.
8. Serve the Novu workflow at `/api/novu` using the Express adapter from `@novu/framework/express`.

## Implementation Guide
1. Run `npm init -y` and `npm install express @novu/framework @novu/node zod`.
2. In `index.js`, use `express.json()` middleware.
3. Implement the `GET /api/crm/users/:id` route.
4. Implement the Novu workflow using `workflow`, `step.custom`, and `step.email`.
5. Use `serve` from `@novu/framework/express` to mount the workflow at `/api/novu`.
6. Start the server with `node index.js`.

## Constraints
- Project path: `/home/user/app`
- Start command: `node index.js`
- Port: 3000
- The custom step must make a real HTTP request to the mock CRM endpoint.

## Integrations
- None