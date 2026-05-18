import { workflow } from '@novu/framework';
import { z } from 'zod';

export const dynamicProviderWorkflow = workflow(
  'dynamic-provider',
  async ({ step, payload, subscriber }) => {
    // Step 1: Fetch the provider configuration from the external API
    const fetchConfig = await step.custom(
      'fetch-config',
      async () => {
        const response = await fetch(
          `http://localhost:4000/config?userId=${subscriber.subscriberId}`
        );
        const config = (await response.json()) as {
          provider: 'sendgrid' | 'mailgun' | 'none';
          templateId: string;
          data: Record<string, unknown>;
          [key: string]: unknown;
        };
        return config;
      }
    );

    // Step 2: Send the email with dynamic provider override based on fetchConfig
    await step.email(
      'send-email',
      async () => ({
        subject: `Order ${payload.orderId}`,
        body: 'Your order is processing.',
      }),
      fetchConfig.provider === 'sendgrid'
        ? {
            providers: {
              sendgrid: async () => ({
                templateId: fetchConfig.templateId as string,
                dynamicTemplateData: fetchConfig.data as Record<string, unknown>,
              }),
            },
          }
        : fetchConfig.provider === 'mailgun'
          ? {
              providers: {
                mailgun: async () => ({
                  template: fetchConfig.templateId as string,
                  'h:X-Mailgun-Variables': JSON.stringify(
                    fetchConfig.data as Record<string, unknown>
                  ),
                }),
              },
            }
          : {},
    );
  },
  {
    payloadSchema: z.object({ orderId: z.string() }),
  }
);
