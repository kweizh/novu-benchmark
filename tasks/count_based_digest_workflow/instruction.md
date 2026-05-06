# Novu Digest Workflow

## Background
You need to create a notification workflow using `@novu/framework` that aggregates multiple events using a digest step before sending an email. Although the task is named `count_based_digest_workflow`, `@novu/framework` currently primarily supports time-based digests (e.g., batching for a certain time duration) and cron-based digests. You will implement a time-based digest that batches events for 5 minutes.

## Requirements
- Initialize a Node.js project in `/home/user/novu-app`.
- Install `@novu/framework` and `express`.
- Create a workflow named `digest-workflow`.
- The workflow should have a digest step named `digest-events` that batches events for 5 minutes.
- After the digest step, add an email step named `send-email` that sends a summary email containing the number of digested events.
- Serve the workflow using an Express server on port 3000 at the `/api/novu` endpoint.

## Implementation Guide
1. `mkdir -p /home/user/novu-app` and `cd /home/user/novu-app`.
2. `npm init -y` and `npm install @novu/framework express`.
3. Create `index.js`.
4. In `index.js`, define the workflow using `workflow` from `@novu/framework`.
5. Use `step.digest` to wait for 5 minutes (`amount: 5, unit: 'minutes'`).
6. Use `step.email` to send an email with the subject `Digest Summary` and body `You have ${events.length} new events`.
7. Use `serve` from `@novu/framework/express` to mount the workflow on an Express app at `/api/novu`.
8. Start the Express server on port 3000.

## Constraints
- Project path: /home/user/novu-app
- Start command: `node index.js`
- Port: 3000