To avoid spamming users with high-frequency alerts, Novu provides a `digest` step that batches notifications over a specified window before sending a summary.

You need to implement a workflow that uses a `digest` step to batch incoming events for exactly 5 minutes, followed by an `email` step that outputs the total number of events collected during that period. 

**Constraints:**
- The digest configuration MUST strictly use a time-based window of 5 minutes (do not use count-based logic).
- The subsequent email step must dynamically render the count of batched events.