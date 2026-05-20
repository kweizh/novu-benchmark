# Novu Delay Step Workflow

## Background
You are building a notification reminder system using the [Novu Framework](https://docs.novu.co/framework). Novu provides a code-first workflow engine where workflows are defined as TypeScript/JavaScript functions and exposed via a bridge endpoint that Novu Cloud (or the Novu Studio) discovers and previews.

In this task you must implement a small Novu workflow that waits for one hour before sending a reminder email to the user. The workflow must be served by an Express bridge endpoint.

## Requirements
- Use the real `@novu/framework`, `express`, and `zod` packages (no mocks or stubs).
- Define a workflow with `workflowId` = `reminder-flow`.
- The workflow must declare a Zod payload schema that requires a `userName` field of type `string`.
- The workflow must contain exactly two steps, in this order:
  1. A `delay` step with stepId `wait-an-hour` configured to wait `1 hour` of `type: 'regular'`.
  2. An `email` step with stepId `reminder-email` whose subject is `Reminder: don't forget!` and body is `It's been an hour, here's your reminder.`.
- Serve the workflow through an Express bridge endpoint mounted on `/api/novu`.
- The Express server must listen on port `3000`.
- Allow unsigned dev requests by setting the environment variable `NOVU_STRICT_AUTHENTICATION_ENABLED=false`.

## Implementation Hints
- Install `@novu/framework`, `express`, and `zod` with npm.
- Use `@novu/framework`'s `workflow()` to define the workflow and `serve()` (from `@novu/framework/express`) to mount the bridge handler on `/api/novu`.
- Inside the workflow function, call `step.delay(...)` and return an object that includes `type`, `amount`, and `unit` to configure the delay duration. Refer to https://docs.novu.co/framework/typescript/steps/delay and https://docs.novu.co/framework/delay for the exact field names.
- Use `step.email(...)` to define the email step and return `subject` and `body` from its resolver.
- The bridge endpoint will be discovered and previewed by HTTP requests to `/api/novu?action=discover` and `/api/novu?action=preview`.

## Acceptance Criteria
- Project path: `/home/user/app`
- Start command: `node index.js`
- Port: 3000
- The bridge endpoint must be reachable at `http://localhost:3000/api/novu`.
- `GET http://localhost:3000/api/novu?action=discover` must respond with status 200 and a JSON body that lists exactly one workflow with `workflowId` = `reminder-flow` containing two steps in order: a `delay` step with stepId `wait-an-hour` and an `email` step with stepId `reminder-email`.
- `POST http://localhost:3000/api/novu?action=preview&workflowId=reminder-flow&stepId=wait-an-hour` (with a valid JSON body containing `userName`) must respond with status 200 and return delay step output containing `type: 'regular'`, `amount: 1`, and `unit: 'hours'`.
- `POST http://localhost:3000/api/novu?action=preview&workflowId=reminder-flow&stepId=reminder-email` must respond with status 200 and return email step output whose `subject` equals `Reminder: don't forget!` and whose `body` equals `It's been an hour, here's your reminder.`.

