# Novu Workflow with Dynamic Provider Override

## Background
You have a Next.js project with a Novu endpoint initialized at `/home/user/app`.
You need to implement a complex workflow that fetches a user's notification preferences from an external API and dynamically overrides the email provider configuration based on those preferences.

## Requirements
1. In `/home/user/app/app/api/novu/workflows.ts`, create and export a workflow named `dynamic-provider`.
2. The workflow must have a payload schema defined as `z.object({ orderId: z.string() })`.
3. The workflow must consist of two steps:
   - A custom step named `fetch-config` that makes an HTTP GET request to `http://localhost:4000/config?userId=${subscriber.subscriberId}` and returns the parsed JSON response.
   - An email step named `send-email`.
4. The external API returns a JSON object with this shape:
   ```ts
   {
     provider: 'sendgrid' | 'mailgun' | 'none',
     templateId: string,
     data: Record<string, any>
   }
   ```
5. The email step must be configured as follows:
   - `subject`: `"Order <orderId>"` (e.g., "Order ord_123")
   - `body`: `"Your order is processing."`
   - `providers`: Dynamically overridden based on the output of the `fetch-config` step.
     - If `provider` is `'sendgrid'`, override the `sendgrid` config with `templateId` and `dynamicTemplateData` (set to the `data` object).
     - If `provider` is `'mailgun'`, override the `mailgun` config with `template` (set to `templateId`) and `'h:X-Mailgun-Variables'` (set to `JSON.stringify(data)`).
     - If `provider` is `'none'` or missing, do not return any `providers` override.

## Constraints
- Project path: `/home/user/app`
- Start command: `npm run dev`
- Port: 3000
- You must use `@novu/framework` and `zod`.
- Do not use any external libraries for fetching data, use the native `fetch` API.