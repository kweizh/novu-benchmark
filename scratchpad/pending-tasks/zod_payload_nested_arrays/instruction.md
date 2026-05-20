# Novu Workflow with Nested Zod Payload Schema (Customer + Items Array)

## Background
Novu Framework lets you co-locate workflow logic and validation in your application. With Zod, you can define complex, **nested** payload schemas that the Novu Bridge enforces at runtime and exposes as JSON schema via the discover endpoint. Your task is to build an Express-based Novu Bridge that exposes a single workflow whose payload uses nested objects and arrays.

## Requirements
- Build a Node.js application that runs a Novu Bridge on top of Express, listening on port 3000.
- Register a workflow named `bulk-order-summary` using `@novu/framework`.
- The workflow's `payloadSchema` must be a Zod schema with the following nested shape:
  - `customer` — an object with `name` (string) and `email` (string, must be a valid email)
  - `items` — an array (with at least 1 element) of objects, each containing:
    - `sku` — string
    - `quantity` — positive integer
    - `price` — non-negative number
  - `totalAmount` — non-negative number
- The workflow contains a single `email` step named `summary-email` whose body and subject are rendered from the payload using Liquid templating.
- Do not enable Novu's strict authentication (we want the dev-mode bridge to be reachable for testing).

## Implementation Hints
- Use `@novu/framework` (the `serve` helper from `@novu/framework/express`) together with the Zod adapter to register a workflow under `/api/novu`.
- Use `z.object`, `z.array`, `z.number().int().positive()` and `z.string().email()` to express the nested constraints.
- Use Liquid expressions in the email step output to access nested fields (e.g. `{{ payload.customer.name }}`) and array length (e.g. `{{ payload.items.length }}`).
- The application must listen on port 3000 and be started with `node index.js` from `/home/user/app`.
- Disable strict authentication by setting `NOVU_STRICT_AUTHENTICATION_ENABLED=false` so the bridge endpoint can be exercised without signed HMAC headers.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- Bridge endpoint mounted under `/api/novu` and reachable for the following HTTP verbs:
  - `GET /api/novu?action=discover` returns a JSON discover payload that includes a workflow with id `bulk-order-summary` and a single email step with id `summary-email`. The workflow's `payload.schema` JSON Schema must describe nested `customer.name`, `customer.email`, and an `items` array (minItems 1) whose item schema includes `sku`, `quantity`, and `price`, where `quantity` is constrained to `integer` and the email field is constrained to `format: "email"`.
  - `POST /api/novu?action=execute&workflowId=bulk-order-summary&stepId=summary-email` rejects an invalid payload (e.g. `items: []` or a `customer.email` value that is not a valid email) with a non-2xx HTTP status.
  - `POST /api/novu?action=preview&workflowId=bulk-order-summary&stepId=summary-email` with a valid payload renders the email step output, where:
    - `subject` is exactly `Order summary for {{ payload.customer.name }}` (rendered),
    - `body` is exactly `Your order contains {{ payload.items.length }} items totaling ${{ payload.totalAmount }}.` (rendered).

