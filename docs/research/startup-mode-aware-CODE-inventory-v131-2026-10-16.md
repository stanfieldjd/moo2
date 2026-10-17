# Mode-aware original Watcom v1.31 CODE inventory and startup-record repair

## Canonical source and scope

The official Master of Orion II DOS v1.31 executable has SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Original Watcom LE CODE is 1,410,709 bytes, SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. The original binary and art are not committed. Previous source-backed Git `466708db6e14742b4c8cc40e9d4d4067e82c8a7e` provided the 32-bit CFG with 396,138 per-function instruction memberships and 21 unresolved apparent edges, plus a separate fully verified 16-bit real-mode audit.

## Original startup bug and root correction

The Watcom startup entry `_cstart_` is at original CODE **0xFFF18**. Its first two authentic machine bytes are `EB 76`: a relative unconditional branch from 0xFFF18 to **0xFFF90**. The 118 bytes between the end of the original jump and the destination, **[0xFFF1A,0xFFF90)**, contain an embedded Watcom vendor identification record, beginning with the exact original text `WATCOM C/C++32 Run-Time system. (c) Copyright by WATCOM International Corp. 1988-1995. All rights reserved.`, followed by non-code metadata ending `con\0`.

The entire 118-byte source payload is authenticated using SHA-256 `5e20cacba0c278bbb54d1bb3e3c7d8f7a53fce416d3be31fe83a73b4210b5572`. Its original disassembly **must not** be treated as fall-through executable instructions from `_cstart_`. The source CODE at destination `0xFFF90` instead begins `FB 83 E4 FC 89 E3`, the instructions `STI; AND ESP,0xfffffffc; MOV EBX,ESP`. This proves genuine executable startup code resumes there. No guessed destination or arbitrary text suppression has been used.

The updated `tools/export_resynchronized_disassembly.py` authenticates the single original direct-branch pair **0xFFF18→0xFFF90** by decoding its signed displacement, authenticates the complete intervening payload by hash and content markers, excludes only this proven bypassed interval from instruction decoding, and restarts source CODE decoding at the actual target. The original 205 independently authenticated inline switch tables, 1,625 exact target DWORDs and previous 16 original source branch restarts remain unchanged and source-checked.

## Measured whole-CODE control-flow difference

| Source-verified property | Before repair | After repair |
|---|---:|---:|
| Original named/synthetic function records | 5,635 | 5,635 |
| Independently authenticated original CODE disassembly segments | 5,578 | **5,579** |
| Source-authenticated direct branch restarts | 16 | **17** |
| Full source-original CFG instruction memberships | 396,138 | **396,305** |
| Functions matching provisional symbol boundary | 5,038 | **5,039** |
| Functions shorter than provisional boundary | 548 | **547** |
| Remaining apparent global-i386 unresolved edges | 21 | **20** |

Exactly one named function changed: `_cstart_` increased from **1 to 168** valid CFG instruction memberships (+167) and now reaches its provisional boundary with **zero** unresolved source CFG edges. No other function gained or lost memberships in this checkpoint. This counts correct machine-code control flow; it does not establish whole-game semantic completion or DOS dynamic parity.

## Evidence-backed classification of the remaining 15 apparent problem entries

The updated `tools/audit_startup_mode_aware_v131.py` and structured `decompilation/reports/startup_mode_aware_v131_2026-10-16.json` enumerate **all 15** remaining legacy-i386-problem symbols and their total **20** legacy apparent unresolved edges, with exact original byte-region SHA fingerprints, original Watcom symbol kinds and confidence notes:

- Original CODE kind-5 symbols `_Alphabet` (ASCII radix characters, source-read at CODE 0x13498F), `_max_planet_flags` and `_flag_replacement_colors` are **data-labelled within CODE**. Their source byte sequences and kind-5 metadata are authenticated individually. Only `_Alphabet` has independent direct source-read proof; don't infer the complete legal use of the other two tables from their names.
- `__GreenleafFastRealIsr` and `__RealDispatcherRR16` are **genuine 16-bit real-mode code**. Their complete authenticated original source bodies (45 and 36 machine instructions), branch offsets, helper calls, hardware I/O and RETF/IRET were separately recovered and checked in the prior Git source audit. These routines should not be miscounted as failed 32-bit game functions.
- `__IrqDataArrayRR16` is exactly **620 zero bytes**. `__SegmentStartRR16`, `__SegmentEndRR16`, `__SegmentStartPC32` and `__SegmentEndPC32` consist entirely of original zero-filled marker bytes. Their exact allocated layout and live relocation usage are not independently proven, but their apparent i386 decode is not evidence of missing gameplay instructions.
- `__VideoBasePD16` begins with **eight original zero bytes**, then bytes starting with a 16-bit-looking `PUSH BP; MOV BP,SP; PUSH DS` prologue. This is classified conservatively as **mixed storage and probable 16-bit runtime code**, not as fully decoded or safely omitted.
- `_netLobby` spans exactly the ten source bytes `4D 4F 4F 32 EC 00 00 00 00 00`, including literal ASCII `MOO2`. It is a proven embedded signature but its broader original section/function semantics are not fully determined.
- `_climate_maintenance_modifiers` has original source bytes consistent with an embedded table but its Watcom symbol kind is **4**, not kind 5; its entire executable-vs-data extent remains **unproven**.
- `___GETDSEnd_` and synthetic `anon_runtime_0012F1D8` remain unverified startup/entry classifications and should not be force-decoded or excluded to improve a metric.

The 20 apparent 32-bit CFG edges are **not** 20 confirmed original gameplay functions missing. Conversely, the fact that many are explained by data/mode mismatch does not prove zero remaining semantic/gameplay work. The right next step is source-verified module/segment type reconciliation, then native behavior implementation and original DOS differential tests.

## Reproducer and constraints

The independently rerunnable auditor `tools/audit_startup_mode_aware_v131.py` verifies both original whole-file fingerprints, the complete Watcom startup payload and exact short branch, original instruction bytes at the code restart, full local disassembly segmentation, unchanged named-function set, exact per-function CFG membership before and after compared to immutable Git commit `466708db6e14742b4c8cc40e9d4d4067e82c8a7e`, remaining 15 symbol names and 20 edge counts, real-mode/data type boundaries and selected full-body source SHA checks.

The final remaster must not depend on the original executable, DOSBox, DOS/4GW, or LBX assets at runtime. This work changes only original-executable *analysis tools* and source evidence, not the original program, Game Lab deployment, browser playability, visuals or Xbox controller. The previously reported 87% and 88% semantic completion percentages have no independently audited basis and are not revived here.
