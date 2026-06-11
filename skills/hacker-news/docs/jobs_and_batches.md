# Jobs and batches

This tool intentionally does not implement a jobs runner.

Reasons:
- The full public API surface is small.
- Every supported endpoint already has an explicit named command.
- Keeping the surface small avoids accidental “generic bridge” behavior.

If batch behavior is ever added later, it must preserve the explicit command surface and update the user docs and the tests together.
