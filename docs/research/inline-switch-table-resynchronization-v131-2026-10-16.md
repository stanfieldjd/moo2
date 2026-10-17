# Source-verified v1.31 CODE resynchronization at inline Watcom jump tables

## Original executable and CODE provenance

The authoritative original locally supplied Master of Orion II DOS v1.31 `ORION2.EXE` has SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Its separately reconstructed Watcom LE CODE image contains exactly 1,410,709 bytes and has SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. Neither binary nor any original copyrighted assets are checked into Git.

The earlier global CFG repair (immutable baseline Git commit `ab732e68280da096e44fdf4c028cbc6bc2435a1f`) exposed one last unreachable **source-verified** indirect switch site: `0x117190` in the named original `Farload_Library_Data_` routine. The code layout embeds a verified 4-entry DWORD case-target array **inside** the function at original CODE `0x117145` through `0x117154` (16 bytes). Linear `objdump` erroneously decoded those table bytes as x86 instructions and lost alignment after the table, where original CODE direct branches target `0x117155`.

## Original authenticated function alignment and switch values

The authentic CODE bytes at `0x117140` are `EB 13`: an unconditional relative branch with destination **`0x117155`**. The source CODE at `0x117155` begins the valid five-byte instruction **`BB 01 00 00 00`** (`MOV EBX,1`). At `0x117190`, the original bytes are **`2E FF A0 45 71 11 00`**, namely `JMP DWORD PTR CS:[EAX+0x117145]`. Its four authenticated original case targets, read as DWORDs directly from the 16-byte table, are:

| Case | Original CODE target |
|---|---|
| 0 | `0x117197` |
| 1 | `0x1171BA` |
| 2 | `0x1171E0` |
| 3 | `0x117206` |

These are the already audited Watcom case DWORD values in the original `decompilation/switch_targets_reconciled.csv` and `.json`. **No guessed jump destinations or forced edges are introduced.** The original table data is excluded from machine-instruction decoding and normal disassembly resumes at exactly the first verified code instruction after it.

## Whole-CODE resynchronization procedure

The updated `tools/export_resynchronized_disassembly.py` authenticates the entire source CODE hash and both source-provenance manifests, then re-reads and checks all **1,625 original DWORD case targets**, their respective site IDs, case indices and exact source CODE offsets across **205 independent switch-table spans**. It checks all spans lie within original known CODE-symbol intervals, contain valid original targets and do not overlap other verified tables.

For each original known function-symbol span, `objdump` decodes only the gaps **outside** source-proved inline table data. It starts a new disassembly segment at the first byte following each verified table. That change prevents a literal DWORD target array from misleading the x86 disassembler's next instruction boundary.

The regenerated local `decompilation/code_object_1_resynced.disasm` (excluded from Git because it is a large derivative of the proprietary original executable) now contains **5,562 independently restarted machine-code disassembly spans** across the original **5,546 unique CODE-symbol intervals**. **Exactly 6,500 source-proven inline data bytes** (1,625×4) are excluded from opcode parsing. No disassembly segment failed. These reproducible high-level metrics are checked into `decompilation/resynced_disassembly.json`.

## Measured CFG outcome

The complete conservative v1.31 CODE CFG analysis is regenerated from that disassembly with the original source-verified **205-site / 1,625-case** indexed switch inventory. Measured differences against the immutable previous Git baseline:

| Measure | Before | After |
|---|---:|---:|
| Original function-entry records | 5,635 | 5,635 |
| Recovered source CFG instruction memberships | 395,671 | **395,735** |
| Entries reaching provisional symbol boundary | 5,033 | **5,034** |
| Entries ending before provisional boundary | 553 | **552** |
| Unresolved conservative CFG edges | 45 | **43** |
| Source-authenticated additional switch sites reachable | 69 of 70 | **70 of 70** |

Exactly **one** function's reachable-instruction membership count changes: original `Farload_Library_Data_`, from **129 to 193** (+64), moving from `shorter+unresolved` to `matches` with **zero unresolved paths** within this function's conservative CFG. All other named/synthetic function entry membership counts are unchanged. The original input disassembly's pseudo-instruction count decreases after correctly excluding inline table bytes; that is expected and **is not** an artificial loss of decoded game logic.

The source-verifying audit `tools/audit_inline_switch_table_resync_v131.py` independently re-authenticates all original table DWORD values, case labels, the exact direct-branch and indirect-dispatch source machine bytes, the new disassembly source segment at `0x117155`, reachable source switch case offsets, identical 5,635 function entry identities, and the complete baseline-vs-current per-function CFG delta. Structured reproducible report: `decompilation/reports/inline_switch_table_resync_v131_2026-10-16.json`.

## Confidence and next work

These are measured original x86 machine-code **CFG membership** and boundary improvements. Reaching a provisional symbol boundary is not the same as recovering executable behavior in C/C++, passing a DOS differential test, or making the browser-native game complete. The historically quoted **87%** and later **88%** are not independently measured semantic completion percentages and are not reused as new estimates.

Remaining broad decompilation challenge: **43 conservatively unresolved CFG edges**, some containing original inline data, compiler shared epilogues and runtime-specific control transfers. The complete game behavior, original DOS dynamic parity, Game Lab native browser execution, visual enhancement and Xbox-controller support still require implementation/validation. No change to the source executable, original art, server or live website occurred in this analysis checkpoint.
