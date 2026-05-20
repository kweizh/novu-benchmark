# Novu Workflow With JSON Schema Payload Validation

## Background
The Novu Framework lets you describe a workflow's expected payload with either a Zod schema or a plain JSON Schema object (the `payloadSchema` option of the `workflow` factory accepts a `JsonSchema | ZodSchema`). Using a JSON Schema object is convenient when the schema needs to be portable, language-neutral, or generated outside of TypeScript. In this task you build a tiny Express-based Novu Bridge whose `account-alert` workflow declares its payload contract as a JSON Schema object.

## Requirements
- Create a Node.js project that uses `@novu/framework` together with the official Express adapter (`@novu/framework/express`).
- Define a workflow whose `workflowId` is `account-alert`.
- The workflow's `payloadSchema` must be a **plain JSON Schema object** (i.e. an object literal with `type: 'object'`, `properties`, `required`, etc.) - **do NOT use Zod** for this workflow's payload schema.
- The JSON Schema must require both `email` and `severity` and must constrain them as follows:
  - `email`: string, JSON Schema `format: 'email'`.
  - `severity`: string, restricted to the enum `['low','medium','high']`.
- The workflow must contain a single `inApp` step whose `stepId` is `notify` and whose resolved `body` uses Liquid placeholders to interpolate the payload, producing exactly `Severity {{ payload.severity }} alert for {{ payload.email }}`.
- Expose the Bridge endpoint at `GET/POST /api/novu` on an Express server bound to port `3000`.
- The application entrypoint must be `index.js` and `node index.js` must start the server.

## Implementation Hints
- Install `@novu/framework` and `express`.
- Pass a literal JSON Schema object (no Zod, no `z.object`) as `payloadSchema` in the workflow options. The framework documents `payloadSchema` as `JsonSchema | ZodSchema` so a plain object is a valid value.
- Use the `serve` helper from `@novu/framework/express` to mount the Bridge under `/api/novu`.
- Disable HMAC validation for local testing by setting `NOVU_STRICT_AUTHENTICATION_ENABLED=false` in the environment (or by passing the equivalent option to the client/serve helper).
- Liquid-style placeholders such as `{{ payload.severity }}` and `{{ payload.email }}` are interpolated by Novu at execution/preview time, so place them directly inside the body string returned by the in-app step resolver.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- Bridge endpoint: `/api/novu` (handles both `GET` and `POST`) mounted via the `@novu/framework/express` `serve` helper.
- Workflow identifier: `account-alert`.
- Workflow step: exactly one `inApp` step with `stepId` equal to `notify` and a `body` template equal to `Severity {{ payload.severity }} alert for {{ payload.email }}`.
- The discovery payload returned for this workflow must expose its `payload` JSON Schema such that:
  - `type` is `"object"`.
  - `required` contains both `"email"` and `"severity"`.
  - `properties.severity.enum` deeply equals `["low","medium","high"]` (any order is acceptable as long as the three values are present and no others).
  - `properties.email` describes a string-typed property (i.e. `type` is `"string"`).
- `GET /api/novu?action=discover` must return HTTP 200 and a JSON document that lists the `account-alert` workflow with the step and JSON Schema described above.
- `POST /api/novu?action=execute` with a payload missing the `email` field (e.g. `{ "severity": "high" }`) must result in a non-2xx HTTP response (any 4xx or 5xx is acceptable), demonstrating that the JSON Schema rejects invalid payloads.
- `POST /api/novu?action=preview` for the `notify` step with a valid payload (such as `{ "email": "alice@example.com", "severity": "medium" }`) must return HTTP 200 and the previewed `outputs.body` must equal `Severity medium alert for alice@example.com`.

