import express from "express";
import { serve } from "@novu/framework/express";
import { dynamicEmailWorkflow } from "./workflow";

const app = express();

app.use(express.json());

app.use("/api/novu", serve({ workflows: [dynamicEmailWorkflow] }));

app.listen(3000, () => {
  console.log("Server is running on port 3000");
});
