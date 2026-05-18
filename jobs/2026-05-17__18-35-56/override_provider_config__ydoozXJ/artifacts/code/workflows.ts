import { workflow } from '@novu/framework';
import { z } from 'zod';

export const dynamicProvider = workflow(
  'dynamic-provider',
  async ({ step, payload, subscriber }) => {
    // Step 1: Fetch config from external API
    const config = await step.custom(
      'fetch-config',
      async () => {
        const response = await fetch(
          `http://localhost:4000/config?userId=${subscriber.subscriberId}`
        );
        return response.json();
      }
    );

    // Step 2: Send email with dynamic provider override
    await step.email(
      'send-email',
      async (inputs) => {
        const providerOverrides = getProviderOverrides(config);

        return {
          subject: `Order ${payload.orderId}`,
          body: 'Your order is processing.',
          ...(providerOverrides && { providers: providerOverrides }),
        };
      }
    );
  },
  {
    payloadSchema: z.object({
      orderId: z.string(),
    }),
  }
);

function getProviderOverrides(config: {
  provider?: 'sendgrid' | 'mailgun' | 'none';
  templateId: string;
  data: Record<string, any>;
}) {
  if (!config.provider || config.provider === 'none') {
    return undefined;
  }

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

  return undefined;
}