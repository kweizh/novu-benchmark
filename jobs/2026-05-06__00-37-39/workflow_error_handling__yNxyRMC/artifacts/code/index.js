const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

const app = express();
app.use(express.json());

const errorHandlingWorkflow = workflow(
  'error-handling-workflow',
  async ({ step, payload }) => {
    // Custom step: fetch-data
    const data = await step.custom('fetch-data', async () => {
      if (payload.simulateError) {
        throw new Error('External API Failed');
      }
      return { status: 'ok' };
    });

    // Email step: send-email
    await step.email('send-email', async () => {
      return {
        subject: 'Process Complete',
        body: `The process status is: ${data.status}`,
      };
    });
  },
  {
    payloadSchema: z.object({
      userId: z.string(),
      simulateError: z.boolean().default(false),
    }),
  }
);

app.use(
  '/api/novu',
  serve({
    workflows: [errorHandlingWorkflow],
    secretKey: process.env.NOVU_SECRET_KEY || 'dummy-secret-key',
  })
);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
