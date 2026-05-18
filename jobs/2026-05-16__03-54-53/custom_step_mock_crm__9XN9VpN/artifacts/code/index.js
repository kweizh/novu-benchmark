const express = require('express');
const { serve, workflow } = require('@novu/framework/express');
const { z } = require('zod');

const app = express();
app.use(express.json());

// ─── Mock CRM Endpoint ───────────────────────────────────────────────────────

app.get('/api/crm/users/:id', (req, res) => {
  res.json({ name: 'Alice', company: 'Acme Corp' });
});

// ─── Novu Workflow ───────────────────────────────────────────────────────────

const crmNotificationWorkflow = workflow(
  'crm-notification',
  async ({ step, payload }) => {
    // Step 1: Fetch user details from the mock CRM
    const crmData = await step.custom(
      'fetch-crm-data',
      async () => {
        const response = await fetch(
          `http://localhost:3000/api/crm/users/${payload.userId}`
        );
        const data = await response.json();
        return data;
      },
      {
        outputSchema: z.object({
          name: z.string(),
          company: z.string(),
        }),
      }
    );

    // Step 2: Send email using the CRM data
    await step.email(
      'send-email',
      async () => {
        const { name, company } = crmData.outputs;
        return {
          subject: `Welcome to ${company}!`,
          body: `Hello ${name}, welcome to ${company}.`,
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

// ─── Mount Novu Bridge ────────────────────────────────────────────────────────

app.use(
  '/api/novu',
  serve({ workflows: [crmNotificationWorkflow] })
);

// ─── Start Server ─────────────────────────────────────────────────────────────

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Mock CRM endpoint: http://localhost:${PORT}/api/crm/users/:id`);
  console.log(`Novu Bridge:       http://localhost:${PORT}/api/novu`);
});
