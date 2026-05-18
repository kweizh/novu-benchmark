const express = require('express');
const { serve } = require('@novu/framework/express');
const { testWorkflow } = require('./workflows');

const app = express();
app.use(express.json());
app.use('/api/novu', serve({ workflows: [testWorkflow] }));

app.listen(3000, () => console.log('Listening on port 3000'));
