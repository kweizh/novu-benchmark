# Novu Express Bridge Setup

## Background
Set up a Novu Bridge Endpoint in an Express.js application to connect your code to Novu Cloud.

## Requirements
- Initialize a Node.js project in `/home/user/myproject`.
- Install `express` and `@novu/framework`.
- Create a workflow file `workflows.js` that defines a workflow named `test-workflow` which sends an email with the subject 'Test Email' and body 'This is a test email from Novu Framework!'.
- Create an `index.js` file that sets up an Express server on port 3000.
- Configure the server to parse JSON (`express.json()`) and mount the Novu Bridge Endpoint at `/api/novu` using the `serve` function from `@novu/framework/express`, passing the `test-workflow`.

## Implementation Guide
1. Run `npm init -y` in `/home/user/myproject`.
2. Run `npm install express @novu/framework`.
3. Create `workflows.js`:
```javascript
const { workflow } = require('@novu/framework');

const testWorkflow = workflow('test-workflow', async ({ step }) => {
  await step.email('test-email', async () => {
    return {
      subject: 'Test Email',
      body: 'This is a test email from Novu Framework!',
    };
  });
});

module.exports = { testWorkflow };
```
4. Create `index.js`:
```javascript
const express = require('express');
const { serve } = require('@novu/framework/express');
const { testWorkflow } = require('./workflows');

const app = express();
app.use(express.json());
app.use('/api/novu', serve({ workflows: [testWorkflow] }));

app.listen(3000, () => console.log('Listening on port 3000'));
```

## Constraints
- Project path: `/home/user/myproject`
- Start command: `node index.js`
- Port: 3000
- Do not use TypeScript, use plain JavaScript (CommonJS) as shown in the guide.