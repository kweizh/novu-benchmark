const { workflow } = require('@novu/framework');
const { z } = require('zod');

module.exports.welcomeUser = workflow(
  'welcome-user',
  async ({ step, payload }) => {
    await step.inApp(
      'notify-in-app',
      async () => {
        return {
          body: `Welcome ${payload.userName}!`,
        };
      }
    );

    await step.email(
      'send-email',
      async () => {
        return {
          subject: 'Welcome to our platform',
          body: `Hello ${payload.userName}, welcome aboard!`,
        };
      }
    );
  },
  {
    payloadSchema: z.object({
      userName: z.string().default('New User'),
      age: z.number().optional(),
    }),
  }
);
