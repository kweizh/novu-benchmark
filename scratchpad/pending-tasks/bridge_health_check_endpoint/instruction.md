# Novu Bridge Health-Check Endpoint

## Background
The Novu Framework exposes a single HTTP endpoint (commonly `/api/novu`) that the Novu Cloud Worker Engine uses to discover and execute workflows defined in your code. The bridge endpoint supports several `action` query parameters; the `health-check` action is used by Novu (and during local development) to confirm that the bridge is reachable and to report how many workflows and steps have been discovered.

In this task you will build a minimal Express.js application that mounts the Novu bridge at `/api/novu`, registers a single workflow, and demonstrates that the bridge's `health-check` and `discover` actions return the expected information.

## Requirements
- Build an Express.js application that mounts the Novu Framework bridge using `serve` from `@novu/framework/express`.
- Mount the bridge at the path `/api/novu` so that:
  - `GET /api/novu?action=health-check` reports the bridge health and discovery counts.
  - `GET /api/novu?action=discover` returns the registered workflows.
- Register exactly one workflow with the workflow id `system-ping`. The workflow must contain exactly one in-app step with the step id `ping-step` that produces a notification with `body` equal to `pong`.
- Run the bridge with HMAC signature verification disabled (suitable for local development / health-check evaluation).
- The application must start an HTTP server listening on port 3000.

## Implementation Hints
- Use the real `@novu/framework` and `express` packages; do not mock them.
- The `workflow` and `serve` helpers are exported from `@novu/framework` and `@novu/framework/express` respectively.
- An in-app step is created with `step.inApp('ping-step', async () => ({ body: 'pong' }))` inside the workflow definition.
- HMAC verification can be disabled either by setting `strictAuthentication: false` on the `Client`, or by setting the environment variable `NOVU_STRICT_AUTHENTICATION_ENABLED=false`.
- Express needs `express.json()` middleware so that the bridge can parse JSON request bodies.
- The Novu `serve` helper for Express returns an object with `GET`, `POST` and `OPTIONS` handlers; mount all of them at the same path.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- HTTP routes:
  - `GET /api/novu?action=health-check`: Returns status 200 and a JSON body shaped like:

    ```json
    {
      "status": "ok",
      "sdkVersion": string,
      "frameworkVersion": string,
      "discovered": {
        "workflows": number,
        "steps": number
      }
    }
    ```

    `discovered.workflows` must be at least 1 and `discovered.steps` must be at least 1.
  - `GET /api/novu?action=discover`: Returns status 200 and a JSON body that contains a `workflows` array. The array must include exactly one workflow whose `workflowId` is `system-ping` and whose `steps` array contains an entry with `stepId` equal to `ping-step` and `type` equal to `in_app`.

