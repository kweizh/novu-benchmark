const express = require('express');
const { serve } = require('@novu/framework/express');
const { followUpWorkflow } = require('./workflows');

const app = express();

// Serve the Novu Bridge Endpoint
app.use('/api/novu', serve([followUpWorkflow]));

// Start the Express server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Novu Bridge Endpoint available at http://localhost:${PORT}/api/novu`);
});