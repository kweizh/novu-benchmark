# Multi-Tenant Novu Workflow

## Background
Novu allows you to handle notifications for different tenants (organizations) within a single SaaS app. Create an Express.js application with a Novu Bridge endpoint that defines a multi-tenant workflow.

## Requirements
- Create a Novu workflow named `multi-tenant-workflow`.
- The workflow should send an email step.
- The email subject should be `Update from ${payload.tenantName}`.
- The email body should be `Hello ${payload.userName}, this is an update for your organization.`.
- The payload schema must validate `tenantName` and `userName` as strings using Zod.
- Serve the workflow via an Express endpoint at `/api/novu`.

## Implementation Guide
1. Initialize a Node.js project in `/home/user/myproject`.
2. Install `@novu/framework`, `express`, and `zod`.
3. Create an `index.js` that sets up the Express server.
4. Define the workflow using `@novu/framework`.
5. Use the `serve` function from `@novu/framework/express` to create the bridge endpoint at `/api/novu`.
6. Start the server on port 3000.

## Constraints
- Project path: `/home/user/myproject`
- Start command: `node index.js`
- Port: 3000
