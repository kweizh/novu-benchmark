# Novu Workflow: HTML Email Body with Liquid Templating

## Background
You are using the [Novu Framework](https://docs.novu.co/framework) (TypeScript SDK `@novu/framework`) to build a transactional notification workflow that sends an order confirmation email. The email subject and body must include HTML and use Novu's built-in Liquid templating syntax (e.g. `{{ payload.orderId }}`) so that Novu Cloud can interpolate payload variables when the workflow is actually delivered. The Bridge Endpoint that hosts the workflow must be served by Express on port 3000 at `/api/novu`.

## Requirements
- Create a Node.js project that uses `@novu/framework` together with `express` and `zod`.
- Define a single workflow with the workflow id `order-confirmation`.
- The workflow must contain exactly one channel step: an `email` step whose `stepId` is `order-email`.
  - The step `subject` must be the literal Liquid template string `Order #{{ payload.orderId }} confirmed`.
  - The step `body` must be the literal Liquid + HTML template string `<h1>Thanks {{ payload.customerName }}!</h1><p>Your order #{{ payload.orderId }} totalling ${{ payload.amount }} is confirmed.</p>` (an HTML body, not plain text).
  - The HTML in the rendered output must not be stripped by the framework's output sanitizer.
- The workflow `payloadSchema` must be defined with **Zod** and must require three fields:
  - `orderId`: string
  - `customerName`: string
  - `amount`: number
- Expose the Novu Bridge Endpoint at `POST/GET/OPTIONS /api/novu` using the Express adapter (`serve` from `@novu/framework/express`).
- The server must listen on port `3000`.
- The server must be startable with `node index.js` from the project root.

## Implementation Hints
- Install `@novu/framework`, `express`, and `zod`.
- Use the `workflow(workflowId, handler, options)` factory and pass a Zod schema via `options.payloadSchema`.
- Inside the step resolver, return an object with `subject` and `body` fields whose values are the Liquid/HTML template strings exactly as specified. Do **not** interpolate the values with JavaScript template literals — the placeholders are Liquid expressions that Novu renders at delivery time.
- The email step's output is HTML-sanitized by default. Use the channel step's options to disable sanitization (e.g. `{ disableOutputSanitization: true }`) so that the HTML tags and Liquid braces in the body are preserved verbatim when the bridge returns the executed output.
- Mount the Novu handler with `app.use('/api/novu', serve({ workflows: [...] }))` and remember `app.use(express.json())` is required for POST requests.
- Do NOT enable strict HMAC authentication; leave `NOVU_SECRET_KEY` unset and run the server in development mode so the bridge accepts unsigned requests (this is the default behavior when `NODE_ENV` is `development` or unset).
- No mocks: the workflow must be a real `@novu/framework` workflow served through the real Express adapter.

## Acceptance Criteria
- Project path: /home/user/app
- Start command: node index.js
- Port: 3000
- API Endpoints exposed by the Novu Bridge:
  - `GET /api/novu?action=discover` returns status 200 with a JSON body of the shape:
    ```json
    {
      "workflows": [
        {
          "workflowId": "order-confirmation",
          "steps": [
            { "stepId": "order-email", "type": "email" }
          ]
        }
      ]
    }
    ```
    The `workflows` array must contain an entry whose `workflowId` is `order-confirmation` and whose `steps` array contains a step with `stepId` `order-email` and `type` `email`.
  - `POST /api/novu?action=execute&workflowId=order-confirmation&stepId=order-email` accepts a JSON body of the form:
    ```json
    {
      "payload": { "orderId": "ORD-1", "customerName": "Alice", "amount": 42 },
      "subscriber": { "subscriberId": "sub_test" },
      "state": [],
      "inputs": {},
      "controls": {}
    }
    ```
    and returns status 200 with a JSON response whose `outputs` object contains:
    - `outputs.subject` equal to the literal string `Order #{{ payload.orderId }} confirmed`
    - `outputs.body` equal to the literal string `<h1>Thanks {{ payload.customerName }}!</h1><p>Your order #{{ payload.orderId }} totalling ${{ payload.amount }} is confirmed.</p>`
  - `POST /api/novu?action=execute&workflowId=order-confirmation&stepId=order-email` with a payload that is missing required fields (e.g. `{}`) must return a non-2xx response (Zod validation must reject it).

