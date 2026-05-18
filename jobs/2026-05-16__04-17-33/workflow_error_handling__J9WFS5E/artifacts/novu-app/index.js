const express = require("express");
const { workflow } = require("@novu/framework");
const { serve } = require("@novu/framework/express");
const { z } = require("zod");

const errorHandlingWorkflow = workflow(
  "error-handling-workflow",
  async ({ payload, step }) => {
    const fetchResult = await step.custom(
      "fetch-data",
      async () => {
        if (payload.simulateError) {
          throw new Error("External API Failed");
        }

        return { status: "ok" };
      },
      {
        outputSchema: z.object({ status: z.string() }),
      }
    );

    await step.email("send-email", async () => ({
      subject: "Process Complete",
      body: `Status: ${fetchResult.status}`,
    }));
  },
  {
    payloadSchema: z.object({
      userId: z.string(),
      simulateError: z.boolean().default(false),
    }),
  }
);

const app = express();
app.use(express.json());
app.use("/api/novu", serve({ workflows: [errorHandlingWorkflow] }));

app.listen(3000, () => {
  console.log("Novu bridge listening on port 3000");
});
