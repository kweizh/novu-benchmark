const express = require('express');
const { serve } = require('@novu/framework/express');
const { slackNotificationWorkflow } = require('./novu/workflows');

const app = express();

// Serve the Novu endpoint
app.use('/api/novu', serve({ workflows: [slackNotificationWorkflow] }));

// Start the server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Novu Bridge Endpoint server running on port ${PORT}`);
  console.log(`Novu endpoint available at http://localhost:${PORT}/api/novu`);
});