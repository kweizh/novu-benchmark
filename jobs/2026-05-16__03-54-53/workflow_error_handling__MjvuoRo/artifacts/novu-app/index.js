'use strict';

const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

// ---------------------------------------------------------------------------
// Payload schema
// ---------------------------------------------------------------------------
const payloadSchema = z.object({
  userId: z.string(),
  simulateError: z.boolean().default(false),
});

// ---------------------------------------------------------------------------
// Workflow definition
// ---------------------------------------------------------------------------
const errorHandlingWorkflow = workflow(
  'error-handling-workflow',
  async ({ step, payload }) => {
    // Custom step: fetch-data
    const fetchDataResult = await step.custom(
      'fetch-data',
      async () => {
        if (payload.simulateError) {
          throw new Error('External API Failed');
        }
        return { status: 'ok' };
      }
    );

    // Email step: send-email
    await step.email(
      'send-email',
      async () => {
        return {
          subject: 'Process Complete',
          body: `The fetch-data step completed with status: ${fetchDataResult.status}`,
        };
      }
    );
  },
  {
    payloadSchema,
  }
);

// ---------------------------------------------------------------------------
// Express server
// ---------------------------------------------------------------------------
const app = express();

app.use('/api/novu', serve({ workflows: [errorHandlingWorkflow] }));

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Novu Bridge server is running on http://localhost:${PORT}/api/novu`);
});
