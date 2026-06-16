# Jobs and batches (not implemented)

Plausible work is usually a small reporting question: check a site, pull stats, or review events for one time range. The shipped tool does not include a jobs runner yet.

If you need repeatable reporting, run the explicit Plausible commands from your own script and keep each site and date range visible in the output.

Do not treat batch reporting as a write path. Plausible reporting should remain read-first, with clear site IDs, date ranges, and metrics in every request.
