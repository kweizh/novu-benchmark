import { workflow } from '@novu/framework';
import { z } from 'zod';

export const subscriberPreferencesWorkflow = workflow(
  'subscriber-preferences',
  async ({ step, payload }) => {
    await step.inApp('inApp', async () => {
      return {
        body: `Hello ${payload.userName}, this is an in-app message.`,
      };
    });

    await step.email('email', async () => {
      return {
        subject: 'Preferences Test',
        body: `Hello ${payload.userName}, this is an email message.`,
      };
    });
  },
  {
    name: 'Subscriber Preferences',
    payloadSchema: z.object({
      userName: z.string(),
    }),
    preferences: {
      channels: {
        in_app: { defaultValue: true, readOnly: false },
        email: { defaultValue: false, readOnly: false },
      },
    },
  }
);
