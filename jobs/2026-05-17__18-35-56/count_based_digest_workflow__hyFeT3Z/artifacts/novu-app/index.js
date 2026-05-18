const { workflow, step, serve } = require('@novu/framework');
const express = require('express');

// Define the digest workflow
const digestWorkflow = workflow('digest-workflow', async (event) => {
  // Digest step to batch events for 5 minutes
  const digestedEvents = await step.digest('digest-events', {
    amount: 5,
    unit: 'minutes'
  }, event);

  // Email step to send summary with the count of digested events
  await step.email('send-email', {
    subject: 'Digest Summary',
    body: `You have ${digestedEvents.events.length} new events`
  });
});

// Create Express app
const app = express();

// Serve the workflow at /api/novu endpoint
serve(app, {
  workflows: [digestWorkflow]
});

// Start server on port 3000
app.listen(3000, () => {
  console.log('Novu digest workflow server running on port 3000');
  console.log('Workflow endpoint: http://localhost:3000/api/novu');
});