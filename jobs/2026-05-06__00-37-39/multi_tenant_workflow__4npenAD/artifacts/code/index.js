const express = require('express');
const { workflow } = require('@novu/framework');
const { serve } = require('@novu/framework/express');
const { z } = require('zod');

const app = express();
app.use(express.json());

const multiTenantWorkflow = workflow('multi-tenant-workflow', async ({ step, payload }) => {
  await step.email('send-email', async () => {
    return {
      subject: `Update from ${payload.tenantName}`,
      body: `Hello ${payload.userName}, this is an update for your organization.`,
    };
  });
}, {
  payloadSchema: z.object({
    tenantName: z.string(),
    userName: z.string(),
  }),
});

app.use('/api/novu', serve({ workflows: [multiTenantWorkflow] }));

const port = 3000;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
