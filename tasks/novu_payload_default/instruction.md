# Novu Payload Default Values

## Background
Novu allows you to define payload schemas for your workflows using Zod. You can specify default values for fields in the payload schema, which are used if the trigger does not provide them.

## Requirements
- You have a Node.js project initialized in `/home/user/project`.
- Create a file `src/novu/workflows.ts` that exports a Novu workflow named `welcome-user`.
- The workflow must have a payload schema defined using `zod`.
- The schema must have a field `userName` of type string with a default value of `'Guest'`.
- The workflow should contain an email step named `send-email` that uses `payload.userName` in its subject.

## Implementation Guide
1. Navigate to `/home/user/project`.
2. Create the file `src/novu/workflows.ts`.
3. Import `workflow` from `@novu/framework` and `z` from `zod`.
4. Define and export the `welcomeUser` workflow.
5. In the workflow options, define `payloadSchema` with `z.object({ userName: z.string().default('Guest') })`.
6. Add an `email` step to the workflow that sets the subject to something like `Welcome, ${payload.userName}!`.

## Constraints
- Project path: /home/user/project
- The workflow ID must be `welcome-user`.
- The exported workflow variable should be named `welcomeUser`.