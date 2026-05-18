const express = require("express");
const { serve } = require("@novu/framework/express");
const { welcomeUser } = require("./novu/workflows");

const app = express();

app.use(
  "/api/novu",
  serve({
    workflows: [welcomeUser],
  })
);

app.get("/", (_req, res) => {
  res.send("Novu workflow server is running.");
});

app.listen(3000, () => {
  console.log("Server listening on http://localhost:3000");
});
