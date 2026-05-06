# Setup Novu Framework in a Remix Application

## Background
You have a basic Remix application. You need to integrate the Novu Framework to handle notifications by adding a Novu API endpoint and a test workflow.

## Requirements
- Install `@novu/framework` in the Remix application.
- Create a Novu workflow definition in `app/novu/workflows.ts` that defines a `test-workflow` with an email step.
- Create a Remix route at `app/routes/api.novu.ts` (which maps to `/api/novu`) that serves the Novu endpoint using the `test-workflow`.
- Add `NOVU_SECRET_KEY=your_secret_key` to a `.env` file in the project root.

## Implementation Guide
1. Navigate to `/home/user/my-novu-app`.
2. Install `@novu/framework` using npm.
3. Create `app/novu/workflows.ts` with a basic workflow named `test-workflow`.
4. Create `app/routes/api.novu.ts` and use `serve` from `@novu/framework/remix` to export `action` and `loader`.
5. Create a `.env` file with `NOVU_SECRET_KEY=your_secret_key`.

## Constraints
- Project path: /home/user/my-novu-app
- Start command: npm run dev
- Port: 5173