import { workflow } from "@novu/framework";
import { z } from "zod";

export const dynamicEmail = workflow(
  "dynamic-email",
  async ({ step, payload }) => {
    await step.email(
      "send-email",
      async () => {
        return {
          subject: `Order ${payload.orderId} confirmed for ${payload.customerName}`,
          body: "Hello",
        };
      }
    );
  },
  {
    payloadSchema: z.object({
      orderId: z.string(),
      customerName: z.string(),
    }),
  }
);
