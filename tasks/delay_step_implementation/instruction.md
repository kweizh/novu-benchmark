# Implement a Delay Step in Novu Workflow

## Background
You are building a notification system using the Novu Framework with an Express.js backend. You need to implement a workflow that delays a follow-up notification by a specific duration (e.g., 24 hours) after an initial trigger.

## Requirements
- Initialize an Express.js application.
- Install `@novu/framework` and `express`.
- Create a Novu workflow named `follow-up-workflow`.
- The workflow must include a delay step (named `reminder-delay`) configured to pause execution for 24 hours.
- Following the delay, it must include an email step (named `follow-up-email`) with the subject `How are you liking our product?`.
- Expose the Novu Bridge Endpoint at `/api/novu` in the Express app.

## Implementation Guide
1. Initialize a Node.js project in `/home/user/myproject`.
2. Install `express` and `@novu/framework`.
3. Create a file `workflows.js` (or `.ts` if using TypeScript) to define your `follow-up-workflow` using `workflow` and `step` from `@novu/framework`.
4. In the workflow definition, use `await step.delay('reminder-delay', async () => ({ amount: 24, unit: 'hours' }))`.
5. Next, use `await step.email('follow-up-email', async () => ({ subject: 'How are you liking our product?', body: 'Just checking in!' }))`.
6. Create an `index.js` file that sets up an Express app. Import the workflow and use the `serve` function from `@novu/framework/express` to mount it on `/api/novu`.
7. Start the Express server on port 3000.

## Constraints
- Project path: `/home/user/myproject`
- Start command: `node index.js`
- Port: 3000
- The workflow must be named `follow-up-workflow`.
- The delay step must be named `reminder-delay`.
- The email step must be named `follow-up-email`.

## Integrations
- None