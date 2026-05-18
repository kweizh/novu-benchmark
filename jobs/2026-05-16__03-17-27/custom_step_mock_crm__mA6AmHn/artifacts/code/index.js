const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

const app = express();
app.use(express.json());

// Mock CRM API
app.get('/api/crm/users/:id', (req, res) => {
  res.json({ name: "Alice", company: "Acme Corp" });
});

// Define Novu Workflow
const crmNotification = workflow('crm-notification', async ({ step, payload }) => {
  const crmData = await step.custom('fetch-crm-data', async () => {
    const response = await fetch(`http://localhost:3000/api/crm/users/${payload.userId}`);
    const data = await response.json();
    return data;
  }, {
    outputSchema: z.object({
      name: z.string(),
      company: z.string()
    })
  });

  await step.email('send-email', async () => {
    return {
      subject: `Welcome to ${crmData.company}!`,
      body: `Hello ${crmData.name}, welcome to ${crmData.company}.`
    };
  });
}, {
  payloadSchema: z.object({
    userId: z.string()
  })
});

// Serve Novu workflow
app.use('/api/novu', serve({
  workflows: [crmNotification]
}));

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});