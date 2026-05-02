In production environments, it is critical to ensure that only Novu Cloud can successfully invoke your Bridge Endpoint by enforcing HMAC verification.

You need to configure an Express-based bridge endpoint using the `@novu/framework/express` adapter that explicitly enables and enforces HMAC security verification for incoming webhook requests. 

**Constraints:**
- Must use the Express framework adapter.
- The security configuration must strictly read the secret key from `process.env.NOVU_SECRET_KEY`.
- Do NOT hardcode the secret key in the source code.