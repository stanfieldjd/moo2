# Local decompilation workbench sync

Current local workbench commit: `31d2e78` (`Keep original machine-code slices out of GitHub`).

The local workbench contains 116 tracked decompilation/tooling/documentation files. Raw proprietary game executables, LBX assets, reconstructed LE object binaries, and raw machine-code function slices are excluded from GitHub.

Current decompilation estimate: approximately 87% complete before the next indirect-control-flow pass.

A complete local Git bundle and tracked-file archive were generated for transfer. The connected GitHub interface currently accepts repository text/blob content but does not expose a local-file upload parameter, so the multi-megabyte local snapshot cannot be transferred as one file through this connector. This marker records the exact local commit that must be synchronized rather than falsely claiming the full transfer completed.
