const express = require('express');
const { serve } = require('@novu/framework/express');
const { welcomeUser } = require('./novu/workflows.js');

const app = express();
const PORT = 3000;

// Middleware to parse JSON bodies
app.use(express.json());

// Set up the Novu Bridge Endpoint
const novuHandler = serve({
  workflows: [welcomeUser]
});

app.use('/api/novu', novuHandler);

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
  console.log(`Novu Bridge Endpoint available at http://localhost:${PORT}/api/novu`);
});