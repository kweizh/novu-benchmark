# Novu Workflow with Metadata and Tags

## Background
Novu Framework lets you annotate workflows with human-friendly metadata so they can be filtered and organized in the Novu Dashboard and Inbox component. In this task you will define a small marketing workflow and ensure it is correctly described with a `name`, `description`, and a set of `tags`.

## Requirements
- Build a Novu Bridge endpoint using Express that serves the Novu Framework at `/api/novu`.
- Define a workflow with id `marketing-campaign` configured with the following metadata:
  - A human-readable display name `Marketing Campaign`.
  - A description: `Promotional emails for new product launches.`.
  - The tags `marketing`, `promotion`, and `product-launch` (in this order).
- The workflow must contain a single email step with id `promo-email` that emits the subject `Big launch!` and the body `Check out our new product.`.
- The bridge server must run on port `3000` and must operate with `NOVU_STRICT_AUTHENTICATION_ENABLED=false` so that an unauthenticated `?action=discover` request is allowed.

## Implementation Hints
- Use `@novu/framework` together with `@novu/framework/express` (`serve`) to mount the bridge on an Express app.
- The workflow factory accepts an options object as its third argument where you can set `name`, `description`, and `tags`.
- The email step handler should return an object with `subject` and `body` properties.
- Disable strict authentication via the `NOVU_STRICT_AUTHENTICATION_ENABLED` environment variable for this local task.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- A GET request to `http://localhost:3000/api/novu?action=discover` returns HTTP 200 with JSON whose `workflows` array contains exactly one entry where:
  - `workflowId` equals `marketing-campaign`.
  - `name` equals `Marketing Campaign`.
  - `description` equals `Promotional emails for new product launches.`.
  - `tags` is an array equal to `["marketing", "promotion", "product-launch"]`.
  - The workflow exposes one email step whose `stepId` is `promo-email`.
- A GET request to `http://localhost:3000/api/novu?action=preview&workflowId=marketing-campaign&stepId=promo-email` (POSTed with an empty payload/controls body where required) returns the email output containing `subject: "Big launch!"` and `body: "Check out our new product."`.

