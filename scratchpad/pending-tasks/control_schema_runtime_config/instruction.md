# Novu Step Control Schema with Runtime Overrides

## Background
The Novu Framework lets developers expose dashboard-editable "Controls" on a step using a `controlSchema`. These controls can be customized in the Novu Dashboard or supplied at runtime through the bridge `preview` action. In this task you will build a small Express-based Novu bridge that defines a workflow whose email step uses a Zod `controlSchema` with defaults, and whose resolver consumes those controls to render the final email subject and body.

## Requirements
- Use the real `@novu/framework` (no mocking) together with `express` and `zod`.
- Implement an Express server that exposes the Novu bridge at `/api/novu` on port `3000`.
- Define a workflow with `workflowId` `daily-report` containing a single `email` step with `stepId` `report-email`.
- The step `controlSchema` must be a Zod object with the following fields:
  - `headline`: string, default `"Daily Report"`.
  - `footer`: string, default `"Best, the Team"`.
- The workflow `payloadSchema` must be a Zod object requiring a single string field `userName`.
- The email step resolver must return:
  - `subject` equal to `controls.headline`.
  - `body` that ends with `\n` followed by `controls.footer` (i.e. the footer appears on its own final line, separated from the rest of the body by a newline). Any body greeting or message text in front of the footer is up to you.
- Bridge authentication strictness must be disabled by setting `NOVU_STRICT_AUTHENTICATION_ENABLED=false`. Do not invent or hardcode a real secret key.

## Implementation Hints
- The `serve` helper from `@novu/framework/express` returns an Express handler that you mount at `/api/novu`.
- The third argument to `step.email(...)` is an options object that accepts a `controlSchema` key (see https://docs.novu.co/framework/typescript/steps).
- Zod default values (`z.string().default("...")`) are applied automatically when controls are not provided by the caller.
- The bridge automatically exposes `?action=discover` and `?action=preview` query actions on the same `/api/novu` route. The discover action returns the registered workflow shape (including the JSON-Schema form of the controls). The preview action accepts a JSON body of the form `{ "controls": {...}, "payload": {...} }` and returns the resolved step outputs.
- Strict authentication can be disabled through the `NOVU_STRICT_AUTHENTICATION_ENABLED` environment variable so that you can call the bridge locally without a signed request.

## Acceptance Criteria
- Project path: `/home/user/app`
- Start command: `node index.js`
- Port: `3000`
- Bridge endpoint: `POST/GET http://localhost:3000/api/novu`
- Discover action (`GET /api/novu?action=discover`):
  - Returns HTTP 200 with a JSON body containing a `workflows` array.
  - One workflow has `workflowId` `daily-report` and contains a step with `stepId` `report-email` of type `email`.
  - That step's `controls` (or `controls.schema`) JSON Schema declares `headline` and `footer` string properties with default values `"Daily Report"` and `"Best, the Team"` respectively.
- Preview action with defaults (`POST /api/novu?action=preview&workflowId=daily-report&stepId=report-email`):
  - Request body: `{"controls": {}, "payload": {"userName": "Alice"}}`.
  - Response is HTTP 200.
  - The resolved step outputs include `subject` equal to `"Daily Report"`.
  - The resolved step outputs include `body` whose final line equals `"Best, the Team"` (i.e. the body ends with `\nBest, the Team`).
- Preview action with overrides (`POST /api/novu?action=preview&workflowId=daily-report&stepId=report-email`):
  - Request body: `{"controls": {"headline": "Custom!", "footer": "Bye!"}, "payload": {"userName": "Alice"}}`.
  - Response is HTTP 200.
  - The resolved step outputs include `subject` equal to `"Custom!"`.
  - The resolved step outputs include `body` that ends with `\nBye!`.
- Payload validation: a preview call with `payload` missing the required `userName` field must NOT return HTTP 200 (the bridge should reject it because of the Zod payload schema).

