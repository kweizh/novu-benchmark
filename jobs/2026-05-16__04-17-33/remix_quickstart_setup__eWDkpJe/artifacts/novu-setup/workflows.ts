import { workflow } from '@novu/framework';

export const testWorkflow = workflow('test-workflow', async ({ step, payload }) => {
  await step.email('test-email', async () => ({
    subject: 'Test workflow notification',
    body: `Hello ${payload?.name ?? 'there'}, this is a Novu test email.`,
  }));
});
