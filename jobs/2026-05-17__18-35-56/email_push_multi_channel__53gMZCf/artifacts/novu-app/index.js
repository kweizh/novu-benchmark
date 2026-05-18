const express = require('express');
const { workflow, serve } = require('@novu/framework/express');

// Create Express app
const app = express();

// Use express.json() middleware before Novu endpoint
app.use(express.json());

// Define the welcome-user workflow with multiple channels
const welcomeWorkflow = workflow('welcome-user', async ({ step }) => {
  // In-app notification step
  await step.inApp('notify-in-app', () => {
    return {
      title: 'Welcome to our platform!',
      body: 'We are excited to have you on board.',
    };
  });

  // Email notification step
  await step.email('send-email', () => {
    return {
      subject: 'Welcome to our platform!',
      body: 'Thank you for joining us. We are excited to have you on board!',
    };
  });
});

// Serve the workflow at /api/novu endpoint
app.use('/api/novu', serve(welcomeWorkflow));

// Start the server on port 3000
app.listen(3000, () => {
  console.log('Novu workflow server is running on port 3000');
  console.log('Workflow endpoint available at http://localhost:3000/api/novu');
});