const express = require('express');
const { serve } = require('@novu/framework/express');
const { followUpWorkflow } = require('./workflows');

const app = express();

app.use('/api/novu', serve({ workflows: [followUpWorkflow] }));

const port = 3000;
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
