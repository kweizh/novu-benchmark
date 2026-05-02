Connecting a Next.js application to Novu Cloud requires setting up a webhook-like Bridge Endpoint using the Novu Framework.

You need to create a basic Next.js App Router API route (`app/api/novu/route.ts`) that initializes the Novu bridge and serves a simple `hello-world` workflow containing a single in-app notification step. 

**Constraints:**
- Must use the `@novu/framework/next` adapter.
- Must correctly export `GET`, `POST`, and `OPTIONS` handlers from the `serve` function.
- The workflow must be named exactly `hello-world`.