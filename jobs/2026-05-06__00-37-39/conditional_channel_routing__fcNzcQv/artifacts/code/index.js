const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

const app = express();
app.use(express.json());

const conditionalRoutingWorkflow = workflow(
  'conditional-routing',
  async ({ step, payload }) => {
    await step.inApp(
      'notify-in-app',
      async () => {
        return {
          body: `Hello ${payload.userName}, you have a new notification.`,
        };
      }
    );

    await step.email(
      'send-email',
      async () => {
        return {
          subject: 'Critical Notification',
          body: `Hello ${payload.userName}, this is a critical notification.`,
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

app.use(
  '/api/novu',
  serve({
    workflows: [conditionalRoutingWorkflow],
  })
);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Novu Bridge Endpoint available at http://localhost:${PORT}/api/novu`);
});
