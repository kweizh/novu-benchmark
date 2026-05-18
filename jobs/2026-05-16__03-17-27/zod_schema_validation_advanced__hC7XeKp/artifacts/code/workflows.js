const { workflow } = require('@novu/framework');
const { z } = require('zod');

const welcomeUser = workflow('welcome-user', async ({ step, payload }) => {
  await step.inApp('notify-in-app', async () => {
    return {
      body: `Welcome to the app, ${payload.userName}!`
    };
  });

  await step.email('send-email', async () => {
    return {
      subject: `Welcome, ${payload.userName}!`,
      body: `Hello ${payload.userName}, welcome to our platform.`
    };
  });
}, {
  payloadSchema: z.object({
    userName: z.string().default('New User'),
    age: z.number().optional()
  })
});

module.exports = { welcomeUser };
