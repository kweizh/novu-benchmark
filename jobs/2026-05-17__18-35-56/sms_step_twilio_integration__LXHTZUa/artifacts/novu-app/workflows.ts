import { workflow, step } from '@novu/framework';
import { z } from 'zod';

export const smsAlert = workflow(
  'sms-alert',
  {
    payloadSchema: z.object({
      message: z.string(),
    }),
  },
  async (event) => {
    await step.sms(
      'send-sms',
      async () => {
        return {
          body: event.payload.message,
        };
      }
    );
  }
);