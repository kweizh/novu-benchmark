import { workflow } from '@novu/framework';
import { z } from 'zod';

export const dynamicProviderWorkflow = workflow(
  'dynamic-provider',
  async ({ step, payload, subscriber }) => {
    const config = await step.custom(
      'fetch-config',
      async () => {
        const response = await fetch(`http://localhost:4000/config?userId=${subscriber.subscriberId}`);
        const data = await response.json();
        return data as {
          provider: 'sendgrid' | 'mailgun' | 'none';
          templateId: string;
          data: Record<string, any>;
        };
      }
    );

    await step.email(
      'send-email',
      async (inputs) => {
        return {
          subject: `Order ${payload.orderId}`,
          body: `Your order is processing.`,
        };
      },
      {
        providers: (inputs) => {
          if (config.provider === 'sendgrid') {
            return {
              sendgrid: {
                templateId: config.templateId,
                dynamicTemplateData: config.data,
              },
            };
          }

          if (config.provider === 'mailgun') {
            return {
              mailgun: {
                template: config.templateId,
                'h:X-Mailgun-Variables': JSON.stringify(config.data),
              },
            };
          }

          return {};
        },
      }
    );
  },
  {
    payloadSchema: z.object({
      orderId: z.string(),
    }),
  }
);
