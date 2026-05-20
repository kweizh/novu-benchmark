# Novu Workflow with Default Channel Preferences

## Background
Novu's TypeScript Framework (`@novu/framework`) lets you ship workflows as code and expose them to Novu Cloud through a bridge endpoint. Each workflow can declare default subscriber preferences directly in code: enabling/disabling channels by default and marking the workflow as critical (so subscribers cannot opt out).

In this task you will build an Express bridge that serves a single security-alert workflow with carefully tuned default preferences for the email, SMS, and in-app channels, and you will mark the workflow as critical.

## Requirements
- Build a Node.js Express application that exposes Novu Framework workflows over a bridge endpoint at `POST /api/novu` (and the corresponding `GET` for discovery).
- Define a single workflow with the workflow id `security-alert` that contains two steps:
  - An `email` step with stepId `alert-email`, subject `Security alert`, and body `Suspicious activity detected.`
  - An `sms` step with stepId `alert-sms`, body `Suspicious activity detected. Open the app.`
- Configure default workflow `preferences` so that:
  - The workflow is critical (subscribers cannot disable it).
  - The email channel is enabled by default.
  - The SMS channel is disabled by default.
  - The in-app channel is enabled by default.
- The bridge must serve unauthenticated discovery (strict authentication disabled) so the verifier can call it without a real Novu secret key.

## Implementation Hints
- Use the official `@novu/framework` package together with its Express helper to mount the bridge handler.
- Use `zod` if you need payload validation, but a payload schema is not strictly required for this task.
- The workflow `preferences` field on `workflow(...)` accepts an `all` object (with `enabled` and `readOnly` properties) and a `channels` object keyed by `email`, `sms`, `inApp`, `chat`, `push`. Use these exact channel keys.
- A critical workflow is expressed by setting `readOnly: true` on the `all` preference object.
- Set `NOVU_STRICT_AUTHENTICATION_ENABLED=false` so the bridge accepts unsigned discovery requests during verification.
- Do not mock `@novu/framework`. Use the real package and real Express server.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- Bridge endpoint:
  - `GET /api/novu?action=discover`: Returns status 200 and a JSON document containing a `workflows` array.
  - The workflows array must contain exactly one workflow with `workflowId` equal to `security-alert`.
  - The workflow must declare exactly two steps with stepIds `alert-email` (type `email`) and `alert-sms` (type `sms`), in that order.
  - The workflow `preferences` object in the discover response must satisfy:
    - `preferences.all.readOnly` is `true` (the workflow is critical).
    - `preferences.channels.email.enabled` is `true`.
    - `preferences.channels.sms.enabled` is `false`.
    - `preferences.channels.inApp.enabled` is `true`.
- The environment variable `NOVU_STRICT_AUTHENTICATION_ENABLED` is set to `false` so the discover endpoint can be queried without a signed request.

