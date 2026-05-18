const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

// Define the multi-tenant workflow
const multiTenantWorkflow = workflow(
  'multi-tenant-workflow',
  async ({ step, payload }) => {
    await step.email('send-email', async () => {
      return {
        subject: `Update from ${payload.tenantName}`,
        body: `Hello ${payload.userName}, this is an update for your organization.`,
      };
    });
  },
  {
    payloadSchema: z.object({
      tenantName: z.string(),
      userName: z.string(),
    }),
  }
);

// Set up Express app
const app = express();

// Mount the Novu bridge endpoint at /api/novu
const novuHandler = serve({ workflows: [multiTenantWorkflow] });
app.use('/api/novu', novuHandler);

// Start the server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Novu bridge endpoint available at http://localhost:${PORT}/api/novu`);
});
