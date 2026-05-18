const express = require('express');
const { serve } = require('@novu/framework/express');
const { workflow, inApp, email } = require('@novu/framework');
const { z } = require('zod');

const conditionalRouting = workflow(
  'conditional-routing',
  {
    payloadSchema: z.object({
      userName: z.string(),
      critical: z.boolean(),
    }),
  },
  (ctx) => {
    ctx.step(
      inApp('notify-in-app', {
        subject: 'Hello {{payload.userName}}',
        body: 'You have a new notification.',
      })
    );

    ctx.step(
      email(
        'send-email',
        {
          subject: 'Critical notification for {{payload.userName}}',
          body: 'A critical event occurred.',
        },
        {
          skip: ({ payload }) => !payload.critical,
        }
      )
    );
  }
);

const app = express();

app.use('/api/novu', serve({ workflows: [conditionalRouting] }));

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});
