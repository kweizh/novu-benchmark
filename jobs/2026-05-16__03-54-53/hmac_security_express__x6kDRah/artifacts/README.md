# Novu Bridge Endpoint – Secure Express.js App

## Project Location
`/home/user/app`

## Files
| File | Description |
|------|-------------|
| `index.js` | Main application: Express server + Novu workflow + Bridge endpoint |
| `package.json` | Project manifest with `npm start` configured for production |

## Start Command
```bash
# Requires NOVU_SECRET_KEY in the environment
NOVU_SECRET_KEY=<your-key> npm start
```
`npm start` runs `NODE_ENV=production node index.js`, which:
- Starts Express on **port 3000**
- Mounts the Novu Bridge Endpoint at **`/api/novu`**
- Enforces **HMAC signature verification** (production mode)

## Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/novu` | Novu Cloud discovery (lists registered workflows) |
| `POST` | `/api/novu` | Trigger / execute workflow steps (HMAC-verified) |

## Workflow
- **ID**: `test-workflow`  
- **Step**: `send-email` (email step that returns subject + body)

## Security
In `production` mode the `@novu/framework` SDK validates every inbound request using an HMAC-SHA-256 signature computed with `NOVU_SECRET_KEY`. Requests without a valid `novu-signature` header receive a `400` response.
