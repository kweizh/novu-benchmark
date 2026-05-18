const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const express = require('express');

const digestWorkflow = workflow('digest-workflow', async ({ step, payload }) => {
  const digest = await step.digest('digest-events', () => ({
    amount: 5,
    unit: 'minutes'
  }));

  await step.email('send-email', async () => {
    return {
      subject: 'Digest Summary',
      body: `You have ${digest.events.length} new events`
    };
  });
});

const app = express();

app.use(express.json());

app.use(
  '/api/novu',
  serve({
    workflows: [digestWorkflow]
  })
);

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
