const express = require('express');
const { workflow, step } = require('@novu/framework');
const { serve } = require('@novu/framework/express');

const digestWorkflow = workflow('digest-workflow', async () => {
  const events = await step.digest('digest-events', {
    amount: 5,
    unit: 'minutes',
  });

  await step.email('send-email', {
    subject: 'Digest Summary',
    body: `You have ${events.length} new events`,
  });
});

const app = express();
app.use('/api/novu', serve({ workflows: [digestWorkflow] }));

app.listen(3000, () => {
  console.log('Novu workflow server listening on port 3000');
});
