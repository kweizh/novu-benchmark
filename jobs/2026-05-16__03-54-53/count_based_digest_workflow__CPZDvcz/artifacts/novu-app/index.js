const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');

// Define the digest workflow
const digestWorkflow = workflow('digest-workflow', async ({ step }) => {
  // Digest step: batch events for 5 minutes
  const digestResult = await step.digest('digest-events', async () => {
    return {
      amount: 5,
      unit: 'minutes',
    };
  });

  // Email step: send a summary with the number of digested events
  await step.email('send-email', async (controls) => {
    const events = digestResult.events || [];
    return {
      subject: 'Digest Summary',
      body: `You have ${events.length} new events`,
    };
  });
});

// Set up Express app
const app = express();

// Mount the Novu workflow handler at /api/novu
const novuHandler = serve({ workflows: [digestWorkflow] });
app.use('/api/novu', novuHandler);

// Start server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Novu digest workflow server running on port ${PORT}`);
  console.log(`Workflow endpoint: http://localhost:${PORT}/api/novu`);
});
