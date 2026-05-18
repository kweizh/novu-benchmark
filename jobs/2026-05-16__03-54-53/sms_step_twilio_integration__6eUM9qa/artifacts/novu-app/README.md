# Novu SMS Workflow Integration

## Project: novu-app (Next.js + @novu/framework)

### Project Location
`/home/user/novu-app`

### Start Command
```bash
cd /home/user/novu-app
npm run dev
```

### Bridge Endpoint
`http://localhost:3000/api/novu`

### Workflow: `sms-alert`
- **Step**: `send-sms` (SMS step)
- **Payload**: `{ message: string }` (validated via zod)
- **SMS Body**: The `message` field from the payload

### Files Created
- `app/api/novu/workflows.ts` — defines the `smsAlert` workflow
- `app/api/novu/route.ts` — exposes the Bridge Endpoint via `serve()`

### Dependencies Installed
- `@novu/framework`
- `zod`
- `zod-to-json-schema` (required peer dependency of @novu/framework)

### Verified Endpoint Response
```json
{"status":"ok","sdkVersion":"2.10.0","frameworkVersion":"2024-06-26","discovered":{"workflows":1,"steps":1}}
```
