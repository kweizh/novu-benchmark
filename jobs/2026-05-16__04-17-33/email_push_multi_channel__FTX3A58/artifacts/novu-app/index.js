const express = require("express");
const { serve } = require("@novu/framework/express");
const { workflow } = require("@novu/framework");

const app = express();

const welcomeUserWorkflow = workflow("welcome-user", async ({ step }) => {
  await step.inApp("notify-in-app", async () => ({
    subject: "Welcome to our app!",
    body: "Thanks for signing up. We're glad you're here.",
  }));

  await step.email("send-email", async () => ({
    subject: "Welcome to our app!",
    body: "Thanks for signing up. We're glad you're here.",
  }));
});

app.use(express.json());
app.use("/api/novu", serve({ workflows: [welcomeUserWorkflow] }));

app.listen(3000, () => {
  console.log("Novu app listening on port 3000");
});
