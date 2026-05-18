# Novu Workflow Error Handling App

## Overview
An Express.js application that serves a Novu Bridge endpoint implementing an `error-handling-workflow` with payload validation and custom step error surfacing.

## Project Structure
- `index.js` — Main application file (workflow definition + Express server)
- `package.json` — Node.js project manifest

## Setup & Run
```bash
cd /home/user/novu-app
npm install
node index.js
```
Server listens on **port 3000** at `http://localhost:3000/api/novu`.

## Workflow: `error-handling-workflow`

### Payload Schema (Zod)
| Field          | Type    | Required | Default |
|----------------|---------|----------|---------|
| `userId`       | string  | Yes      | —       |
| `simulateError`| boolean | No       | `false` |

### Steps
1. **`fetch-data`** (custom step)
   - If `payload.simulateError === true` → throws `Error("External API Failed")`
   - If `payload.simulateError === false` → returns `{ status: "ok" }`

2. **`send-email`** (email step)
   - Subject: `"Process Complete"`
   - Body: `"The fetch-data step completed with status: <status>"`

## Health Check
```bash
curl http://localhost:3000/api/novu/health
# → {"status":"ok","sdkVersion":"2.10.0","frameworkVersion":"2024-06-26","discovered":{"workflows":1,"steps":2}}
```

## Dependencies
- `express` — HTTP server
- `@novu/framework` v2.10.0 — Novu Bridge framework
- `zod` — Schema validation
- `zod-to-json-schema` — Peer dependency for Zod schema conversion
