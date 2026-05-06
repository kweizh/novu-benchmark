# Novu SMS Workflow Integration

## Background
Create a Novu workflow that sends an SMS notification. You will use the `@novu/framework` to define the workflow in a Next.js application.

## Requirements
- Initialize a basic Next.js project.
- Install `@novu/framework`.
- Create a Novu workflow named `sms-alert`.
- The workflow must include an SMS step named `send-sms`.
- The workflow payload must be validated using `zod` and accept a `message` string.
- The SMS body should be the `message` from the payload.
- Expose the workflow via a Bridge Endpoint at `/api/novu`.

## Implementation Guide
1. Create a Next.js app in `/home/user/novu-app` using `npx create-next-app@latest novu-app --typescript --eslint --tailwind --no-src-dir --app --import-alias "@/*"`.
2. Install `@novu/framework` and `zod`: `npm install @novu/framework zod`.
3. Create a file `app/api/novu/workflows.ts` and define the `smsAlert` workflow using `step.sms`.
4. Create the Bridge Endpoint in `app/api/novu/route.ts` using `serve` from `@novu/framework/next` and export `GET`, `POST`, `OPTIONS`.

## Constraints
- Project path: `/home/user/novu-app`
- Start command: `npm run dev`
- Port: 3000
- The workflow must be exported as `smsAlert`.