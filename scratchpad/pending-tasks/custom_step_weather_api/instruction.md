# Novu Custom Step Calling a Weather API

## Background
Novu's `step.custom` lets you run arbitrary asynchronous code inside a workflow, persist its return value, and reference that value from later steps. Build a small Express service that exposes both a mock weather API and a Novu Bridge Endpoint. The workflow first calls the mock weather API from inside a custom step, then uses the parsed JSON to compose an email subject and body.

## Requirements
- Implement an Express application that serves two things on port 3000:
  - A mock weather endpoint at `GET /api/weather?city=<city>` that always returns:
    `{ "city": "<city>", "tempC": 22, "conditions": "Sunny" }` (status 200, `Content-Type: application/json`).
  - A Novu Bridge Endpoint mounted at `/api/novu` using `@novu/framework/express`.
- Define a workflow with workflow id `weather-update` using `@novu/framework` whose `payloadSchema` is a Zod schema requiring `city: string`.
- The workflow must have two steps, in this order:
  1. `fetch-weather` — a `step.custom` step that uses native `fetch` to call `http://localhost:3000/api/weather?city=${payload.city}`, parses the JSON, and returns it. The step must declare an `outputSchema` (Zod) describing `city: string`, `tempC: number`, `conditions: string`.
  2. `weather-email` — a `step.email` step whose `subject` and `body` reference the previous step's outputs using template syntax. The subject must be `Weather for {{ steps['fetch-weather'].outputs.city }}` and the body must be `It's {{ steps['fetch-weather'].outputs.tempC }}°C and {{ steps['fetch-weather'].outputs.conditions }}.`.

## Implementation Hints
- Use `@novu/framework` to declare the workflow and `serve` from `@novu/framework/express` to expose the bridge router at `/api/novu`.
- Use `zod` for both `payloadSchema` and the custom step's `outputSchema`.
- Mount the mock weather route on the same Express app before the bridge mount, and start listening on port 3000.
- The custom step's resolver should be an `async` function that performs the HTTP fetch and returns the parsed body unchanged.
- The email step's resolver must return `{ subject, body }` with the exact template strings shown above so Novu's templating engine can interpolate the prior step's outputs.
- Set `NOVU_STRICT_AUTHENTICATION_ENABLED=false` in the runtime environment so the bridge accepts unauthenticated `discover` and `execute` calls. Do not invent or send any signing keys.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- API Endpoints:
  - GET `/api/weather?city=<city>`: Returns status 200 and a JSON object.

    ```json
    // Response
    {
      "city": string,
      "tempC": number,
      "conditions": string
    }
    ```

  - GET `/api/novu?action=discover`: Returns 200 and a discover payload listing the `weather-update` workflow and its `fetch-weather` and `weather-email` steps.
  - POST `/api/novu?action=execute&workflowId=weather-update&stepId=fetch-weather`: Executes the custom step against the local mock weather endpoint and returns its outputs.
  - POST `/api/novu?action=execute&workflowId=weather-update&stepId=weather-email`: When provided with the prior step's state, returns the rendered email `subject` and `body` with the fetched weather data interpolated.

