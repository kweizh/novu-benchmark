# Novu In-App Step With Action Buttons

## Background
Novu Framework's `inApp` channel step can render an interactive `<Inbox />` notification that includes optional `primaryAction` and `secondaryAction` buttons. Each action has a `label` and a `redirect` object whose `url` controls where the user is sent when the button is clicked. In this task you must build an Express-based Bridge application that exposes a workflow whose in-app notification carries two such action buttons used to approve or decline an incoming request.

## Requirements
- Create a Node.js project that uses `@novu/framework` together with the official Express adapter (`@novu/framework/express`).
- Define a workflow with identifier `approval-request`.
- The workflow must contain a single `inApp` step. Its rendered output must include:
  - A `body` derived from the trigger payload that mentions the requester (the payload field that holds the requester name is described in the Acceptance Criteria).
  - A `primaryAction` with the label `Approve` redirecting to `/requests/approve`.
  - A `secondaryAction` with the label `Decline` redirecting to `/requests/decline`.
- The workflow's payload schema must require a `requester` field of type string (use `zod`).
- Expose the Bridge endpoint at `POST/GET /api/novu` on an Express server listening on port 3000.
- The application entrypoint must be `index.js` and `node index.js` must start the server.

## Implementation Hints
- Install `@novu/framework`, `express`, and `zod`.
- Use the `workflow` factory from `@novu/framework` and the `serve` helper from `@novu/framework/express` to mount the Bridge endpoint.
- The `inApp` step resolver returns an object whose `primaryAction` and `secondaryAction` follow the Novu Framework schema (each is an object with a `label` string and a `redirect` object containing `url`).
- Disable HMAC validation for local testing, for example by passing `strictAuthentication: false` to the `Client`/`serve` options or by running the process with `NODE_ENV=development`.
- Use Liquid-style placeholders (e.g. `{{payload.requester}}`) inside the body string so Novu can substitute payload values at execution time.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- Bridge endpoint: `/api/novu` mounted via the `@novu/framework/express` `serve` helper.
- Workflow identifier: `approval-request`.
- Payload schema: requires a string field named `requester`.
- In-app step output schema (returned by the resolver), as documented at https://docs.novu.co/framework/typescript/steps/inApp :
  ```json
  {
    "body": "You have a new approval request from <requester>.",
    "primaryAction": {
      "label": "Approve",
      "redirect": { "url": "/requests/approve" }
    },
    "secondaryAction": {
      "label": "Decline",
      "redirect": { "url": "/requests/decline" }
    }
  }
  ```
- `GET /api/novu?action=discover` must return a JSON document that lists a workflow with `workflowId` equal to `approval-request` and at least one step with channel type `in_app`.
- `POST /api/novu?action=execute&workflowId=approval-request&stepId=<stepId>` with a body `{ "action": "execute", "workflowId": "approval-request", "stepId": "<stepId>", "payload": { "requester": "<name>" }, "controls": {}, "subscriber": { "subscriberId": "test-subscriber" }, "state": [], "inputs": {} }` must return HTTP 200 and a JSON body whose `outputs` field matches the in-app step output schema above, with `<requester>` replaced by the value provided in the request payload.

