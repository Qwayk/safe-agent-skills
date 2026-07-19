# Repeating work safely

This tool intentionally has no generic CSV job runner. A generic runner would weaken the fixed-command boundary and make mixed financial or payroll changes harder to review.

Some Xero endpoints accept arrays, such as invoice or contact collections. Use the exact fixed command and one reviewed JSON input file for that endpoint. Xero’s limits guide recommends practical bundles of up to about 50 nodes, even when an endpoint has no smaller documented node count.

For repeated reads, run the same fixed read command for each explicit input and keep each output separate. For repeated writes, create and review a separate plan for each meaningful target or one bounded provider-supported collection plan. Never combine unrelated tenants or risk types in one approval.

The old `examples/jobs.csv` and `examples/jobs_with_write.csv` paths are retained only as compatibility notes; they state that no generic jobs command exists.
