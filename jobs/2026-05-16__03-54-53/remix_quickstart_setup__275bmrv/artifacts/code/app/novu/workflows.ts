import { workflow } from "@novu/framework";
import { z } from "zod";

export const testWorkflow = workflow(
  "test-workflow",
  async ({ step, payload }) => {
    await step.email("send-email", async () => {
      return {
        subject: `Test Notification: ${payload.subject}`,
        body: `<p>Hello,</p><p>${payload.message}</p>`,
      };
    });
  },
  {
    payloadSchema: z.object({
      subject: z.string().default("Test Subject"),
      message: z.string().default("This is a test notification from Novu."),
    }),
  }
);
