const express = require('express');
const { workflow, serve } = require('@novu/framework/express');
const { z } = require('zod');

// Define the workflow with Zod schema validation
const conditionalRouting = workflow(
  'conditional-routing',
  {
    payloadSchema: z.object({
      userName: z.string(),
      critical: z.boolean(),
    }),
  },
  async ({ step, payload }) => {
    // Step 1: In-app notification - always runs
    await step.inApp('notify-in-app', async () => {
      return {
        subject: `Hello ${payload.userName}!`,
        body: 'You have a new notification.',
      };
    });

    // Step 2: Email - skipped if critical is false
    await step.email('send-email', async () => {
      return {
        subject: `Important: ${payload.userName}`,
        body: 'This is a critical notification.',
      };
    }, {
      skip: () => !payload.critical,
    });
  }
);

// Create Express app
const app = express();

// Serve the Novu workflow
app.use('/api/novu', serve());

// Start the server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Novu bridge endpoint available at http://localhost:${PORT}/api/novu`);
});