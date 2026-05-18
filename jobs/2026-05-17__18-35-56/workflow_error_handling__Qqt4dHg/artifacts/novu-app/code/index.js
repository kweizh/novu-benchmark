const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

// Define the Zod schema for payload validation
const errorHandlingWorkflowSchema = z.object({
  userId: z.string(),
  simulateError: z.boolean().default(false),
});

// Define the error-handling-workflow
const errorHandlingWorkflow = workflow('error-handling-workflow', async (step) => {
  // Custom step: fetch-data
  const fetchData = await step.custom(
    'fetch-data',
    async ({ payload }) => {
      if (payload.simulateError) {
        throw new Error('External API Failed');
      }
      return { status: 'ok' };
    }
  );

  // Email step: send-email
  await step.email('send-email', {
    subject: 'Process Complete',
    body: `The process has completed with status: ${fetchData.status}`,
  });
}, {
  payloadSchema: errorHandlingWorkflowSchema,
});

// Create Express app
const app = express();

// Mount the Novu Bridge at /api/novu
app.use('/api/novu', serve());

// Start the server on port 3000
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Novu Bridge server running on port ${PORT}`);
  console.log(`Workflow endpoint available at http://localhost:${PORT}/api/novu`);
});