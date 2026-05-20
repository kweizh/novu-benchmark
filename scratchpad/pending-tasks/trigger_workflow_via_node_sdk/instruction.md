# Trigger a Novu Workflow with the Node SDK

## Background
Novu publishes an official Node/TypeScript SDK on npm as `@novu/api` (`import { Novu } from "@novu/api"`). The SDK lets server-side applications call the Novu REST API (`POST /v1/events/trigger`) to fire a workflow for one or more subscribers. Your goal is to build a small Node.js script that uses this SDK to trigger a workflow named `welcome-workflow` and persists the parsed response to disk.

Because this evaluation runs inside a hermetic container without access to the real Novu Cloud, the verifier will start a tiny local HTTP server that mimics the `/v1/events/trigger` endpoint. The verifier configures the SDK to point at that local server through the `NOVU_API_BASE_URL` environment variable. Your script must read that variable and, when it is set, pass it to the SDK as its server URL override so the request reaches the mock instead of `https://api.novu.co`.

## Requirements
- Initialize a Node.js project at `/home/user/app` (a `package.json` with `@novu/api` listed under `dependencies`).
- Install `@novu/api` locally into `/home/user/app/node_modules`.
- Create an executable script `/home/user/app/trigger.js` that:
  - Instantiates the `Novu` client from `@novu/api`, reading `NOVU_SECRET_KEY` from the environment for the `secretKey` option.
  - When `NOVU_API_BASE_URL` is set, configures the SDK to direct requests to that URL instead of the default Novu Cloud endpoint.
  - Invokes the trigger API with `workflowId: "welcome-workflow"`, `to: { subscriberId: "sub_demo_1" }`, and `payload: { userName: "Alice" }`.
  - Writes the parsed JSON body returned by the SDK to `/home/user/app/result.json` (UTF-8 encoded JSON; pretty-printing is allowed but not required).
- The script must be runnable with `node trigger.js` from inside `/home/user/app`.

## Implementation Hints
- The npm package is `@novu/api`. Read its README on npm for the current constructor options and the shape of the `trigger` method.
- The SDK constructor accepts a `serverURL` option to override the default API host; use it when the verifier provides `NOVU_API_BASE_URL`.
- The `trigger` method returns an object whose `result` (or equivalent) field contains the parsed response body with fields like `acknowledged`, `status`, and `transactionId`. Inspect the SDK types so you know what to serialize.
- Use Node's built-in `fs` module to write the result file; no extra runtime dependencies are needed beyond `@novu/api`.

## Acceptance Criteria
- Project path: /home/user/app
- Command: node trigger.js (executed from /home/user/app)
- Required environment variables read by the script:
  - `NOVU_SECRET_KEY` (used as the SDK `secretKey`).
  - `NOVU_API_BASE_URL` (optional; when set, used as the SDK server URL override).
- Output artifact: `/home/user/app/result.json` containing the JSON body returned by the trigger call. The JSON document must include at least the fields `acknowledged` (boolean) and `transactionId` (string) returned by the server.
- `/home/user/app/package.json` must list `@novu/api` under `dependencies`, and `/home/user/app/node_modules/@novu/api` must exist after install.
- The script must complete with exit code 0 when the trigger call succeeds.

