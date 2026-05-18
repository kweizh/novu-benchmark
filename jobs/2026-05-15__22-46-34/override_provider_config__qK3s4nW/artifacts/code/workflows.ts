import { workflow } from '@novu/framework';
import { z } from 'zod';

export const dynamicProvider = workflow(
  'dynamic-provider',
  async ({ step, payload, subscriber }) => {
    const config = await step.custom(
      'fetch-config',
      async () => {
        const response = await fetch(`http://localhost:4000/config?userId=${subscriber.subscriberId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch config: ${response.statusText}`);
        }
        return (await response.json()) as {
          provider: 'sendgrid' | 'mailgun' | 'none';
          templateId: string;
          data: Record<string, any>;
        };
      }
    );

    await step.email(
      'send-email',
      async () => {
        const subject = `Order ${payload.orderId}`;
        const body = `Your order is processing.`;

        const providers: any = {};

        if (config.provider === 'sendgrid') {
          providers.sendgrid = {
            templateId: config.templateId,
            dynamicTemplateData: config.data,
          };
        } else if (config.provider === 'mailgun') {
          providers.mailgun = {
            template: config.templateId,
            'h:X-Mailgun-Variables': JSON.stringify(config.data),
          };
        }

        const result: any = {
          subject,
          body,
        };

        if (Object.keys(providers).length > 0) {
          result.providers = providers;
        }

        return result;
      }
    );
  },
  {
    payloadSchema: z.object({
      orderId: z.string(),
    }),
  }
);
