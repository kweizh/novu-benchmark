import { workflow } from '@novu/framework';
import { z } from 'zod';

export const premiumNotification = workflow(
  'premium-notification',
  async ({ step, payload }) => {
    // Step that always runs
    await step.inApp('notify-in-app', async () => {
      return {
        body: 'Welcome to our service!',
      };
    });

    // Step that runs only for premium subscribers
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
