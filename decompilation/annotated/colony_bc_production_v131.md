# Colony_BC_Production_ — authenticated v1.31 static decompilation checkpoint

## Provenance

- Reference executable: official locally supplied `ORION2.EXE` v1.31, SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
- Authenticated Watcom LE CODE image: SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`.
- Full named function body: CODE `0xD03F1..0xD08C7` (1239 bytes), SHA-256 `4ea7459e0e93d44fa342b14b568351a51a2ff317c3291cc98500da0639edc4ac`. Function extent cross-checked against original `decompilation/functions.csv`.
- Source caller: `Pre_Import_Computing_` invokes this procedure at CODE `0xD1E0F`, authenticated separately in `tools/audit_pre_import_computing_v131.py`.
- Independently authenticated complete named callees: `Event_Check_Space_Anomaly_` (80 bytes, CODE `0x1341E`), `Colony_Officer_` (68 bytes, CODE `0xCD9F2`), `Owned_Officer_Level_` (86 bytes, CODE `0x84951`), and `sprintf_` (48 bytes, CODE `0x1165F2`). Exact digests are in the audit report.
- Audit: `tools/audit_colony_bc_production_v131.py` and `decompilation/reports/colony_bc_production_v131_2026-10-16.json`; raw source output `analysis/Colony_BC_Production_.disasm`. No original binaries/assets are committed.

## Complete decoded machine-code coverage

Exactly 1239 source bytes resolve into **381 decoded x86 instructions**, with **72 direct control transfers** (18 CALL and 54 direct conditional/unconditional jumps). Each transfer is validated against a decoded instruction entry, an independently named callee or a recognized shared external tail. The audit also checks 71 selected exact opcode anchors and the full body digest.

Unlike shorter function decodes, GNU `objdump` prints three *continuation lines* for source instructions longer than the configured bytes per line. These lines are the remaining bytes of earlier instructions, **not** new independent instructions:

| Continuation CODE offset | Starts at | Trailing bytes |
|---|---|---|
| `0xD040A` | `0xD0403` | 2 |
| `0xD0431` | `0xD042A` | 2 |
| `0xD0885` | `0xD087E` | 1 |

The audit combines them with their actual instruction starts and verifies exact byte-contiguous coverage. Treating continuation offsets as executable entries would introduce false entry points.

## Source-verified algorithm structure

This is an *annotated description of original machine instructions*, not original recovered C or a runtime-equivalent port.

- **Empty colony:** CODE `0xD03FD–0xD040C` checks colony BYTE `+0x0A`. If zero, store zero in colony WORD `+0xED`, then jump directly to the shared epilogue `0xCEB17`. This path bypasses all optional formatting.
- **Special anomaly:** CODE `0xD0411–0xD044B` derives the colony index using DATA global `_colony`, stride `0x169`, and calls `Event_Check_Space_Anomaly_`. A nonzero return sets WORD `+0xED` to zero; a non-null display pointer receives the text from original DATA global `_anomaly_msg` at `0x3231C`. Then return through `0xCEB17`.
- **Player baseline:** CODE `0xD0450–0xD049B` locates DATA `_player` by signed owner BYTE and stride `0xEA9`, invokes `Colony_Officer_`, reads signed player BYTE `+0x8A4`, doubles and adds 4, and obtains the original population-entry count from colony BYTE `+0x0A`.
- **Population scan:** CODE `0xD04A4–0xD04E6` walks original packed DWORD entries in reverse, reading the low nibble. Only tags less than 8 contribute. The tag-indexed player BYTE `+0x8B6` splits these into two original counters; tags 8–15 do not increment either in this observed loop.
- **Core arithmetic:** CODE `0xD04EF–0xD052C` optionally adds the original CODE-indexed bonus table at `0xCD4E6` (indexed via a global byte at DATA `0x21CB0`) when player BYTE `+0x28` is not 100. It multiplies the two counters' sum by the adjusted base and then applies an original signed quarter rounding sequence (`+2; CDQ; SHL EDX,2; SBB; SAR 2`). For bounded **nonnegative** synthetic input, the isolated sequence equals `floor((count*base+2)/4)`; no arbitrary signed-domain equivalence is claimed.
- **Morale correction:** CODE `0xD052F–0xD0593` skips morale influence for derived government group 3, otherwise uses signed colony morale BYTE `+0x07` and the base amount in a separately signed, rounded division by 20. This path is **dependent on** the earlier `Colony_Morale_` calculation and cannot be treated as an independently sourced constant.
- **Other modifiers:** CODE `0xD0593–0xD06F4` examines the owning planet's BYTE `+0x0F` for extra 5 or 10, the colony's WORD `+0x115` and WORD `+0xE9`, player BYTE `+0x8B7`, player BYTE `+0x162`, colony BYTEs `+0x153/+0x15D`, government BYTE `+0x89F`, and two mutually exclusive leader BYTE `+0x2A` flags (`0x20`, `0x10`) to compute additional contributions. Exact source operands and branch ordering are in the original full disassembly and JSON transfer inventory. Their complete in-game semantic meaning and all value ranges are **unresolved**.
- **Production write:** CODE `0xD06F4–0xD0717` accumulates core and additional modifiers, adds colony WORD `+0x127` using an **AX/WORD operation**, and writes the low **WORD** of the resulting sum to colony `+0xED`. This is not a 32-bit unbounded output and cannot be replaced by clamped arithmetic.
- **Optional text:** CODE `0xD071E–0xD08C3` returns immediately for a null EDI breakdown pointer; otherwise it makes 14 direct `sprintf_` calls to format selected production components, then jumps into the shared last formatter at CODE `0xCEB08`. The binary's external strings and display buffer behavior are not treated as part of numeric production evaluation.

## CODE data and address spaces

The exact eight-byte CODE lookup slice at `0xCD4E6` is `[0,0,1,2,3,25,25,25]`, SHA-256 `59f534fc4d2ed728a8bd38cf136dea4a78ac39176d0d941ef82ef3d2be8450e8`. Runtime globals `_colony`, `_player`, `_planet`, `_leaders` and `_anomaly_msg` are verified original **DATA** references. Do not interpret CODE and DATA offsets as belonging to one uniform address space.

## Verification boundaries

Twelve bounded synthetic fixtures verify population-tag splitting and nonnegative quarter-rounding arithmetic; all 71 selected opcode anchors and the complete 1239-byte body are checked against the canonical locally supplied executable. These fixtures are **not** execution of DOS gameplay or proof of correct native-game equivalence. Additional work is required to trace each complex production modifier to source-level gameplay semantics and verify state lifecycles, signed overflow behavior, original renderer strings and complete runtime behavior. The original game and live website remain untouched.
