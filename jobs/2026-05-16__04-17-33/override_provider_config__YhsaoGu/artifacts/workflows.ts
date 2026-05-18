import { workflow } from '@novu/framework';
import { z } from 'zod';

type ProviderConfig = {
  provider?: 'sendgrid' | 'mailgun' | 'none';
  templateId: string;
  data: Record<string, unknown>;
};

const getProviderOverrides = (config?: ProviderConfig) => {
  if (!config?.provider || config.provider === 'none') {
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
        'h:X-Mailgun-Variables': JSON.stringify(config.data ?? {}),
      },
    };
  }

  return undefined;
};

export const dynamicProvider = workflow(
  'dynamic-provider',
  {
    payloadSchema: z.object({
      orderId: z.string(),
    }),
  },
  async ({ step, payload, subscriber }) => {
    const config = await step.custom('fetch-config', async () => {
      const response = await fetch(
        `http://localhost:4000/config?userId=${subscriber.subscriberId}`,
      );

      if (!response.ok) {
        throw new Error(`Failed to load config: ${response.status}`);
      }

      return (await response.json()) as ProviderConfig;
    });

    await step.email('send-email', {
      subject: `Order ${payload.orderId}`,
      body: 'Your order is processing.',
      providers: getProviderOverrides(config),
    });
  },
);
