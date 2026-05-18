import { serve } from '@novu/framework/remix';
import { testWorkflow } from '../novu/workflows';

export const { loader, action } = serve({
  workflows: [testWorkflow],
});
