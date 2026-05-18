const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

const app = express();
app.use(express.json());

const errorHandlingWorkflow = workflow(
  'error-handling-workflow',
  async ({ step, payload }) => {
    const data = await step.custom('fetch-data', async () => {
      if (payload.simulateError) {
        throw new Error('External API Failed');
      }
      return { status: 'ok' };
    });

    await step.email('send-email', async () => {
      return {
        subject: 'Process Complete',
        body: `The process completed with status: ${data.status}`,
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

app.use('/api/novu', serve({ workflows: [errorHandlingWorkflow] }));

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Novu Bridge server running on port ${PORT}`);
  console.log(`Endpoint available at http://localhost:${PORT}/api/novu`);
});
