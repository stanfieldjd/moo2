# MOO2 reverse-engineering workbench status

Local source snapshot: `176c55fa21a33df1da4452f52efed2fc3c3a2eb2`

Current phase: full executable decompilation. Gameplay reconstruction is deferred until decompilation coverage is complete enough for a systematic reconstruction pass.

Current best completion estimate: 87% decompilation / 13% remaining.

The original proprietary executable and game assets are not stored in this repository. Development tooling verifies a locally supplied official v1.31 executable before extracting derived analysis.

Recent work has concentrated on resynchronized x86 decoding, CFG-reachable instruction recovery, switch-table recovery, indirect call/table resolution, synthetic unnamed call targets, and Watcom runtime initialization dispatch tables.

## Authenticated static economy checkpoint — 2026-10-16

Original v1.31 pre-import analysis now includes source-verified static reconstruction of two formerly pending economy callbacks: `Colony_BC_Maintenance_` (197 bytes; 48 opcode checkpoints and 4 controlled fixtures) and `Colony_Industry_Maintenance_` (297 bytes; 55 opcode checkpoints and 7 controlled fixtures). Both independently verify the shared original `Event_Check_Space_Anomaly_` (80 bytes) dependency and shared epilogue. The exact evidence, limitations, and reproduction commands are in their corresponding `decompilation/annotated/` files, reports, and `tools/audit_*.py` tests.

Seven of the nine previously identified `Pre_Import_Computing_` downstream economy callbacks still lack these specific source-static reconstructions: `Colony_Morale_`, `Colony_Industry_Production_`, `Colony_Food_Production_`, `Colony_Food_Maintenance_`, `Colony_Replicators_`, `Colony_Research_Production_`, and `Colony_BC_Production_`. No source-level behavioral equivalence under actual DOS execution, native remaster implementation, or revised total decompilation percentage is claimed.

## Authenticated static economy checkpoint — 2026-10-16, food-maintenance continuation

`Colony_Food_Maintenance_` has an additional source-authenticated **static** control-flow reconstruction: original 330-byte body, 73 exact instruction checkpoints, ten controlled synthetic fixtures and the 80-byte `Event_Check_Space_Anomaly_` dependency. See `tools/audit_colony_food_maintenance_v131.py`, `decompilation/reports/colony_food_maintenance_v131_2026-10-16.json`, and `decompilation/annotated/colony_food_maintenance_v131.md` for reproducible evidence and limitations.

Three of the nine previously unresolved pre-import callbacks now have this **specific source-static audit**: `Colony_BC_Maintenance_`, `Colony_Industry_Maintenance_`, and `Colony_Food_Maintenance_`. Six remain in that previously defined set: `Colony_Morale_`, `Colony_Industry_Production_`, `Colony_Food_Production_`, `Colony_Replicators_`, `Colony_Research_Production_`, and `Colony_BC_Production_`. This is a narrow subsystem audit count, **not** a revised estimate of whole-executable decompilation completeness, successful DOS differential verification, or native gameplay implementation.

## Authenticated static economy checkpoint — 2026-10-16, replicator continuation

`Colony_Replicators_` has been traced and source-checked as a separate 594-byte four-stage accounting routine. See `tools/audit_colony_replicators_v131.py`, `decompilation/reports/colony_replicators_v131_2026-10-16.json`, and `decompilation/annotated/colony_replicators_v131.md`. These verify the original complete function body, internal conditional transfers, three final colony-field writes, and bounded arithmetic fixtures; no DOS gameplay execution or full original state-domain equivalence is claimed.

Four of nine initially unresolved `Pre_Import_Computing_` downstream callbacks now have source-static audits: `Colony_BC_Maintenance_`, `Colony_Industry_Maintenance_`, `Colony_Food_Maintenance_`, and `Colony_Replicators_`. Five remain in that particular audit queue: `Colony_Morale_`, `Colony_Industry_Production_`, `Colony_Food_Production_`, `Colony_Research_Production_`, and `Colony_BC_Production_`. The previously recorded 87% whole-executable coverage estimate is unchanged; these counts do not independently measure coverage.

## Authenticated static economy checkpoint — 2026-10-16, morale continuation

`Colony_Morale_` has a source-verified 982-byte **static** control-flow reconstruction including complete 280-instruction coverage, 52 original direct control transfers, authenticated original helper targets and CODE lookup slices, byte-wrapping morale arithmetic, and 30 controlled source-derived fixtures. The gameplay BYTE `+0x07` calculation and optional 13-`sprintf_` breakdown path are separated. Original code evidence, limitations, and reproduction steps are in `analysis/Colony_Morale_.disasm`, `tools/audit_colony_morale_v131.py`, `decompilation/annotated/colony_morale_v131.md`, `docs/research/colony-morale-v131-2026-10-16.md` and `decompilation/reports/colony_morale_v131_2026-10-16.json`.

Five of the original nine source-static `Pre_Import_Computing_` callback audits now have authenticated evidence: `Colony_BC_Maintenance_`, `Colony_Industry_Maintenance_`, `Colony_Food_Maintenance_`, `Colony_Replicators_`, and `Colony_Morale_`. Four remain from that queue: `Colony_Industry_Production_`, `Colony_Food_Production_`, `Colony_Research_Production_`, and `Colony_BC_Production_`. These are **specific audits**, not proof of complete native-game decompilation, valid-state equivalence or updated whole-executable coverage. The previous 87% estimate remains unrecalculated.
