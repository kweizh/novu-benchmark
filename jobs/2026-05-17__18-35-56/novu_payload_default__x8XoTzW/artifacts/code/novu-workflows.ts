import { workflow } from '@novu/framework';
import { z } from 'zod';

export const welcomeUser = workflow(
  'welcome-user',
  {
    payloadSchema: z.object({
      userName: z.string().default('Guest'),
    }),
  },
  async ({ step, payload }) => {
    await step.email(
      'send-email',
      async (inputs) => {
        return {
          subject: `Welcome, ${payload.userName}!`,
          body: 'Hello!',
        };
      }
    );
  }
);