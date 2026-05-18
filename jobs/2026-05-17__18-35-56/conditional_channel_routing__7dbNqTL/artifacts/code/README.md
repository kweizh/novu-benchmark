# Novu Conditional Channel Routing

This project demonstrates conditional channel routing using the Novu Framework with Express.

## Setup

```bash
cd /home/user/project
npm install
node index.js
```

## Workflow: `conditional-routing`

The workflow accepts a payload with:
- `userName` (string): The name of the user
- `critical` (boolean): Whether the notification is critical

### Steps

1. **notify-in-app** (inApp): Always runs, sends an in-app notification to the user
2. **send-email** (email): Only runs if `payload.critical` is true

## API Endpoint

The Novu Bridge is available at: `http://localhost:3000/api/novu`

## Usage

To trigger the workflow, send a POST request to the Novu Bridge endpoint with the workflow identifier and payload.

Example payload:
```json
{
  "workflowId": "conditional-routing",
  "payload": {
    "userName": "John Doe",
    "critical": true
  }
}
```

When `critical` is `false`, the email step will be skipped and only the in-app notification will be sent.