import { serve } from "@novu/framework/remix";
import { testWorkflow } from "../novu/workflows";

const handler = serve({
  workflows: [testWorkflow],
});

export { handler as action, handler as loader };
