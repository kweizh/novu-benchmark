import { workflow, email } from '@novu/framework';
import { z } from 'zod';

export const dynamicEmail = workflow('dynamic-email', async (step) => {
  const payload = await step.payload(
    z.object({
      orderId: z.string(),
      customerName: z.string(),
    })
  );

  await step.email(
    'send-email',
    async () => {
      return {
        subject: `Order ${payload.orderId} confirmed for ${payload.customerName}`,
        body: 'Hello',
      };
    }
  );
});