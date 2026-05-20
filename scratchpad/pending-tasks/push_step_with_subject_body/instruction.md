# Novu Workflow with Push Step (Subject + Body)

## Background
You are building a notification workflow for a mobile application using the [Novu Framework](https://docs.novu.co/framework). The workflow must send a push notification whose `subject` and `body` are rendered from the trigger payload using Liquid-style template variables. The workflow code will be exposed via a [Novu Bridge endpoint](https://docs.novu.co/framework/endpoint) so that the Novu Cloud (or local dev tooling) can discover and preview the workflow over HTTP.

## Requirements
- Implement a Novu workflow with ID `mobile-alert` using the `@novu/framework` TypeScript-style SDK (you may use plain JavaScript with `node index.js`).
- The workflow MUST contain exactly one step:
  - Channel: `push`
  - Step ID: `notify-push`
  - Output `subject`: rendered from the template `{{ payload.title }}`
  - Output `body`: rendered from the template `{{ payload.message }}`
- Define a Zod payload schema for the workflow that REQUIRES the following fields:
  - `title: string`
  - `message: string`
- Expose the workflow via a Novu Bridge endpoint using the official Express adapter from `@novu/framework/express` (the `serve` helper).
- Mount the Bridge handler at path `/api/novu`.
- The Express server must listen on port `3000`.
- The app must boot with `node index.js` from `/home/user/app`.

## Implementation Hints
- Use `@novu/framework` to declare the workflow and the push step. Refer to https://docs.novu.co/framework/typescript/steps/push for the push step output shape.
- Use `@novu/framework/express` `serve({ client })` and register the returned handler on `app.use('/api/novu', ...)` (or `app.all('/api/novu', ...)`).
- Wrap your push resolver so the returned object includes both `subject` and `body` literally containing the Liquid template strings; Novu's Bridge will render them with the payload at preview/execution time.
- Use Zod to declare `payloadSchema`. Both `title` and `message` should be required strings.
- Set the environment variable `NOVU_STRICT_AUTHENTICATION_ENABLED=false` so that the bridge endpoint can be discovered and previewed without a real Novu API key.
- Install only what you need: `@novu/framework`, `express`, `zod`.

## Acceptance Criteria
- Project path: `/home/user/app`
- Start command: `node index.js`
- Port: `3000`
- API Endpoints exposed by the Novu Bridge at `/api/novu`:
  - `GET /api/novu?action=discover`
    - Returns status `200`.
    - The JSON response includes a `workflows` array.
    - At least one workflow object satisfies all of:
      - `workflowId === "mobile-alert"`
      - Contains a step with `stepId === "notify-push"` whose `type` (or `template.type`) is `"push"`.
  - `POST /api/novu?action=preview&workflowId=mobile-alert&stepId=notify-push`
    - Request JSON body shape:
      ```json
      {
        "inputs": {},
        "controls": {},
        "data": { "title": "<string>", "message": "<string>" },
        "payload": { "title": "<string>", "message": "<string>" },
        "state": [],
        "subscriber": {}
      }
      ```
    - Returns status `200`.
    - The JSON response contains an `outputs` object with string fields `subject` and `body`. The values must equal the interpolated payload (i.e., `subject === payload.title`, `body === payload.message`).
- Payload validation: The workflow's payload schema must require both `title` and `message` as strings. A discover call must expose a JSON Schema for the payload that lists `title` and `message` under `required`.

