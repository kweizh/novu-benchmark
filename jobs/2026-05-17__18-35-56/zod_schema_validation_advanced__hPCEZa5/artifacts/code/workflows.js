const { workflow, step } = require('@novu/framework');
const { z } = require('zod');

// Define the Zod payload schema
const payloadSchema = z.object({
  userName: z.string().default('New User'),
  age: z.number().optional()
});

// Create the welcome-user workflow
const welcomeUser = workflow(
  'welcome-user',
  {
    payloadSchema
  },
  async (event) => {
    const { payload } = event;

    // Step 1: Send in-app notification
    await step.inApp(
      'notify-in-app',
      async () => {
        return {
          subject: `Welcome, ${payload.userName}!`,
          body: `Thanks for joining us${payload.age ? `. You're ${payload.age} years old!` : ''}.`,
          data: {
            userName: payload.userName,
            age: payload.age
          }
        };
      }
    );

    // Step 2: Send email
    await step.email(
      'send-email',
      async () => {
        return {
          subject: `Welcome to Our Platform, ${payload.userName}!`,
          body: `Hello ${payload.userName},\n\nWelcome to our platform!${payload.age ? `\n\nWe noticed you're ${payload.age} years old.` : ''}\n\nWe're excited to have you on board.\n\nBest regards,\nThe Team`,
          data: {
            userName: payload.userName,
            age: payload.age
          }
        };
      }
    );
  }
);

module.exports = { welcomeUser };