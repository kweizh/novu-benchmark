import { serve } from '@novu/framework/remix';
import { testWorkflow } from '../novu/workflows';

export const { action, loader } = serve({
  workflows: [testWorkflow],
});
