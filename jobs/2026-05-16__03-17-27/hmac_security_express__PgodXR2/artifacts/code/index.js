const express = require('express');
const { serve } = require('@novu/framework/express');
const { workflow } = require('@novu/framework');

const app = express();
const port = 3000;

app.use(express.json());

const testWorkflow = workflow('test-workflow', async ({ step }) => {
  await step.email('send-email', async () => {
    return {
      subject: 'Test Email',
      body: 'This is a test email',
    };
  });
});

app.use('/api/novu', serve({
  workflows: [testWorkflow],
}));

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
