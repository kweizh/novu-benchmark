const { workflow } = require('@novu/framework');

const slackNotification = workflow('slack-notification', async () => {
  return {
    steps: {
      'send-to-slack': {
        type: 'chat',
        body: {
          text: 'Hello from Novu!',
        },
      },
    },
  };
});

module.exports = {
  slackNotification,
};
