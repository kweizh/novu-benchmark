import { workflow } from '@novu/framework';
import { z } from 'zod';

export const welcomeUser = workflow(
  'welcome-user',
  async ({ step, payload }) => {
    await step.email(
      'send-email',
      async (controls) => {
        return {
          subject: `Welcome, ${payload.userName}!`,
          body: 'Hello'
        };
      }
    );
  },
  {
    payloadSchema: z.object({
      userName: z.string().default('Guest'),
    }),
  }
);
