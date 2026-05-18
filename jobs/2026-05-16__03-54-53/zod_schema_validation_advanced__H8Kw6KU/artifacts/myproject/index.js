const express = require('express');
const { serve } = require('@novu/framework/express');
const { welcomeUserWorkflow } = require('./novu/workflows');

const app = express();
const PORT = 3000;

// Parse incoming JSON bodies (required by the Novu Bridge handler)
app.use(express.json());

// ── Novu Bridge Endpoint ─────────────────────────────────────────────────────
// Expose all registered workflows at /api/novu so the Novu platform can
// discover, validate, and trigger them.
app.use(
  '/api/novu',
  serve({ workflows: [welcomeUserWorkflow] })
);

// ── Health check ─────────────────────────────────────────────────────────────
app.get('/', (req, res) => {
  res.json({ status: 'ok', message: 'Novu Bridge server is running.' });
});

// ── Start server ─────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
  console.log(`Novu Bridge Endpoint: http://localhost:${PORT}/api/novu`);
});
