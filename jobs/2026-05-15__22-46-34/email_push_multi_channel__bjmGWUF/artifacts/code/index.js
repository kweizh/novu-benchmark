const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');

const app = express();
app.use(express.json());

const welcomeUser = workflow('welcome-user', async ({ step }) => {
  await step.inApp('notify-in-app', async () => {
    return {
      body: 'Welcome to our app!',
    };
  });

  await step.email('send-email', async () => {
    return {
      subject: 'Welcome!',
      body: 'We are glad to have you here.',
    };
  });
});

app.use('/api/novu', serve({ workflows: [welcomeUser] }));

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
