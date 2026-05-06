# Novu Workflow with Conditional Skip

## Background
Using the `@novu/framework`, create a workflow that selectively sends notifications based on the payload attributes. This simulates sending a premium SMS only to premium subscribers.

## Requirements
- Initialize a Node.js project in `/home/user/novu-project`.
- Install `@novu/framework` and `zod`.
- Create an `index.ts` file that exports a workflow named `premiumNotification`.
- The workflow must have the ID `premium-notification`.
- Define a payload schema using `zod` with an `isPremium` boolean property (default `false`).
- The workflow should have an `inApp` step (stepId: `notify-in-app`) that always runs.
- The workflow should have an `sms` step (stepId: `notify-sms`) that sends an SMS with the body "Premium features unlocked!".
- The `sms` step must use the `skip` function to skip execution if `payload.isPremium` is `false`.

## Implementation Guide
1. `mkdir -p /home/user/novu-project && cd /home/user/novu-project`
2. Initialize a new project with `npm init -y`.
3. Install dependencies: `npm install @novu/framework zod typescript @types/node`.
4. Create `index.ts` and implement the workflow as described.

## Constraints
- Project path: `/home/user/novu-project`
- Use TypeScript for `index.ts`.