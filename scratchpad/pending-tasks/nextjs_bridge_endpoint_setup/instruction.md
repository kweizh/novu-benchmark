# Novu Bridge Endpoint in Next.js (App Router)

## Background
Novu Framework lets you define notification workflows in code and expose them through a single HTTP endpoint called a Bridge Endpoint. Novu Cloud calls this endpoint to discover and execute workflows. In this task you will scaffold a Next.js application that exposes a Novu Bridge Endpoint at `/api/novu` using the App Router and the `serve` helper from `@novu/framework/next`.

## Requirements
- Initialize a Next.js (App Router, TypeScript) project at `/home/user/app`.
- Add `@novu/framework` as a dependency.
- Create a workflow file that defines exactly one workflow with the workflow id `hello-world`. The workflow must contain a single In-App step whose `body` is exactly `Hello from Next.js`.
- Create the Bridge route at `app/api/novu/route.ts` using the `serve` function imported from `@novu/framework/next`, registering the `hello-world` workflow.
- The route must export named `GET`, `POST`, and `OPTIONS` handlers backed by `serve(...)`.
- The app must start on port 3000 with `npm run dev` and respond to the Novu discovery request at `GET /api/novu?action=discover`.

## Implementation Hints
- Use `create-next-app` (or set up `package.json` manually) with the App Router enabled and TypeScript.
- Use the `workflow` factory from `@novu/framework` to declare the workflow, and `step.inApp(...)` to add the in-app step. See https://docs.novu.co/framework/typescript/workflow and https://docs.novu.co/framework/in-app-channel.
- The `serve` helper from `@novu/framework/next` returns an object that exposes HTTP method handlers. You can spread or destructure it to re-export `GET`, `POST`, and `OPTIONS` for a Next.js Route Handler. See https://docs.novu.co/framework/quickstart/nextjs and https://docs.novu.co/framework/endpoint.
- The Novu discovery response is a JSON object containing a `workflows` array. Each workflow entry has a `workflowId` and a `steps` array, where each step has a `stepId` and a `type` (e.g. `in_app`).

## Acceptance Criteria
- Project path: /home/user/app
- Start command: npm run dev
- Port: 3000
- The Next.js app uses the App Router. A file exists at `/home/user/app/app/api/novu/route.ts`.
- The route handler exports the named exports `GET`, `POST`, and `OPTIONS`, all created from the `serve` function of `@novu/framework/next`.
- `package.json` lists `next` and `@novu/framework` as dependencies.
- API behavior:
  - `GET /api/novu?action=discover` returns HTTP 200 with a JSON response body that conforms to the following shape:
    ```json
    {
      "workflows": [
        {
          "workflowId": "hello-world",
          "steps": [
            { "stepId": string, "type": "in_app" }
          ]
        }
      ]
    }
    ```
  - Exactly one workflow with `workflowId` equal to `hello-world` must be present.
  - That workflow must contain at least one step whose `type` is `in_app`.
  - When the in-app step is previewed (e.g. via `POST /api/novu?action=preview` with the workflow and step ids), the resolved `body` output must be exactly the string `Hello from Next.js`.

