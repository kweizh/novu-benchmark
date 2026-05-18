const express = require('express');
const { serve } = require('@novu/framework/express');
const { followUpWorkflow } = require('./workflows');

const app = express();

// Mount the Novu Bridge Endpoint at /api/novu
app.use(express.json());
app.use('/api/novu', serve({ workflows: [followUpWorkflow] }));

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Novu Bridge Endpoint available at http://localhost:${PORT}/api/novu`);
});
