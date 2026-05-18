const express = require('express');
const { serve } = require('@novu/framework/express');
const { followUpWorkflow } = require('./workflows');

const app = express();

app.use(express.json()); // It's good practice, though serve might handle it.
app.use('/api/novu', serve({
  workflows: [followUpWorkflow]
}));

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
