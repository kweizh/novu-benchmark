import { workflow } from '@novu/framework';
import { z } from 'zod';

export const welcomeUser = workflow('welcome-user', {
  payloadSchema: z.object({
    userName: z.string().default('Guest'),
  }),
  steps: [
    {
      name: 'send-email',
      type: 'email',
      inputs: {
        subject: ({ payload }) => `Welcome, ${payload.userName}!`,
      },
    },
  ],
});
