const { workflow, step } = require('@novu/framework');

const followUpWorkflow = workflow('follow-up-workflow', async ({ step }) => {
  // Delay step to pause execution for 24 hours
  await step.delay('reminder-delay', async () => ({
    amount: 24,
    unit: 'hours'
  }));

  // Email step after the delay
  await step.email('follow-up-email', async () => ({
    subject: 'How are you liking our product?',
    body: 'Just checking in!'
  }));
});

module.exports = { followUpWorkflow };