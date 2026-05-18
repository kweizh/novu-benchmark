const express = require('express');
const { serve } = require('@novu/framework/express');
const { slackNotification } = require('./novu/workflows.js');

const app = express();
const port = 3000;

app.use(express.json());

app.use('/api/novu', serve({
  workflows: [slackNotification],
}));

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
