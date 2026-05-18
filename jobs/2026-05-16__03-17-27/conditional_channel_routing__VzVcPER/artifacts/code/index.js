const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

const app = express();
app.use(express.json());

const conditionalRouting = workflow(
  'conditional-routing',
  async ({ step, payload }) => {
    await step.inApp('notify-in-app', async () => {
      return {
        body: 'Hello from In-App',
      };
    });

    await step.email(
      'send-email',
      async () => {
        return {
          subject: 'Critical Alert',
          body: 'This is a critical alert email.',
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
    workflows: [conditionalRouting],
  })
);

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
