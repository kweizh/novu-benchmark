const express = require("express");
const { workflow } = require("@novu/framework");
const { serve } = require("@novu/framework/express");
const { z } = require("zod");

const multiTenantWorkflow = workflow(
  "multi-tenant-workflow",
  ({ step, payload }) => {
    step.email("send-email", () => ({
      subject: `Update from ${payload.tenantName}`,
      body: `Hello ${payload.userName}, this is an update for your organization.`,
    }));
  },
  {
    payloadSchema: z.object({
      tenantName: z.string(),
      userName: z.string(),
    }),
  }
);

const app = express();
app.use(express.json());

app.use(
  "/api/novu",
  serve({
    workflows: [multiTenantWorkflow],
  })
);

const port = 3000;
app.listen(port, () => {
  console.log(`Novu bridge listening on port ${port}`);
});
