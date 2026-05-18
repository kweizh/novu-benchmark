import express from 'express';
import { serve } from '@novu/framework/express';
import { dynamicEmail } from './workflow';

const app = express();

app.use('/api/novu', serve({ workflows: [dynamicEmail] }));

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});