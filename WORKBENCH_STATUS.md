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

## Authenticated static economy checkpoint — 2026-10-16, BC production continuation

`Colony_BC_Production_` now has source-authenticated static coverage of its full original 1239-byte body (381 decoded instructions, 72 direct CALL/JMP/Jcc transfers, 71 exact opcode anchors, 12 bounded fixtures). Its 18 named direct calls, split instruction-byte continuations, final colony WORD `+0xED` write, zero-population/anomaly exits and optional formatter path are auditable via `tools/audit_colony_bc_production_v131.py`, `decompilation/reports/colony_bc_production_v131_2026-10-16.json`, `analysis/Colony_BC_Production_.disasm`, `decompilation/annotated/colony_bc_production_v131.md` and `docs/research/colony-bc-production-v131-2026-10-16.md`. Some complex signed production-modifier semantics and original DOS differential behavior remain unverified.

Six of the original nine `Pre_Import_Computing_` callbacks now have source-static audits: `Colony_BC_Maintenance_`, `Colony_Industry_Maintenance_`, `Colony_Food_Maintenance_`, `Colony_Replicators_`, `Colony_Morale_` and `Colony_BC_Production_`. Three remain in this specific audit queue: `Colony_Industry_Production_`, `Colony_Food_Production_` and `Colony_Research_Production_`. These audit counts do not establish overall executable-decompilation completeness, runtime equivalence or a revised percentage; the earlier 87% estimate remains unrecalculated.

## Authenticated static caller checkpoint — 2026-10-16, research / food / industry production

Three remaining original `Pre_Import_Computing_` production **caller bodies** have now received authenticated, exact-byte static control-flow audits: `Colony_Research_Production_` (1,103 bytes; 316 source instructions; 72 direct transfers), `Colony_Food_Production_` (1,209 bytes; 351 instructions; 70 direct transfers), and `Colony_Industry_Production_` (1,789 bytes; 519 instructions; 100 direct transfers). Verification includes original EXE/CODE digests, complete named function body hashes, contiguously decoded original bytes, named callee target/body hashes, original CODE/DATA address distinction, selected exact instruction anchors and twelve bounded controlled caller-only arithmetic fixtures. See `tools/audit_remaining_colony_production_callers_v131.py`, `decompilation/reports/remaining_colony_production_callers_v131_2026-10-16.json`, and `decompilation/annotated/remaining_colony_production_callers_v131.md`. Original raw disassembly files remain unchanged.

All **nine of the initially identified `Pre_Import_Computing_` callback bodies now have source-static audits**. This closes that caller-body *instruction-coverage queue*, **not** all behavioral obligations. In particular, all three production callers depend on `Colony_Job_Production_` (996 original bytes), whose full original body is source-authenticated but whose internal gameplay behavior is **not proven by the current caller audit**; other modifier branches likewise need semantic/differential work. No DOS runtime equivalence or complete native-game implementation is claimed. The prior whole-executable 87% estimate remains unrecalculated.

## Shared job-production dependency checkpoint — 2026-10-16

The production callers' shared `Colony_Job_Production_` body at original CODE `0xCE280` now additionally has a source-authenticated static full-body audit (996 bytes, 283 decoded x86 instructions, 62 direct control transfers, 40 exact opcode anchors, seven disassembler byte continuations, authenticated named helper bodies and 15 bounded final-division fixtures). Its three job selectors are traced and the optional `0x256`-byte per-source breakdown copy is distinguished from return arithmetic. Evidence: `tools/audit_colony_job_production_v131.py`, `decompilation/reports/colony_job_production_v131_2026-10-16.json`, and `decompilation/annotated/colony_job_production_v131.md`.

This upgrades the helper's **static instruction and branch coverage**, but its nested `Gravity_Player_Production_Factor_` / `Colony_Pop_Base_Prod_Produced_` game-rule semantics, all production modifiers and actual DOS runtime equivalence remain outstanding. The previous 87% whole-executable completion estimate has not been recalculated.
