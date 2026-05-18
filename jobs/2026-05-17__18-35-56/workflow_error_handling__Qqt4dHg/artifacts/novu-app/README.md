# Novu Workflow Error Handling

## Overview
This project implements a Novu workflow with error handling capabilities using Express.js, the @novu/framework, and Zod for payload validation.

## Workflow: error-handling-workflow

### Payload Schema
The workflow validates payloads using Zod with the following schema:
- `userId` (string, required): The user identifier
- `simulateError` (boolean, optional, default: false): Flag to trigger error simulation

### Steps

#### 1. fetch-data (Custom Step)
- **Type**: Custom step
- **Behavior**:
  - If `payload.simulateError` is `true`, throws an Error with message "External API Failed"
  - If `payload.simulateError` is `false`, returns `{ status: "ok" }`

#### 2. send-email (Email Step)
- **Type**: Email step
- **Subject**: "Process Complete"
- **Body**: Includes the status from the fetch-data step

## Project Structure
```
/home/user/novu-app/
├── index.js          # Main application file with workflow definition
└── package.json      # Project dependencies and scripts
```

## Installation
```bash
cd /home/user/novu-app
npm install
```

## Dependencies
- `express`: ^5.2.1
- `@novu/framework`: ^2.10.0
- `zod`: ^4.4.3
- `zod-to-json-schema`: (installed as peer dependency)

## Running the Application
```bash
node index.js
```

Or using npm:
```bash
npm start
```

## Server Configuration
- **Port**: 3000
- **Novu Bridge Endpoint**: `http://localhost:3000/api/novu`

## Usage Examples

### Successful Workflow (no error)
```bash
POST /api/novu
{
  "userId": "user123",
  "simulateError": false
}
```

### Error Workflow (simulated error)
```bash
POST /api/novu
{
  "userId": "user123",
  "simulateError": true
}
```

## Key Features
1. **Zod Payload Validation**: Ensures data integrity with schema validation
2. **Custom Error Handling**: Demonstrates error propagation in custom steps
3. **Express Integration**: Seamless integration with Express.js framework
4. **Novu Bridge**: Provides REST API endpoint for workflow execution

## Notes
- The server runs in the background and can be monitored
- Error messages from custom steps are properly surfaced to the caller
- The workflow demonstrates proper error handling patterns in Novu workflows