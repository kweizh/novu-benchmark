# Novu Digest Workflow with Look-Back Window

## Background
Novu Framework lets you author notification workflows as code and serve them through a Bridge Endpoint. The `digest` action step aggregates multiple events triggered for the same subscriber into one notification. The Look-Back strategy adds a guard: before creating a digest, Novu checks whether any event was triggered for the same subscriber within the prior `lookBackWindow` period. If yes, a digest is created; otherwise the event is sent immediately and digest creation is skipped.

You must build a small Express application that exposes a Novu Bridge Endpoint and registers a digest-based workflow that demonstrates the Look-Back strategy.

## Requirements
- Use real `@novu/framework`, `express`, and `zod` packages. Do not stub or mock any framework primitives.
- Define a workflow with the workflow id `notification-digest`.
- The workflow must contain exactly two steps in this order:
  1. A `digest` step with stepId `batch-events` whose resolver returns a regular (count-based) digest configuration:
     - `amount`: `5`
     - `unit`: `"seconds"`
     - `lookBackWindow`: an object with `amount: 10` and `unit: "minutes"`.
  2. An `email` step with stepId `summary-email` whose resolver returns:
     - `subject`: the exact Liquid template string `You have {{ steps['batch-events'].events.length }} new notifications`
     - `body`: the exact string `Check them out in your dashboard.`
- Expose the workflow through the Express adapter `@novu/framework/express` mounted at path `/api/novu`.
- The Express server must listen on port 3000.
- The project must be runnable directly from TypeScript sources (no compile step required by the verifier). The standard `npm start` command should boot the server.

## Implementation Hints
- The Novu Bridge Endpoint must accept `GET`, `POST`, `PUT`, and `OPTIONS` requests via the framework's `serve` export. `express.json()` must be installed before mounting the handler.
- Look-back is configured by returning a `lookBackWindow` object from the digest resolver alongside `amount` and `unit`. The shape is `{ amount: number, unit: 'seconds' | 'minutes' | 'hours' | 'days' | 'weeks' | 'months' }`.
- During development the Bridge Endpoint requires HMAC signatures by default. To make local verification possible, set the environment variable `NOVU_STRICT_AUTHENTICATION_ENABLED=false` (already configured in the environment) so the framework skips HMAC validation.
- A valid `NOVU_SECRET_KEY` env var must be available to the process at start time; a dummy non-empty value is acceptable for local development.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: npm start
- Port: 3000
- The application listens on `http://localhost:3000` and serves the Novu Bridge Endpoint at `/api/novu`.
- API endpoints exposed by the Bridge handler:
  - `GET /api/novu` (no query string) returns a `200 OK` JSON health check response.
  - `GET /api/novu?action=discover` returns `200 OK` with a JSON body containing a `workflows` array. The array MUST include an entry whose `workflowId` equals `notification-digest` and whose `steps` array contains two entries with `stepId` values `batch-events` (type `digest`) and `summary-email` (type `email`) in that order.
  - `POST /api/novu?action=preview&workflowId=notification-digest&stepId=batch-events` accepts the Novu preview request body and returns `200 OK` with a JSON body whose `outputs` field includes:
    ```json
    {
      "amount": 5,
      "unit": "seconds",
      "lookBackWindow": { "amount": 10, "unit": "minutes" }
    }
    ```
  - `POST /api/novu?action=preview&workflowId=notification-digest&stepId=summary-email` accepts the Novu preview request body (including prior step state for `batch-events`) and returns `200 OK` with a JSON body whose `outputs.subject` reflects the number of digested events from the supplied state and whose `outputs.body` equals `Check them out in your dashboard.`.

