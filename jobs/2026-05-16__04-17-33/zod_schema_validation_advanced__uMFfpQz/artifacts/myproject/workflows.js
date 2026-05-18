const { workflow } = require("@novu/framework");
const { z } = require("zod");

const payloadSchema = z.object({
  userName: z.string().default("New User"),
  age: z.number().optional(),
});

const welcomeUser = workflow(
  "welcome-user",
  { payloadSchema },
  async ({ step, payload }) => {
    await step.inApp("notify-in-app", async () => {
      const ageText = payload.age ? ` Age: ${payload.age}.` : "";

      return {
        subject: `Welcome ${payload.userName}`,
        body: `Welcome ${payload.userName}.${ageText}`,
      };
    });

    await step.email("send-email", async () => {
      const ageText = payload.age ? ` Age: ${payload.age}.` : "";

      return {
        subject: `Welcome ${payload.userName}`,
        body: `Hello ${payload.userName}.${ageText}`,
      };
    });
  }
);

module.exports = {
  payloadSchema,
  welcomeUser,
};
