import { serve } from '@novu/framework/remix';
import { testWorkflow } from '../novu/workflows';

export const action = serve(testWorkflow);
export const loader = serve(testWorkflow);