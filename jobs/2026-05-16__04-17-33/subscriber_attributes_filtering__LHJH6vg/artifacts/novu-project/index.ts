import { workflow } from '@novu/framework';
import { z } from 'zod';

const payloadSchema = z.object({
  isPremium: z.boolean().default(false),
});

export const premiumNotification = workflow(
  'premium-notification',
  payloadSchema,
  async ({ payload, step }) => {
    await step.inApp('notify-in-app', async () => ({
      body: 'Thanks for being with us!',
    }));

    await step.sms(
      'notify-sms',
      async () => ({
        body: 'Premium features unlocked!',
      }),
      {
        skip: () => !payload.isPremium,
      }
    );
  }
);
