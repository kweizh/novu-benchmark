import express from "express";
import { serve } from "@novu/framework/express";
import { dynamicEmailWorkflow } from "./workflow";

const app = express();

app.use("/api/novu", serve({ workflows: [dynamicEmailWorkflow] }));

app.listen(3000, () => {
  console.log("Novu workflow server listening on port 3000");
});
