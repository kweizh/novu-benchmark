const express = require('express');
const { workflow, Client } = require('@novu/framework');
const { serve } = require('@novu/framework/express');

const novuSecretKey = process.env.NOVU_SECRET_KEY;

if (!novuSecretKey) {
  throw new Error('NOVU_SECRET_KEY environment variable is required');
}

const novuClient = new Client({
  secretKey: novuSecretKey,
  strictAuthentication: true,
});

const testWorkflow = workflow('test-workflow', async ({ step }) => {
  await step.email('send-test-email', async () => ({
    subject: 'Test Workflow Email',
    body: 'This email was sent from the test-workflow in Novu Framework.',
  }));
});

const app = express();
app.use(express.json());

app.use('/api/novu', serve({
  client: novuClient,
  workflows: [testWorkflow],
}));

const port = 3000;
app.listen(port, () => {
  console.log(`Novu Bridge listening on port ${port}`);
});
