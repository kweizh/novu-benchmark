const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

const app = express();
app.use(express.json());

const PORT = 3000;

/**
 * Mock CRM endpoint
 * Returns a JSON object { "name": "Alice", "company": "Acme Corp" } for any ID.
 */
app.get('/api/crm/users/:id', (req, res) => {
  console.log(`CRM API called for user ID: ${req.params.id}`);
  res.json({ name: "Alice", company: "Acme Corp" });
});

/**
 * Novu workflow named 'crm-notification'
 */
const crmNotification = workflow(
  'crm-notification',
  async ({ step, payload }) => {
    // Step 1: Fetch CRM data using a custom step
    const crmData = await step.custom(
      'fetch-crm-data',
      async () => {
        console.log(`Fetching CRM data for user: ${payload.userId}`);
        const response = await fetch(`http://localhost:${PORT}/api/crm/users/${payload.userId}`);
        if (!response.ok) {
          throw new Error(`Failed to fetch CRM data: ${response.statusText}`);
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

    // Step 2: Send email using the data returned from the custom step
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

// Serve the Novu workflow at /api/novu
app.use('/api/novu', serve({ workflows: [crmNotification] }));

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Novu Bridge endpoint available at http://localhost:${PORT}/api/novu`);
  console.log(`Mock CRM endpoint available at http://localhost:${PORT}/api/crm/users/:id`);
});
