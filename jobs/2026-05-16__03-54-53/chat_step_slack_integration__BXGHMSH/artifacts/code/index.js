const express = require('express');
const { serve } = require('@novu/framework/express');
const { slackNotificationWorkflow } = require('./novu/workflows');

const app = express();

app.use(express.json());

app.use('/api/novu', serve({ workflows: [slackNotificationWorkflow] }));

app.listen(3000, () => {
  console.log('Novu Bridge server is running on http://localhost:3000');
  console.log('Bridge endpoint available at http://localhost:3000/api/novu');
});
