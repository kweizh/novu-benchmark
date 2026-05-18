const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

const app = express();
app.use(express.json());

const conditionalRoutingWorkflow = workflow(
  'conditional-routing',
  async ({ step, payload }) => {
    // 1. An inApp step named notify-in-app that always runs.
    await step.inApp('notify-in-app', async () => {
      return {
        body: `Hello ${payload.userName}, this is an in-app notification.`,
      };
    });

    // 2. An email step named send-email that is skipped if payload.critical is false.
    await step.email(
      'send-email',
      async () => {
        return {
          subject: 'Critical Notification',
          body: `Hello ${payload.userName}, this is a critical email notification.`,
        };
      },
      {
        skip: () => !payload.critical,
      }
    );
  },
  {
    payloadSchema: z.object({
      userName: z.string(),
      critical: z.boolean(),
    }),
  }
);

// Create a Novu Bridge Endpoint at /api/novu using @novu/framework/express
app.use('/api/novu', serve({ workflows: [conditionalRoutingWorkflow] }));

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Novu Bridge Endpoint: http://localhost:${PORT}/api/novu`);
});
