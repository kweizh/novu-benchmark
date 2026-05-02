Certain notification steps should only execute if specific subscriber attributes or conditions are met, such as restricting SMS notifications to premium users.

You need to create a workflow containing an `sms` step where the execution is conditionally bypassed using the step's native `skip` function if the subscriber's custom attribute `isPremium` evaluates to false. 

**Constraints:**
- Must use the native `skip` function provided in the step configuration.
- Do NOT wrap the step in a standard `if/else` block; rely entirely on Novu's step-level skip configuration.
- The skip logic must accurately read from the `subscriber` object.