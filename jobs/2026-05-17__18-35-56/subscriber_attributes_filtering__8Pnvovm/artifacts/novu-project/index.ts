import { workflow } from '@novu/framework';
import { z } from 'zod';

// Define the payload schema with isPremium boolean property (default false)
const premiumNotificationSchema = z.object({
  isPremium: z.boolean().default(false),
});

// Create the premiumNotification workflow with ID 'premium-notification'
export const premiumNotification = workflow(
  'premium-notification',
  async ({ step, payload }) => {
    // In-app step - always runs
    await step.inApp('notify-in-app', async () => {
      return {
        subject: 'Notification',
        body: 'You have a new notification',
      };
    });

    // SMS step - only runs if payload.isPremium is true
    await step.sms(
      'notify-sms',
      async () => {
        return {
          body: 'Premium features unlocked!',
        };
      },
      {
        // Skip if isPremium is false
        skip: () => !payload.isPremium,
      }
    );
  },
  {
    payloadSchema: premiumNotificationSchema,
  }
);