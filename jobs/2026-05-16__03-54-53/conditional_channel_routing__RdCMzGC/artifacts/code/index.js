const express = require('express');
const { serve } = require('@novu/framework/express');
const { workflow } = require('@novu/framework');
const { z } = require('zod');

// Define the payload schema using Zod
const payloadSchema = z.object({
  userName: z.string(),
  critical: z.boolean(),
});

// Define the conditional-routing workflow
const conditionalRoutingWorkflow = workflow(
  'conditional-routing',
  async ({ step, payload }) => {
    // Step 1: inApp notification — always runs
    await step.inApp('notify-in-app', async () => {
      return {
        subject: `Hello, ${payload.userName}!`,
        body: `You have a new notification${payload.critical ? ' (CRITICAL)' : ''}.`,
      };
    });

    // Step 2: email notification — skipped when payload.critical is false
    await step.email(
      'send-email',
      async () => {
        return {
          subject: `Critical Alert for ${payload.userName}`,
          body: `Dear ${payload.userName},\n\nThis is a critical notification that requires your immediate attention.`,
        };
      },
      {
        skip: () => !payload.critical,
      }
    );
  },
  {
    payloadSchema,
  }
);

// Set up Express app and mount the Novu Bridge endpoint
const app = express();

app.use(
  '/api/novu',
  serve({ workflows: [conditionalRoutingWorkflow] })
);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Novu Bridge server running on http://localhost:${PORT}`);
  console.log(`Bridge endpoint available at http://localhost:${PORT}/api/novu`);
});
