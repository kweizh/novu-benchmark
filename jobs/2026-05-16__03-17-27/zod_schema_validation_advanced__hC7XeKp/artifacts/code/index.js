const express = require('express');
const { serve } = require('@novu/framework/express');
const { welcomeUser } = require('./novu/workflows');

const app = express();
const port = 3000;

app.use(express.json());

app.use('/api/novu', serve({ workflows: [welcomeUser] }));

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
