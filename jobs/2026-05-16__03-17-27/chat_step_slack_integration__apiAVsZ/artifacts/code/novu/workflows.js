const { workflow } = require('@novu/framework');

const slackNotification = workflow('slack-notification', async (step) => {
  await step.chat('send-to-slack', async () => {
    return {
      body: "Hello from Novu!"
    };
  });
});

module.exports = { slackNotification };
