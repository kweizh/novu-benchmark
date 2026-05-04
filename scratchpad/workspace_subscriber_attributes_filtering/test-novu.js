import { workflow } from '@novu/framework';
import { z } from 'zod';
export const premiumNotification = workflow('premium-notification', async ({ step, payload }) => {
    await step.inApp('notify-in-app', async () => ({
        body: `Welcome!`,
    }));
    await step.sms('notify-sms', async () => ({
        body: `Premium features unlocked!`,
    }), {
        skip: () => payload.isPremium === false
    });
}, {
    payloadSchema: z.object({
        isPremium: z.boolean().default(false),
    }),
});
console.log(Object.keys(premiumNotification));
