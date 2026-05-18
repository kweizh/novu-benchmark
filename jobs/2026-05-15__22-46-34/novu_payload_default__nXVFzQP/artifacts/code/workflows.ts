import { workflow } from '@novu/framework';
import { z } from 'zod';

export const welcomeUser = workflow(
  'welcome-user',
  async ({ step, payload }) => {
    await step.email('send-email', async () => {
      return {
        subject: `Welcome, ${payload.userName}!`,
        body: `Hello ${payload.userName}, welcome to our platform!`,
      };
    });
  },
  {
    payloadSchema: z.object({
      userName: z.string().default('Guest'),
    }),
  }
);
