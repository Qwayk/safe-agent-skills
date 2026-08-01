# Source architecture

`operations.py` is the fixed 40-operation inventory. `cli.py` builds the named parser tree, validates official query bounds, plans and applies writes, performs available preflight and response-derived readback checks, masks private output, and labels async responses. `config.py` keeps the production host fixed and loads the two credential values. `http.py` enforces HTTPS and the Spaceship host before sending a request, disables redirects, and treats a 3xx as a failed original-host response.

`runs.py`, `audit_log.py`, and `json_files.py` support automatic run-local plans and receipts, explicit output paths, and run history. Run IDs are validated as safe single path segments before a run directory is created. Persisted command displays digest contact and SafePay transaction identifiers, while audit fields mask billing contacts and opaque private errors. These modules do not add provider operations. `output.py` keeps JSON mode to one object on stdout.

Some unchanged starter modules remain in the source checkout because this task was not authorized to delete or reorganize files. They are unreachable from `cli.py`, unreferenced by customer docs, and excluded from both package archives. The installed command surface contains only the fixed Spaceship operations and local front doors described above.
