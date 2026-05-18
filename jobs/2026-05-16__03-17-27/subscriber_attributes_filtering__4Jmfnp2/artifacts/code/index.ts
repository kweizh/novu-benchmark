import { workflow } from '@novu/framework';
import { z } from 'zod';

export const premiumNotification = workflow(
  'premium-notification',
  async ({ step, payload }) => {
    await step.inApp('notify-in-app', async () => {
      return {
        body: 'You have a new notification!',
      };
    });

    await step.sms(
      'notify-sms',
      async () => {
        return {
          body: 'Premium features unlocked!',
        };
      },
      {
        skip: () => payload.isPremium === false,
      }
    );
  },
  {
    payloadSchema: z.object({
      isPremium: z.boolean().default(false),
    }),
  }
);
