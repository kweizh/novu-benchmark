import { serve } from '@novu/framework/next';
import { smsAlert } from './workflows';

export const GET = serve({ workflows: [smsAlert] });
export const POST = serve({ workflows: [smsAlert] });
export const OPTIONS = serve({ workflows: [smsAlert] });