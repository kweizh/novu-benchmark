const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');

// Define the welcome-user workflow with in-app and email channels
const welcomeUserWorkflow = workflow('welcome-user', async ({ step, payload }) => {
  // In-app notification step
  await step.inApp('notify-in-app', async () => {
    return {
      subject: 'Welcome to our platform!',
      body: `Hello! You have a new in-app notification.`,
    };
  });

  // Email notification step
  await step.email('send-email', async () => {
    return {
      subject: 'Welcome! Getting started guide',
      body: `
        <h1>Welcome!</h1>
        <p>Thank you for joining our platform. We are excited to have you on board.</p>
        <p>Get started by exploring our features.</p>
      `,
    };
  });
});

// Set up Express application
const app = express();

// Apply JSON middleware before Novu endpoint
app.use(express.json());

// Mount Novu workflow handler at /api/novu
app.use('/api/novu', serve({ workflows: [welcomeUserWorkflow] }));

// Start server on port 3000
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Novu Express app listening on port ${PORT}`);
  console.log(`Novu endpoint available at http://localhost:${PORT}/api/novu`);
});
