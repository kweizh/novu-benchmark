# Novu Conditional Channel Routing — Artifacts

## Project Location
`/home/user/project`

## Start Command
```
node index.js
```

## Port
`3000`

## Bridge Endpoint
`GET/POST http://localhost:3000/api/novu`

## Workflow: `conditional-routing`

### Payload Schema (Zod)
| Field      | Type    | Description                          |
|------------|---------|--------------------------------------|
| `userName` | string  | Name of the notification recipient   |
| `critical` | boolean | Whether the notification is critical |

### Steps
| Step ID        | Type   | Behaviour                                        |
|----------------|--------|--------------------------------------------------|
| `notify-in-app`| inApp  | Always runs                                      |
| `send-email`   | email  | Skipped when `payload.critical === false`        |

## Health Check (confirmed working)
```json
{
  "status": "ok",
  "sdkVersion": "2.10.0",
  "frameworkVersion": "2024-06-26",
  "discovered": {
    "workflows": 1,
    "steps": 2
  }
}
```

## Files
- `code/index.js` — main application entry point
- `code/package.json` — Node.js project manifest
