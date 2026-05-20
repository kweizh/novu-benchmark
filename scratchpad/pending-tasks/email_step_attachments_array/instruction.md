# Novu Email Step with Attachments Array

## Background
Novu Framework's TypeScript SDK lets you define notification workflows in code. The `email` step output supports an optional `attachments` array so emails can carry file payloads alongside the subject and body. This task asks you to build a single-workflow Novu Bridge endpoint that exposes an `invoice-email` workflow whose email step always attaches a small text file alongside the rendered subject and body.

## Requirements
- Build a Node.js project under `/home/user/app` that uses `@novu/framework`, `express`, and `zod` to expose a Novu Bridge endpoint.
- Define exactly one workflow with id `invoice-email`.
- The workflow's payload schema (Zod) must require a string field `invoiceNumber`.
- The workflow must contain a single `email` step with stepId `send-invoice` whose output object includes:
  - `subject`: rendered from the template `"Your invoice {{ payload.invoiceNumber }}"`.
  - `body`: the literal string `"Please find your invoice attached."`.
  - `attachments`: an array containing exactly one entry that represents the file `invoice.txt` (MIME type `text/plain`) whose contents are the base64 encoding of the literal text `Sample invoice content`.
- Mount the Novu serve handler on an Express app and listen on port 3000.
- Disable Novu strict authentication for local evaluation.

## Implementation Hints
- Install `@novu/framework`, `express`, and `zod` as real runtime dependencies — do not stub or mock them.
- Use `serve` from `@novu/framework/express` to wire the workflow client to an Express route (typically `/api/novu`).
- Use the Zod schema's `payloadSchema` option on `workflow(...)` so the framework validates and exposes the JSON schema during discovery.
- For the attachment, compute the base64 representation of the literal text `Sample invoice content` (for example with `Buffer.from(...).toString('base64')`).
- Refer to the Novu attachment shape used in Novu providers: each entry is an object with `file`, `name`, and `mime` fields. The `file` value should be the base64-encoded string.
- Set `NOVU_STRICT_AUTHENTICATION_ENABLED=false` in the process environment so the Bridge accepts unauthenticated discover/preview requests during evaluation.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- Bridge endpoints (mounted via the Novu Express serve handler):
  - `GET /api/novu?action=discover`
    - Returns status 200 with a JSON body containing a `workflows` array. The array must include exactly one workflow whose `workflowId` is `invoice-email` and which contains a step whose `stepId` is `send-invoice` and whose `type` is `email`.
  - `POST /api/novu?action=preview&workflowId=invoice-email&stepId=send-invoice`
    - Request body example:
      ```json
      {
        "inputs": {},
        "controls": {},
        "data": { "invoiceNumber": "INV-1" },
        "payload": { "invoiceNumber": "INV-1" },
        "state": [],
        "subscriber": {}
      }
      ```
    - Returns status 200 with a JSON body whose `outputs` field contains:
      - `subject` equal to `Your invoice INV-1`
      - `body` equal to `Please find your invoice attached.`
      - `attachments` array of length 1 whose only entry has `name` equal to `invoice.txt`, MIME type `text/plain` (under the `mime` field), and a base64 `file` string that decodes to `Sample invoice content`.

