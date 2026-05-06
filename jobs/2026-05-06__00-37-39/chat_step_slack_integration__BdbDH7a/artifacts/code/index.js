const express = require('express');
const { serve } = require('@novu/framework/express');
const { slackNotification } = require('./novu/workflows');

const app = express();
app.use(express.json());

app.use('/api/novu', serve({ workflows: [slackNotification] }));

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
