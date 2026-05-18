const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const express = require('express');

const digestWorkflow = workflow('digest-workflow', async ({ step }) => {
  const events = await step.digest('digest-events', async () => {
    return {
      amount: 5,
      unit: 'minutes',
    };
  });

  await step.email('send-email', async () => {
    return {
      subject: 'Digest Summary',
      body: `You have ${events.length} new events`,
    };
  });
});

const app = express();
app.use(express.json());

app.use('/api/novu', serve({ workflows: [digestWorkflow] }));

app.listen(3000, () => {
  console.log('Server started on port 3000');
});
