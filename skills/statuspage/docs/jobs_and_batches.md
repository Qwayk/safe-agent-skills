# Jobs and batches

Statuspage work is usually one public page at a time: check the current status, open incidents, planned maintenance, and affected components. The shipped tool is read-only and does not include a batch runner.

For repeated checks, run the same read command against each public status page URL from your own script or scheduler. Keep the output separate by page so incident details do not get mixed together.

If batch behavior is added later, it should stay read-only, show which pages it will check, and update the safety docs and tests at the same time.
