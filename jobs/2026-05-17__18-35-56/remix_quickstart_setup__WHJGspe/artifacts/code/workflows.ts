import { workflow } from '@novu/framework';

export const testWorkflow = workflow('test-workflow', async (step) => {
  const emailStep = await step.email(
    'send-email',
    async (inputs) => {
      return {
        subject: 'Test Email from Novu',
        body: 'This is a test email sent using Novu Framework in Remix.',
      };
    }
  );

  return {
    success: true,
    emailSent: emailStep,
  };
});