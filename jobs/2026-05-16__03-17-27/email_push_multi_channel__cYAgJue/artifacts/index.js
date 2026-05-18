const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');

const app = express();

app.use(express.json());

const welcomeUser = workflow('welcome-user', async (step) => {
  await step.inApp('notify-in-app', async () => {
    return {
      body: 'Welcome to our platform!'
    };
  });

  await step.email('send-email', async () => {
    return {
      subject: 'Welcome!',
      body: 'Welcome to our platform!'
    };
  });
});

app.use(
  '/api/novu',
  serve({
    workflows: [welcomeUser]
  })
);

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
