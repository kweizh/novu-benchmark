import { workflow } from '@novu/framework';
import { z } from 'zod/v3';

export const welcomeUser = workflow(
  'welcome-user',
  async ({ step, payload }) => {
    await step.email('send-email', async () => {
      return {
        subject: `Welcome, ${payload.userName}!`,
        body: `<p>Hello, ${payload.userName}! Welcome aboard.</p>`,
      };
    });
  },
  {
    payloadSchema: z.object({
      userName: z.string().default('Guest'),
    }),
  }
);
