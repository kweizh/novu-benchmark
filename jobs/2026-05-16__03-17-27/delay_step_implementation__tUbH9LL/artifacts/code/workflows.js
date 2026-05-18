const { workflow } = require('@novu/framework');

const followUpWorkflow = workflow('follow-up-workflow', async ({ step }) => {
  await step.delay('reminder-delay', async () => ({
    amount: 24,
    unit: 'hours'
  }));

  await step.email('follow-up-email', async () => ({
    subject: 'How are you liking our product?',
    body: 'Just checking in!'
  }));
});

module.exports = { followUpWorkflow };
