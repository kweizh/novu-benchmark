import { workflow } from "@novu/framework";
import { z } from "zod";

export const premiumNotification = workflow(
  "premium-notification",
  async ({ step, payload }) => {
    // In-app step: always runs
    await step.inApp("notify-in-app", async () => {
      return {
        subject: "Notification",
        body: payload.isPremium
          ? "Welcome, premium subscriber!"
          : "Welcome to our service!",
      };
    });

    // SMS step: only runs when isPremium is true
    await step.sms(
      "notify-sms",
      async () => {
        return {
          body: "Premium features unlocked!",
        };
      },
      {
        skip: () => !payload.isPremium,
      }
    );
  },
  {
    payloadSchema: z.object({
      isPremium: z.boolean().default(false),
    }),
  }
);
