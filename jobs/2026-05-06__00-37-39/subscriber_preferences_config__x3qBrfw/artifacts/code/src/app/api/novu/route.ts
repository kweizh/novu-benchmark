import { serve } from '@novu/framework/next';
import { subscriberPreferencesWorkflow } from '../../../novu/workflows';

export const { GET, POST, OPTIONS } = serve({
  workflows: [subscriberPreferencesWorkflow],
});
