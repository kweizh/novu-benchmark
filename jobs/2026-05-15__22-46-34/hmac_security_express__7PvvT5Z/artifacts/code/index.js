const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');

const app = express();
app.use(express.json());

const testWorkflow = workflow('test-workflow', async ({ step }) => {
  await step.email('send-email', async (inputs) => {
    return {
      subject: 'Test Email',
      body: 'This is a test email from Novu Framework',
    };
  });
});

app.use(
  '/api/novu',
  serve({
    workflows: [testWorkflow],
  })
);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
