# Novu Digest Workflow Application

A notification workflow application using `@novu/framework` that aggregates multiple events using a time-based digest step before sending an email.

## Features

- **Workflow Name**: `digest-workflow`
- **Digest Step**: `digest-events` - batches events for 5 minutes
- **Email Step**: `send-email` - sends a summary email with the count of digested events

## Setup

```bash
cd /home/user/novu-app
npm install
```

## Running the Application

```bash
node index.js
```

The server will start on port 3000 at the `/api/novu` endpoint.

## Workflow Details

1. Events are triggered to the `digest-workflow`
2. The `digest-events` step batches events for 5 minutes
3. After the digest window, the `send-email` step sends an email with:
   - Subject: "Digest Summary"
   - Body: "You have ${events.length} new events"

## Project Structure

```
/home/user/novu-app/
├── package.json
└── index.js
```

## Dependencies

- `@novu/framework` - Workflow orchestration
- `express` - Web server

## API Endpoint

- `POST http://localhost:3000/api/novu` - Trigger the digest workflow