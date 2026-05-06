const express = require('express');
const { serve } = require('@novu/framework/express');
const { followUpWorkflow } = require('./workflows');

const app = express();
app.use(express.json());

app.use(
  '/api/novu',
  serve({
    workflows: [followUpWorkflow],
  })
);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
