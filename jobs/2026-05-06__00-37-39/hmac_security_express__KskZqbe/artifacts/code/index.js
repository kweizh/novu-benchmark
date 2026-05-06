const express = require('express');
const { serve } = require('@novu/framework/express');
const { workflow } = require('@novu/framework');

const app = express();
app.use(express.json());

const testWorkflow = workflow('test-workflow', async ({ step }) => {
  await step.email('send-email', async (inputs) => {
    return {
      subject: 'Test Email',
      body: 'This is a test email from Novu Bridge Endpoint',
    };
  });
});

app.use(
  '/api/novu',
  serve({
    workflows: [testWorkflow],
    apiKey: process.env.NOVU_SECRET_KEY,
  })
);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server started on port ${PORT}`);
});
