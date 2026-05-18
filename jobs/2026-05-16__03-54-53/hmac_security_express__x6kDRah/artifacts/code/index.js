'use strict';

const express = require('express');
const { workflow, Client } = require('@novu/framework');
const { serve } = require('@novu/framework/express');

// Initialize the Novu client with the secret key for HMAC verification
const client = new Client({
  secretKey: process.env.NOVU_SECRET_KEY,
});

// Define the test-workflow that sends an email
const testWorkflow = workflow('test-workflow', async ({ step, payload }) => {
  await step.email('send-email', async (controls) => {
    return {
      subject: controls.subject || 'Hello from Novu',
      body: controls.body || `<p>This is a test email sent via Novu Framework.</p>`,
    };
  });
});

// Set up the Express application
const app = express();

// Mount the Novu Bridge Endpoint at /api/novu
// The serve() helper handles GET (discovery) and POST (execution/trigger) requests
// In production (NODE_ENV=production), HMAC signature verification is enforced automatically
app.use(
  '/api/novu',
  serve({
    client,
    workflows: [testWorkflow],
  })
);

// Start the server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Novu Bridge server running on port ${PORT}`);
  console.log(`Bridge endpoint: http://localhost:${PORT}/api/novu`);
  console.log(`Environment: ${process.env.NODE_ENV}`);
  console.log(
    `HMAC verification: ${process.env.NODE_ENV === 'production' ? 'ENABLED' : 'disabled'}`
  );
});
