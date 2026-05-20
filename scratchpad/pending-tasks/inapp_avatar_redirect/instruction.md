# Novu In-App Step with Avatar and Redirect

## Background
You are building a notification bridge for a collaborative threads product. When someone is mentioned in a comment, an in-app notification should appear in the user's inbox with the mentioner's avatar and clickable behavior that opens the relevant thread inside the current tab. Use the `@novu/framework` TypeScript/JavaScript SDK behind an Express bridge endpoint to define this notification workflow.

## Requirements
- Create a Novu workflow with id `comment-mention`.
- The workflow declares a Zod payload schema requiring three string fields: `commenter`, `threadTitle`, and `threadId`.
- Add a single `inApp` step with id `notify-mention` that resolves the following outputs from the payload:
  - `subject`: `"New mention"`
  - `body`: `"{{ payload.commenter }} mentioned you in {{ payload.threadTitle }}"` (the placeholders must interpolate the payload values at preview time).
  - `avatar`: `"https://cdn.example.com/avatar.png"`
  - `redirect`: an object with `url` set to `"/threads/{{ payload.threadId }}"` and `target` set to `"_self"`.
- Serve the bridge over Express with the Novu `serve` handler mounted at `/api/novu`.

## Implementation Hints
- Install and use the real `@novu/framework`, `express`, and `zod` packages. Do not mock or stub them.
- Use the Express bridge integration from `@novu/framework/express` and bind the Novu client to the workflow before serving.
- The body and redirect URL must rely on Novu's template interpolation (e.g. Liquid-style `{{ payload.commenter }}`) so the framework substitutes values at preview/runtime.
- Disable strict authentication for local evaluation by setting `NOVU_STRICT_AUTHENTICATION_ENABLED=false` in the process environment.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- Bridge endpoint base path: `/api/novu`
- The discover endpoint (`GET /api/novu?action=discover`) must list a workflow with id `comment-mention` containing a step with id `notify-mention` of type `in_app`.
- The preview endpoint (`POST /api/novu?action=preview&workflowId=comment-mention&stepId=notify-mention`) must accept a JSON body containing `data` (the payload) and respond with a JSON object whose `outputs` field contains:
  - `subject` equal to `"New mention"`
  - `body` equal to the interpolated string using the provided `commenter` and `threadTitle`
  - `avatar` equal to `"https://cdn.example.com/avatar.png"`
  - `redirect.url` equal to `"/threads/<threadId>"` using the provided `threadId`
  - `redirect.target` equal to `"_self"`
- A request to the preview endpoint with payload missing any required field must fail validation (non-2xx response).

