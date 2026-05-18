const express = require('express');
const { serve } = require('@novu/framework/express');
const { welcomeUser } = require('./novu/workflows');

const app = express();
app.use(express.json());

app.use(
  '/api/novu',
  serve({
    workflows: [welcomeUser],
  })
);

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
