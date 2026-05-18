const express = require('express');
const { workflow, step } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

const app = express();

app.use(express.json());

// Mock CRM endpoint
app.get('/api/crm/users/:id', (req, res) => {
  // Return mock user data for any ID
  res.json({
    name: 'Alice',
    company: 'Acme Corp'
  });
});

// Define the Novu workflow
const crmNotificationWorkflow = workflow('crm-notification', {
  payloadSchema: z.object({
    userId: z.string()
  })
}, async ({ payload, step }) => {
  // Custom step to fetch CRM data
  const crmData = await step.custom('fetch-crm-data', {
    outputSchema: z.object({
      name: z.string(),
      company: z.string()
    })
  }, async () => {
    // Make HTTP GET request to the mock CRM endpoint
    const response = await fetch(`http://localhost:3000/api/crm/users/${payload.userId}`);
    const data = await response.json();
    return data;
  });

  // Email step using the CRM data
  await step.email('send-email', {
    subject: `Welcome to ${crmData.company}!`,
    body: `Hello ${crmData.name}, welcome to ${crmData.company}.`
  });
});

// Mount the Novu workflow at /api/novu
app.use('/api/novu', serve(crmNotificationWorkflow));

// Start the server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Mock CRM endpoint: http://localhost:${PORT}/api/crm/users/:id`);
  console.log(`Novu workflow endpoint: http://localhost:${PORT}/api/novu`);
});