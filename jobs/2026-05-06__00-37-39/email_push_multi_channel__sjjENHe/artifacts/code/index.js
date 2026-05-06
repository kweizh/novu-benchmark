const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');

const app = express();

// Use express.json() middleware before the Novu endpoint
app.use(express.json());

const welcomeUserWorkflow = workflow('welcome-user', async ({ step, payload }) => {
  await step.inApp('notify-in-app', async () => {
    return {
      body: `Welcome to the app!`,
    };
  });

  await step.email('send-email', async () => {
    return {
      subject: 'Welcome to our platform',
      body: `Hello, we are glad to have you!`,
    };
  });
});

// Serve the workflow at the /api/novu endpoint
app.use('/api/novu', serve({ workflows: [welcomeUserWorkflow] }));

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
