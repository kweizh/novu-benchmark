# Hono Bridge Endpoint for Novu Framework

## Background
Novu Framework lets you define notification workflows in code and expose them to the Novu Worker Engine through a single HTTP "Bridge Endpoint" (typically mounted at `/api/novu`). The Worker Engine then calls this endpoint to discover workflows and to resolve step content per subscriber. While Novu ships first-party `serve` adapters for several Node.js frameworks, you will build a Bridge Endpoint on top of the lightweight Hono web framework so that the Novu workflows are served from a Hono app running on Node.js.

## Requirements
- Create a Node.js project at `/home/user/app` that uses Hono together with `@novu/framework`.
- Define a workflow with workflow id `greet-hono` and a single email step with step id `welcome-email`.
  - The email step must produce a subject of exactly `Welcome via Hono`.
  - The email step must produce a body of exactly `Greetings from a Hono-powered Novu app.`.
- Expose the Novu Bridge Endpoint on the Hono app under the path `/api/novu`. The endpoint must respond to `GET`, `POST` and `OPTIONS` requests as the Novu Framework expects, and the `GET` request must return the discover payload that lists the `greet-hono` workflow and its `welcome-email` email step.
- Start the Hono app on Node.js using `@hono/node-server` and listen on port `3000`.
- Do not mock `@novu/framework` or `hono`; the real packages must be installed and used.

## Implementation Hints
- Use the `workflow` factory from `@novu/framework` to declare the `greet-hono` workflow and the `step.email` channel to declare the `welcome-email` step.
- The Novu Framework package exports the low-level `NovuRequestHandler` from `@novu/framework`. The Novu docs include a reference example of writing a custom `serve` function for any framework on top of `NovuRequestHandler`; you can adapt that pattern to plug Novu into a Hono route, because Hono passes Web-standard `Request` objects to its handlers.
- Alternatively, you may delegate to one of the existing first-party adapters that exposes Web-standard `Request`/`Response` handlers (such as the one shipped under `@novu/framework`'s SvelteKit/Remix builds) as long as the resulting `GET /api/novu` response is the standard Novu discover payload.
- Wire the Hono app to Node.js via `serve` from `@hono/node-server` listening on port `3000`.
- Make sure the Novu Bridge Endpoint runs in `development` mode so that it does not require a signed HMAC header for requests in this local test environment. The official Novu client supports this via a `strictAuthentication: false` style configuration.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: npm start
- Port: 3000
- The HTTP server must be a Hono app served by `@hono/node-server`.
- API Endpoints:
  - `GET /api/novu`: Returns status 200 and a JSON body that is the Novu Bridge discover payload. The payload must contain a `workflows` array (or be otherwise traversable so that the discover result for the workflow can be located), and within it there must be an entry whose workflow id is `greet-hono` containing at least one step whose step id is `welcome-email` and whose channel/type is `email`.
  - `POST /api/novu` with the standard Novu `execute` body for the `welcome-email` step of the `greet-hono` workflow must return status 200 and an `outputs` (or equivalent) object whose `subject` equals `Welcome via Hono` and whose `body` equals `Greetings from a Hono-powered Novu app.`.

