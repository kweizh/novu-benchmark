const express = require('express');
const { workflow, step } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

// Define the multi-tenant workflow
const multiTenantWorkflow = workflow('multi-tenant-workflow', async (payload) => {
  // Define the email step with the subject and body using payload values
  return step.email({
    subject: `Update from ${payload.tenantName}`,
    body: `Hello ${payload.userName}, this is an update for your organization.`,
  });
}, {
  // Define the payload schema using Zod
  payloadSchema: z.object({
    tenantName: z.string(),
    userName: z.string(),
  }),
});

// Create Express server
const app = express();

// Serve the Novu workflow at /api/novu
serve({
  app,
  workflows: [multiTenantWorkflow],
  path: '/api/novu',
});

// Start the server on port 3000
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Novu multi-tenant workflow server running on port ${PORT}`);
  console.log(`Bridge endpoint available at http://localhost:${PORT}/api/novu`);
});