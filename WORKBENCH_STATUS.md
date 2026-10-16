# MOO2 reverse-engineering workbench status

Local source snapshot: `176c55fa21a33df1da4452f52efed2fc3c3a2eb2`

Current phase: full executable decompilation. Gameplay reconstruction is deferred until decompilation coverage is complete enough for a systematic reconstruction pass.

Current best completion estimate: 87% decompilation / 13% remaining.

The original proprietary executable and game assets are not stored in this repository. Development tooling verifies a locally supplied official v1.31 executable before extracting derived analysis.

Recent work has concentrated on resynchronized x86 decoding, CFG-reachable instruction recovery, switch-table recovery, indirect call/table resolution, synthetic unnamed call targets, and Watcom runtime initialization dispatch tables.

## Authenticated static economy checkpoint — 2026-10-16

Original v1.31 pre-import analysis now includes source-verified static reconstruction of two formerly pending economy callbacks: `Colony_BC_Maintenance_` (197 bytes; 48 opcode checkpoints and 4 controlled fixtures) and `Colony_Industry_Maintenance_` (297 bytes; 55 opcode checkpoints and 7 controlled fixtures). Both independently verify the shared original `Event_Check_Space_Anomaly_` (80 bytes) dependency and shared epilogue. The exact evidence, limitations, and reproduction commands are in their corresponding `decompilation/annotated/` files, reports, and `tools/audit_*.py` tests.

Seven of the nine previously identified `Pre_Import_Computing_` downstream economy callbacks still lack these specific source-static reconstructions: `Colony_Morale_`, `Colony_Industry_Production_`, `Colony_Food_Production_`, `Colony_Food_Maintenance_`, `Colony_Replicators_`, `Colony_Research_Production_`, and `Colony_BC_Production_`. No source-level behavioral equivalence under actual DOS execution, native remaster implementation, or revised total decompilation percentage is claimed.
