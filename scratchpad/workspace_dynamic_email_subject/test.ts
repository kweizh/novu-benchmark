import { workflow } from '@novu/framework';
import { z } from 'zod';
import { serve } from '@novu/framework/express';
import express from 'express';

export const dynamicEmail = workflow(
  'dynamic-email',
  async ({ step, payload }) => {
    await step.email('send-email', async () => ({
      subject: `Order ${payload.orderId} confirmed for ${payload.customerName}`,
      body: `Hello`,
    }));
  },
  {
    payloadSchema: z.object({
      orderId: z.string(),
      customerName: z.string(),
    }),
  }
);

const app = express();
app.use(express.json());
app.use('/api/novu', serve({ workflows: [dynamicEmail] }));
app.listen(3000, () => console.log('Listening on 3000'));
