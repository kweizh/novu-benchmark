# Novu Workflow with Zod Validation

## Project Overview

This project demonstrates a multi-channel Novu workflow that sends both email and in-app notifications, using Zod for payload validation.

## Project Structure

```
/home/user/myproject/
├── index.js              # Express server with Novu Bridge Endpoint
├── novu/
│   └── workflows.js      # Novu workflow definitions
├── node_modules/         # Project dependencies
└── package.json          # Project configuration
```

## Files Created

### 1. `/home/user/myproject/package.json`
- Standard Node.js package.json
- Dependencies: `express`, `@novu/framework`, `zod`, `zod-to-json-schema`

### 2. `/home/user/myproject/novu/workflows.js`
- Exports the `welcomeUser` workflow
- Uses Zod schema for payload validation with:
  - `userName`: string (required, default: 'New User')
  - `age`: number (optional)
- Contains two steps:
  - `notify-in-app`: In-app notification step
  - `send-email`: Email notification step

### 3. `/home/user/myproject/index.js`
- Express server running on port 3000
- Exposes Novu Bridge Endpoint at `/api/novu`
- Integrates the `welcomeUser` workflow

## How to Run

Start the server:
```bash
cd /home/user/myproject
node index.js
```

The server will start on port 3000 and the Novu Bridge Endpoint will be available at `http://localhost:3000/api/novu`.

## Workflow Details

### welcome-user Workflow
- **Name**: `welcome-user`
- **Validation**: Uses Zod schema to validate payload
- **Steps**:
  1. **notify-in-app**: Sends an in-app notification with welcome message
  2. **send-email**: Sends an email with welcome message

### Payload Schema
```javascript
{
  userName: string (default: 'New User'),
  age?: number
}
```

## Testing

To test the workflow, you can send a POST request to the Novu Bridge Endpoint with a valid payload.

Example payload:
```json
{
  "userName": "John Doe",
  "age": 30
}
```

Or with minimal payload (userName will default to 'New User'):
```json
{
  "age": 25
}
```

## Dependencies

- `express`: Web framework for Node.js
- `@novu/framework`: Novu framework for workflow management
- `zod`: TypeScript-first schema validation
- `zod-to-json-schema`: Converts Zod schemas to JSON schemas (required by Novu framework)

## Notes

- The server successfully starts and listens on port 3000
- The Novu Bridge Endpoint is properly configured at `/api/novu`
- Zod validation is integrated into the workflow
- Both in-app and email notification steps are defined