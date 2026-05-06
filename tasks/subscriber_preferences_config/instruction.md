# Configure Workflow Subscriber Preferences in Novu

## Background
Novu's Code-First Framework allows developers to define workflow channel preferences directly in code. This is useful for setting default delivery preferences (e.g., enabling In-App notifications while disabling Emails by default) and controlling whether subscribers can override these settings.

## Requirements
- Initialize a Next.js App Router project.
- Install `@novu/framework` and `zod`.
- Create a workflow with the ID `subscriber-preferences` and name `Subscriber Preferences`.
- The workflow should have two steps: `inApp` and `email`.
- Configure the workflow's payload schema using Zod to expect a `userName` string.
- Set the `inApp` step body to: `Hello ${payload.userName}, this is an in-app message.`
- Set the `email` step subject to `Preferences Test` and body to: `Hello ${payload.userName}, this is an email message.`
- Configure the workflow preferences so that `inApp` is enabled by default, `email` is disabled by default, and the preferences are NOT read-only (subscribers can change them).
- Expose the workflow via a Novu Bridge Endpoint at `/api/novu`.

## Implementation Guide
1. Create a Next.js app in `/home/user/myproject` using `npx create-next-app@latest myproject --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm`.
2. Install dependencies: `npm install @novu/framework zod` inside the project.
3. Create the workflow file at `src/novu/workflows.ts`.
4. Define the workflow using the `workflow` function from `@novu/framework`.
5. Use the `preferences` option in the workflow configuration to set the channel preferences.
6. Create the API route at `src/app/api/novu/route.ts` using `serve` from `@novu/framework/next` and pass the workflow to it.

## Constraints
- Project path: `/home/user/myproject`
- Start command: `npm run dev`
- Port: 3000
