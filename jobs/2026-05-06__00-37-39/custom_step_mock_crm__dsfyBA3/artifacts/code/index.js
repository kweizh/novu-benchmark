const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

const app = express();
app.use(express.json());

const PORT = 3000;

// Mock CRM endpoint
app.get('/api/crm/users/:id', (req, res) => {
  res.json({
    name: 'Alice',
    company: 'Acme Corp',
  });
});

// Novu Workflow
const crmNotificationWorkflow = workflow(
  'crm-notification',
  async ({ step, payload }) => {
    // Custom step to fetch CRM data
    const crmData = await step.custom(
      'fetch-crm-data',
      async () => {
        const response = await fetch(`http://localhost:3000/api/crm/users/${payload.userId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch CRM data');
        }
        return await response.json();
      },
      {
        outputSchema: z.object({
          name: z.string(),
          company: z.string(),
        }),
      }
    );

    // Email step using the CRM data
    await step.email(
      'send-email',
      async () => {
        return {
          subject: `Welcome to ${crmData.company}!`,
          body: `Hello ${crmData.name}, welcome to ${crmData.company}.`,
        };
      }
    );
  },
  {
    payloadSchema: z.object({
      userId: z.string(),
    }),
  }
);

// Serve Novu Bridge
app.use(
  '/api/novu',
  serve({
    workflows: [crmNotificationWorkflow],
    secretKey: 'my-secret-key', // Added dummy secret key
  })
);

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Novu Bridge served at http://localhost:${PORT}/api/novu`);
});
