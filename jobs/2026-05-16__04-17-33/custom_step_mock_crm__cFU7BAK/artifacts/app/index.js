const express = require("express");
const { workflow, step } = require("@novu/framework");
const { serve } = require("@novu/framework/express");
const { z } = require("zod");

const app = express();
app.use(express.json());

app.get("/api/crm/users/:id", (req, res) => {
  res.json({ name: "Alice", company: "Acme Corp" });
});

const crmNotification = workflow(
  "crm-notification",
  async ({ payload }) => {
    const crmData = await step.custom(
      "fetch-crm-data",
      async () => {
        const response = await fetch(
          `http://localhost:3000/api/crm/users/${payload.userId}`
        );

        if (!response.ok) {
          throw new Error(`CRM request failed with status ${response.status}`);
        }

        return response.json();
      },
      {
        outputSchema: z.object({
          name: z.string(),
          company: z.string(),
        }),
      }
    );

    await step.email("send-email", async () => ({
      subject: `Welcome to ${crmData.company}!`,
      body: `Hello ${crmData.name}, welcome to ${crmData.company}.`,
    }));
  },
  {
    payloadSchema: z.object({
      userId: z.string(),
    }),
  }
);

app.use("/api/novu", serve({ workflows: [crmNotification] }));

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
