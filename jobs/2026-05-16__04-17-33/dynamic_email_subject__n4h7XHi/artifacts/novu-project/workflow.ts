import { workflow } from "@novu/framework";
import { z } from "zod";

export const dynamicEmailWorkflow = workflow(
  "dynamic-email",
  {
    payloadSchema: z.object({
      orderId: z.string(),
      customerName: z.string(),
    }),
  },
  (context) => {
    const { orderId, customerName } = context.payload;

    return {
      "send-email": {
        channel: "email",
        subject: `Order ${orderId} confirmed for ${customerName}`,
        body: "Hello",
      },
    };
  }
);
