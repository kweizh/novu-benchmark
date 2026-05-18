const express = require('express');
const { serve } = require('@novu/framework/express');
const { slackNotification } = require('./novu/workflows');

const app = express();

app.use('/api/novu', serve({
  workflows: [slackNotification],
}));

app.listen(3000, () => {
  console.log('Novu bridge listening on port 3000');
});
