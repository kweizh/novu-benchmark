# Novu Bridge Discover Endpoint Metadata

## Background
Novu Framework exposes a single Bridge Endpoint that serves workflow definitions and content to the Novu Worker Engine. When the engine calls the endpoint with `action=discover`, it expects a complete metadata listing of all defined workflows: workflow IDs, names, descriptions, payload schemas (with constraints such as enum values), and the ordered list of steps with their channel types. Your task is to build an Express-based Bridge Endpoint that exposes a single workflow with the correct metadata so it is fully discoverable by Novu.

## Requirements
- Build an Express.js application that exposes the Novu Bridge Endpoint at `/api/novu` on port 3000.
- Use the official `@novu/framework` package together with `express` and `zod`.
- Define exactly one workflow with `workflowId` of `order-status`.
  - Workflow `name` must be `Order Status Updates`.
  - Workflow `description` must be `Sends order updates via email and SMS`.
  - The workflow `payloadSchema` is a Zod schema that requires:
    - `orderId`: a string.
    - `status`: an enum constrained to the values `shipped`, `delivered`, `canceled`.
- The workflow must declare two steps in this exact order:
  1. An email step with `stepId` `order-email`, subject `Order {{ payload.orderId }}`, and body `Status: {{ payload.status }}`.
  2. An SMS step with `stepId` `order-sms`, and body `Order {{ payload.orderId }} is now {{ payload.status }}`.
- The endpoint must successfully respond to `GET /api/novu?action=discover` and `POST /api/novu?action=preview` for both steps.

## Implementation Hints
- Use the `serve` function from `@novu/framework/express` to wire the workflow client into Express.
- Use `workflow(...)` from `@novu/framework` to register a workflow and its steps via the `step.email` and `step.sms` helpers.
- Use `zod` to declare the payload schema and pass it via the workflow `payloadSchema` option.
- Use the placeholder syntax `{{ payload.<field> }}` directly in subject/body strings to enable preview interpolation.
- Strict authentication should be disabled for local discovery; the environment will set `NOVU_STRICT_AUTHENTICATION_ENABLED=false`.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- API Endpoints:
  - GET `/api/novu?action=discover`: Returns status 200 with a JSON body that contains a `workflows` array. The array must contain exactly one workflow whose:
    - `workflowId` is `order-status`.
    - `name` is `Order Status Updates`.
    - `description` is `Sends order updates via email and SMS`.
    - `payload.schema` includes an enum constraint for `status` with values `shipped`, `delivered`, `canceled`, and requires `orderId`.
    - `steps` array contains exactly two entries in order: an `email` step with `stepId` `order-email` followed by an `sms` step with `stepId` `order-sms`.
  - POST `/api/novu?action=preview&workflowId=order-status&stepId=order-email`: With JSON body `{"payload": {"orderId": "O-99", "status": "shipped"}, "controls": {}}`, returns status 200 and resolves the email subject to `Order O-99` and the body to `Status: shipped`.
  - POST `/api/novu?action=preview&workflowId=order-status&stepId=order-sms`: With the same body, returns status 200 and resolves the SMS body to `Order O-99 is now shipped`.

