# Source-verified production caller control flow — MOO2 v1.31

## Evidence

This checkpoint authenticates **complete machine instruction bytes and direct control flow** for three original Watcom LE CODE functions using the unmodified official v1.31 `ORION2.EXE` (SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`) and exact derived CODE object (SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`).

| Original named function | CODE start | Bytes | Decoded instructions | Direct calls | Direct transfers | Selected exact opcode anchors |
|---|---:|---:|---:|---:|---:|---:|
| `Colony_Research_Production_` | `0xCFF74` | 1,103 | 316 | 32 | 72 | 23 |
| `Colony_Food_Production_` | `0xCE664` | 1,209 | 351 | 35 | 70 | 15 |
| `Colony_Industry_Production_` | `0xCEE1B` | 1,789 | 519 | 40 | 100 | 11 |

These are **static** source-authenticated caller traces, **not** completed behavioral or runtime-equivalent native implementations. The report `decompilation/reports/remaining_colony_production_callers_v131_2026-10-16.json` includes full SHA-256 digests of the three named bodies, all 242 direct transfers, every called named function, all GNU `objdump` opcode-byte continuation lines, and the original output-address anchors.

`tools/audit_remaining_colony_production_callers_v131.py` reproduces the verification, checks every decoded original byte against the Watcom LE CODE object, enforces contiguous instruction coverage and authenticates named helper bodies against the original symbol map. It tests twelve **bounded synthetic caller-only arithmetic** cases; those are *not* DOS runtime comparisons.

## Three caller outputs and shared source paths

### Colony_Research_Production_

- Output is original colony **WORD `+0xEB`**.
- CODE `0xCFF80–0xCFF8F`: if unsigned colony population count BYTE `+0x0A` is zero, set `+0xEB` to zero and use shared return at `0xCEB17`.
- CODE `0xCFF94–0xCFFCE`: compute colony index from global DATA `_colony` with record stride `0x169`; call `Event_Check_Space_Anomaly_`. For a nonzero result, zero WORD `+0xEB`; optionally copy DATA `_anomaly_msg` to caller-provided EDI display buffer, then return via `0xCEB17`.
- CODE `0xCFFD3–0xCFFED`: pass job-type selector **2** to `Colony_Job_Production_` at CODE `0xCE280`, with a local breakdown destination only when the EDI display buffer is present. The returned AX is then sign-extended.
- CODE `0xCFFF0–0xD0050`: conditionally add the observed exact constant contributions **5**, **10**, **15**, and **30** based on four colony BYTE flags at `+0x159`, `+0x154`, `+0x149`, and `+0x13C`. Store the low WORD to colony `+0xEB`. The flags' gameplay labels remain to be established by cross references, rather than assigned by guess.
- CODE `0xD0057–0xD03BE`: optional breakdown text uses 22 direct `sprintf_` calls, eight `Format_Quotient_` calls and shared formatter tail `0xCEB08`. This formatting path runs *after* the numeric WORD write; it is not the origin of that value.

### Colony_Food_Production_

- Output is original colony **WORD `+0xE7`**.
- CODE `0xCE670–0xCE6BE`: empty colony or the positive anomaly predicate zeroes `+0xE7`; the anomaly path can copy DATA `_anomaly_msg` to the optional display buffer.
- CODE `0xCE6C9–0xCE6FF`: if colony BYTE `+0xDD` is zero, the routine clears an optional local breakdown buffer via `memset_` and skips the shared job-production calculation. Otherwise call `Colony_Job_Production_` (job-type selector **0**), with optional breakdown pointer determined by caller EDI.
- CODE `0xCE6FF–0xCE727`: flags at colony `+0x14B` and `+0x161` contribute selected values **2** and **4** before writing the low WORD to `+0xE7`. This exact limited caller arithmetic is covered by the controlled fixtures; the shared helper's internal production contributions are not.
- The rest of the named procedure contains source-linked optional breakdown text. The audit verifies 23 `sprintf_` calls and nine `Format_Quotient_` calls along with the source control branches.

### Colony_Industry_Production_

- Output is original colony **WORD `+0xE9`**; the routine also resets colony BYTE `+0xFB` at entry.
- CODE `0xCEE2D–0xCEE45`: reset BYTE `+0xFB`; if unsigned population BYTE `+0x0A` is zero, store zero to WORD `+0xE9`, then take the original in-function shared return path.
- CODE `0xCEE4A–0xCEE84`: derive index via DATA global `_colony`, call `Event_Check_Space_Anomaly_`; a positive result sets WORD `+0xE9` zero and optionally copies anomaly text.
- CODE `0xCEE89–0xCEEA5`: selector **1** to `Colony_Job_Production_`. The industry procedure includes its own longer branch-specific modifiers and optional display formatting; **this audit does not claim** to have semantically resolved every player, leader, planet, or building field used in that calculation. The source references to named `Colony_Officer_` and `Owned_Officer_Level_` are verified.
- The audit confirms 26 direct `sprintf_` calls, nine `Format_Quotient_` calls, a total of 40 named direct calls, and an unusual source-original Watcom stack-frame adjustment (`ENTER 0x2F0; SUB EBP,0x82`). Those exact frame operations must not be replaced with guessed local indexing.

## Common nested dependency and current proof boundary

The shared `Colony_Job_Production_` has original CODE start `0xCE280`, complete named length **996 bytes**, source SHA-256 `853acbdf8e5057e9ad4f3a34c7f5aa98392c668eee1568f8133995ca5d641860`. All three callers' direct call targets and its complete body identity are verified. The helper has its own officer, player, planet, and technology branches and therefore **requires an independent internal behavioral audit**.

Related source named callee bodies verified by hash: `Event_Check_Space_Anomaly_`, `Format_Quotient_`, `Colony_Officer_`, `Owned_Officer_Level_`, `sprintf_`, and `memset_`. A matched callee hash proves source provenance only, not its complete game-rule semantics.

GNU `objdump` byte continuation rows are reattached to the preceding actual instruction start. Verified continuation-line totals: nine for research, thirteen for food, eleven for industry. The previous raw disassembly files `analysis/Colony_Research_Production_.disasm`, `analysis/Colony_Food_Production_.disasm`, and `analysis/Colony_Industry_Production_.disasm` remain **unchanged**.

This checkpoint closes *instruction coverage for the three caller bodies in the nine-function audit queue*, not all remaining source-level behavior. Original DOS differential tests, signed/domain edge cases and clean native game rendering and gameplay remain unverified.
