# Novu Workflow: Skip Step Based on Payload Condition

## Background
Novu's `@novu/framework` lets you define notification workflows in code. Each step accepts an options object that may contain a `skip` function. When `skip` returns `true`, the framework treats the step as executed-but-skipped and does not run its resolver. The skip closure can reference values from the workflow handler scope, including the validated `payload`.

In this task you will expose a Novu Bridge endpoint built with Express that serves a workflow with two channel steps. The second step must be conditionally skipped based on a boolean flag in the payload.

## Requirements
- Implement a Novu workflow with workflow id `quiet-hours-notifier`.
- The workflow has TWO steps in order:
  1. An `inApp` step with stepId `notify-inapp` that ALWAYS runs. Its body must be `Heads up: {{ payload.message }}` (use a template variable interpolated by Novu, NOT a JavaScript string interpolation).
  2. A `push` step with stepId `notify-push`. Its `subject` must be `Notification` and its `body` must be `{{ payload.message }}`. The step must declare a `skip` option (a function) that returns `true` when `payload.quietHours === true`, and `false` otherwise.
- The workflow's `payloadSchema` (built with Zod) MUST require:
  - `message`: string
  - `quietHours`: boolean
- Expose the Novu Bridge using the Express adapter (`@novu/framework/express`).
- The server listens on port `3000`.
- HMAC strict authentication is disabled via the environment variable `NOVU_STRICT_AUTHENTICATION_ENABLED=false` (already set in the environment).

## Implementation Hints
- Install `@novu/framework`, `express`, and `zod`.
- Define the workflow with `workflow('quiet-hours-notifier', async ({ payload, step }) => { ... }, { payloadSchema: z.object({...}) })`.
- For the push step, pass `{ skip: () => payload.quietHours === true }` as the third argument so the closure can read the validated payload.
- Mount the bridge handler at the root path using `serve({ workflows: [...] })` from `@novu/framework/express`.
- Make sure `express.json()` middleware is registered before the Novu handler so the bridge can read JSON request bodies.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- The server exposes the Novu Bridge protocol on the root path and supports the following requests:
  - `GET /?action=discover` returns status `200` and a JSON body whose `workflows` array contains an entry whose `workflowId` is `quiet-hours-notifier` with a `steps` array that includes both `notify-inapp` (type `in_app`) and `notify-push` (type `push`).
  - `POST /?action=execute&workflowId=quiet-hours-notifier&stepId=notify-push` triggers execution of the push step. The request body is a Novu Bridge `Event` (JSON) that includes a `payload` object validated by the workflow's `payloadSchema`, plus a `state` array containing the hydrated `notify-inapp` step output. The response status is `200` and the JSON response satisfies:
    - When `payload.quietHours === false`, `options.skip` is `false` and `outputs.body` equals the value of `payload.message`.
    - When `payload.quietHours === true`, `options.skip` is `true` and `outputs` is an empty object `{}`.

