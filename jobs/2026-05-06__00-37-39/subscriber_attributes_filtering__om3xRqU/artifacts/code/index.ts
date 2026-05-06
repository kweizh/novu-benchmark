import { workflow } from '@novu/framework';
import { z } from 'zod';

export const premiumNotification = workflow(
  'premium-notification',
  async ({ step, payload }) => {
    // In-app step that always runs
    await step.inApp('notify-in-app', async () => {
      return {
        body: 'Welcome to our service!',
      };
    });

    // SMS step that only runs for premium subscribers
    await step.sms(
      'notify-sms',
      async () => {
        return {
          body: 'Premium features unlocked!',
        };
      },
      {
        skip: () => !payload.isPremium,
      }
    );
  },
  {
    payloadSchema: z.object({
      isPremium: z.boolean().default(false),
    }),
  }
);
