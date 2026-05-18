import { workflow } from '@novu/framework';
import { z } from 'zod';

export const dynamicProvider = workflow(
  'dynamic-provider',
  async ({ step, payload, subscriber }) => {
    const config = await step.custom('fetch-config', async () => {
      const response = await fetch(`http://localhost:4000/config?userId=${subscriber.subscriberId}`);
      return await response.json();
    });

    await step.email('send-email', async () => {
      let providers = {};

      if (config.provider === 'sendgrid') {
        providers = {
          sendgrid: {
            templateId: config.templateId,
            dynamicTemplateData: config.data,
          },
        };
      } else if (config.provider === 'mailgun') {
        providers = {
          mailgun: {
            template: config.templateId,
            'h:X-Mailgun-Variables': JSON.stringify(config.data),
          },
        };
      }

      return {
        subject: `Order ${payload.orderId}`,
        body: 'Your order is processing.',
        providers: Object.keys(providers).length > 0 ? providers : undefined,
      };
    });
  },
  {
    payloadSchema: z.object({
      orderId: z.string(),
    }),
  }
);
