# Novu Delay Workflow — Artifacts

## Project Location
`/home/user/myproject`

## Files
- `code/index.js` — Express app with Novu Bridge Endpoint at `/api/novu`
- `code/workflows.js` — Novu workflow definition (`follow-up-workflow`)
- `code/package.json` — Node.js project manifest

## Workflow Details
- **Workflow name**: `follow-up-workflow`
- **Step 1**: `reminder-delay` (type: `delay`) — pauses for 24 hours
- **Step 2**: `follow-up-email` (type: `email`) — subject: "How are you liking our product?"

## Running
```bash
cd /home/user/myproject
node index.js
# Server starts on port 3000
# Bridge endpoint: http://localhost:3000/api/novu
```

## Verified Output
```
Server is running on port 3000
Novu Bridge Endpoint available at http://localhost:3000/api/novu
Discovered workflowId: 'follow-up-workflow'
├ σ Discovered stepId: 'reminder-delay'    Type: 'delay'
└ σ Discovered stepId: 'follow-up-email'   Type: 'email'
```
