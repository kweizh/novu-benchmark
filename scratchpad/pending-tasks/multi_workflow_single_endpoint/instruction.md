# Multiple Novu Workflows Served from a Single Bridge Endpoint (Express)

## Background
The Novu Framework lets you define workflows in code and expose them through a single Bridge Endpoint. A single `serve()` call can register many workflows at once, which is the recommended way to keep all of your notification logic discoverable from one URL. In this task you will build an Express.js Bridge Endpoint that registers three different workflows (in-app, transactional email, and a digested weekly summary) under one `/api/novu` endpoint.

## Requirements
- Build an Express.js application that mounts the Novu Bridge Endpoint at `/api/novu` using `serve` from `@novu/framework/express`.
- Register three workflows in a single `serve({ workflows: [...] })` call:
  1. `welcome-user`: contains one in-app step with the step id `notify` and body `Welcome aboard!`.
  2. `password-reset`: contains one email step with the step id `reset-email`, subject `Reset your password`, and body `Click here to reset.`.
  3. `weekly-digest`: contains a digest step with the step id `batch` (amount `7`, unit `days`) followed by an email step with the step id `summary` and subject `Your weekly summary`.
- The server must listen on port `3000`.
- The Bridge Endpoint must respond to `GET /api/novu?action=discover` with metadata describing all three workflows and their steps.

## Implementation Hints
- Install the real `@novu/framework`, `express`, and `zod` packages — do not mock them.
- Use `workflow(id, async ({ step }) => { ... })` from `@novu/framework` to define each workflow.
- Mount the bridge handler with `app.use('/api/novu', serve({ workflows: [...] }))` after `app.use(express.json())`.
- For local evaluation, the Novu strict authentication check must be disabled. The environment variable `NOVU_STRICT_AUTHENTICATION_ENABLED=false` is already set for you.

## Acceptance Criteria
- Project path: `/home/user/app`
- Start command: `node index.js`
- Port: `3000`
- API Endpoint:
  - `GET /api/novu?action=discover`: Returns status `200` and a JSON body that includes a `workflows` array. Each workflow entry exposes at least the workflow id and an array of steps; each step exposes its step id and step type. The response must contain all three workflows with the following ids and steps:
    - workflow id `welcome-user` with a step id `notify` of type `in_app`.
    - workflow id `password-reset` with a step id `reset-email` of type `email`.
    - workflow id `weekly-digest` with steps `batch` (type `digest`) and `summary` (type `email`).

