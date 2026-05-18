import { workflow } from '@novu/framework';

export const testWorkflow = workflow('test-workflow', async (step) => {
  await step.email('send-email', async (controls) => {
    return {
      subject: 'Test Email',
      body: 'This is a test email from Novu in Remix',
    };
  });
});
