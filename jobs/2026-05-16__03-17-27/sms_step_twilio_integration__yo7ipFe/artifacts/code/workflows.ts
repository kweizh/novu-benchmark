import { workflow } from '@novu/framework';
import { z } from 'zod';

export const smsAlert = workflow(
  'sms-alert',
  async ({ step, payload }) => {
    await step.sms('send-sms', async () => {
      return {
        body: payload.message,
      };
    });
  },
  {
    payloadSchema: z.object({
      message: z.string(),
    }),
  }
);
