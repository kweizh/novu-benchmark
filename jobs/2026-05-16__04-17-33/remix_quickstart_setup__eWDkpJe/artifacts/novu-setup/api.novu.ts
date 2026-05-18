import { serve } from '@novu/framework/remix';
import { testWorkflow } from '~/novu/workflows';

const handler = serve({ workflows: [testWorkflow] });

export const loader = handler;
export const action = handler;
