Workflows often require fetching fresh data from an external API (like a mock CRM or database) immediately before sending a notification to ensure the content is up-to-date.

You need to create a workflow that utilizes a `custom` step to simulate an API call fetching dynamic user statistics, and then pass the resulting data into an `email` step to construct the message body. 

**Constraints:**
- Must use `step.custom()` to encapsulate the external data fetching logic.
- The mock fetch operation must return a statically defined JSON object for testing purposes.
- The downstream `email` step must await and use the output of the `custom` step.