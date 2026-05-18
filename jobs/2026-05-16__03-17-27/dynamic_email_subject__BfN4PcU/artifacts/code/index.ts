import express from 'express';
import { serve } from '@novu/framework/express';
import { dynamicEmail } from './workflow';

const app = express();

// Parse JSON bodies (as sent by API clients)
app.use(express.json());

app.use(
  '/api/novu',
  serve({
    workflows: [dynamicEmail]
  })
);

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
