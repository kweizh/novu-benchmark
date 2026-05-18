const express = require('express');
const { workflow, serve } = require('@novu/framework/express');

// Define the test-workflow workflow
const testWorkflow = workflow('test-workflow', async ({ step, payload }) => {
  await step.email('send-email', async () => {
    return {
      subject: 'Test Email from Novu Workflow',
      body: 'This is a test email sent from the Novu workflow.',
      to: payload.recipientEmail || 'test@example.com',
    };
  });
});

// Create Express app
const app = express();

// Get Novu secret key from environment
const NOVU_SECRET_KEY = process.env.NOVU_SECRET_KEY;

// Configure Novu serve middleware with HMAC verification
// In production mode (NODE_ENV=production), HMAC verification is enforced by default
app.use(
  '/api/novu',
  serve({
    workflows: [testWorkflow],
    apiKey: NOVU_SECRET_KEY,
  })
);

// Start server on port 3000
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Novu Bridge Endpoint server running on port ${PORT}`);
  console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`Novu Bridge Endpoint available at http://localhost:${PORT}/api/novu`);
});