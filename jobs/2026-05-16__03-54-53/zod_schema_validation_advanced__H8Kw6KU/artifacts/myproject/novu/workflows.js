const { workflow, step } = require('@novu/framework');
const { z } = require('zod');

/**
 * Zod payload schema for the welcome-user workflow.
 *
 * - userName: required string, defaults to 'New User'
 * - age:      optional number
 */
const payloadSchema = z.object({
  userName: z.string().default('New User'),
  age: z.number().optional(),
});

/**
 * welcome-user workflow
 *
 * Steps:
 *  1. notify-in-app  – sends an in-app notification
 *  2. send-email     – sends a welcome email
 */
const welcomeUserWorkflow = workflow(
  'welcome-user',
  async ({ step, payload }) => {
    // ── Step 1: In-App notification ─────────────────────────────────────
    await step.inApp('notify-in-app', async () => {
      return {
        subject: `Welcome, ${payload.userName}!`,
        body: payload.age
          ? `Hi ${payload.userName}, glad to have you here (age: ${payload.age}).`
          : `Hi ${payload.userName}, glad to have you here!`,
      };
    });

    // ── Step 2: Email notification ───────────────────────────────────────
    await step.email('send-email', async () => {
      return {
        subject: `Welcome to our platform, ${payload.userName}!`,
        body: `
          <h1>Hello, ${payload.userName}!</h1>
          <p>Thank you for joining us.${
            payload.age ? ` We see you are ${payload.age} years old.` : ''
          }</p>
          <p>We're excited to have you on board.</p>
        `,
      };
    });
  },
  {
    payloadSchema,
  }
);

module.exports = { welcomeUserWorkflow };
