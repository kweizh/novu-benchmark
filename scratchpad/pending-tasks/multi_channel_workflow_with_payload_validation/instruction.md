Novu allows defining robust workflows that span multiple channels (e.g., email, in-app) while ensuring data integrity via payload validation.

You need to implement a workflow named `user-onboarding` that takes a user's `name` and `planTier` as payload parameters, validates them using Zod, and sequentially sends an in-app notification followed by an email notification utilizing these payload variables. 

**Constraints:**
- The payload schema MUST be defined using Zod.
- The `planTier` must default to the string `'free'`.
- Both the `inApp` and `email` steps must reference the validated `name` from the payload in their message bodies.