# Original v1.31 direct-branch resynchronization and final conservative CFG triage

## Original-source evidence and why this matters

The official original Master of Orion II DOS v1.31 executable `ORION2.EXE` has SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Its original extracted Watcom LE CODE has SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837` and length 1,410,709 bytes. Proprietary original source executable/CODE files are local only, not committed.

Previous corrected whole-executable reconstruction at GitHub commit `4882a69f0e2b73c0afd2a90cd51af46347a85b03` verified 205 inline Watcom switch tables, 1,625 exact case entries, 395,735 CFG instruction memberships, and 43 unresolved CFG edges across the 5,635 original CODE/synthetic function entries.

Investigation of all **43 individual unresolved edges** found most game-related remaining cases were not indirect calls at all: the original Watcom x86 `JMP` and `Jcc` instructions directly encode a valid destination **within their own named function**, but the previous linear disassembly lost instruction alignment before the target. For example, original CODE `0x10759A` includes `EB 45` (branch to `0x1075E1` inside `Draw_Visible_Fields_Back_`) and the original CODE `0x11A164` includes `E9 B8 00 00 00` (branch to `0x11A221` in `Draw_No_Glass_`). Source CODE `0x116565` includes `E3 0B` (JECXZ branch to `0x116572` within `strstr_`). These targets are original instruction addresses authenticated directly from the machine-code displacement, not guessed from disassembler labels.

## Exact verified branch sites

The updated `tools/export_resynchronized_disassembly.py` now verifies **16** original-code direct branch displacements in **15** original named function intervals, then splits its disassembly at the corresponding proven branch destination. It rejects source branches whose opcode, displacement, same-function interval, or verified inline-data boundaries fail validation. The source-verifying auditor `tools/audit_direct_branch_resync_v131.py` independently checks the entire 205 source-verified inline switch table spans / 1,625 exact original case destinations and the new branch restart provenance.

| Original function / branch context | Source branch CODE | Verified restart CODE |
|---|---|---|
| Disable_Draw_Field_ | `0x10733F` | `0x107351` |
| Draw_Visible_Fields_Back_ | `0x10759A` | `0x1075E1` |
| Get_Video_Total_Memory_ | `0x115442` | `0x11545F` |
| strstr_ | `0x116565` | `0x116572` |
| strstr_ | `0x11659A` | `0x1165A7` |
| Farload_Library_ | `0x116E39` | `0x116E51` |
| Draw_No_Glass_ | `0x11A164` | `0x11A221` |
| Draw_ | `0x11A77F` | `0x11A791` |
| Remap_Draw_ | `0x11B935` | `0x11B949` |
| Draw_File_Animation_Stencil_ | `0x11CE55` | `0x11CE73` |
| Draw_File_Animation_On_ | `0x11D095` | `0x11D0B3` |
| Draw_Multi_File_Animation_ | `0x11D55A` | `0x11D56F` |
| Replace_Color_ | `0x1271E0` | `0x1271FF` |
| Replace_Color_All_ | `0x12747D` | `0x12749F` |
| Replace_Color_Gradient_ | `0x12774B` | `0x12776B` |
| Print_Paragraph_ | `0x12E2BE` | `0x12E2D6` |

All direct branch instructions are re-read from original CODE, decoded by opcode class and signed displacement width, and required to encode their recorded destination exactly. No new switch entry, guessed branch target, or gameplay rule is introduced.

## Full original CODE regeneration and auditable gains

The exporter performed **5,578 separate disassembly segments** instead of 5,562, retaining the same **5,546 original named CODE symbol intervals**. All 205 original authenticated inline tables and their exact 6,500 bytes of case DWORD data remain excluded from x86 instruction decoding. No disassembler restart failed.

| Conservative original-source CFG measure | Before | Now |
|---|---:|---:|
| CFG instruction memberships | 395,735 | **396,138** |
| Functions matching provisional CODE boundary | 5,034 | **5,038** |
| Functions ending before provisional boundary | 552 | **548** |
| Unresolved conservative CFG edges | 43 | **21** |
| Total original/synthetic function entries | 5,635 | **5,635** |

**403** additional source instruction memberships were recovered across **15 original functions**, and **zero function entries lost** any previously reachable instructions. `Draw_Visible_Fields_Back_` gained 132, `Draw_Multi_File_Animation_` gained 66, `Farload_Library_` gained 33, `Replace_Color_`, `Replace_Color_All_` and `Replace_Color_Gradient_` each gained 24, `Disable_Draw_Field_` gained 20, and `Get_Video_Total_Memory_` gained 18. The remaining original branch restart sites recovered the shorter tails of nine additional named code functions. This is tracked source control-flow progress, not a semantic whole-game completion percentage.

## Remaining unresolved edge classification

The **remaining 21 conservatively unresolved CFG edges** are attached to only **16 symbol entries**, rather than the large ordinary gameplay/drawing functions already resolved:

- **Data-labelled or likely non-executable intervals:** `_max_planet_flags`, `_flag_replacement_colors`, `_climate_maintenance_modifiers`, `_Alphabet`, `_netLobby`. These require further actual Watcom CODE-vs-data type evidence before being marked executable or excluded. Do not turn data byte sequences into fictitious x86 functions for better metrics.
- **Startup/memory-marker entries:** `_cstart_`, `___GETDSEnd_`, `anon_runtime_0012F1D8`, `__SegmentStartRR16`, `__SegmentEndRR16`, `__SegmentStartPC32`, `__SegmentEndPC32`. Some are symbols at pure marker/zero-length runtime boundaries or branches to special startup stubs; do not claim they are fully decoded C functions.
- **Low-level runtime interrupt/video code, potentially not 32-bit-mode source:** `__IrqDataArrayRR16`, `__VideoBasePD16`, `__GreenleafFastRealIsr`, `__RealDispatcherRR16`. Their actual 16-bit-mode/relocation behavior requires separate toolchain verification before force-decoding in the standard Watcom i386 CODE pass.

These are classifications and hypotheses, not proofs that every remaining source byte is data or that the original game is semantically complete.

## Reproduction and trust boundaries

`tools/audit_direct_branch_resync_v131.py` authenticates original DOS EXE and original CODE hashes; all 16 independently original-byte-validated direct branch sites and target addresses; no branch into a verified inline table; exact 205 original switch tables and 1,625 authentic case DWORD targets; immutable Git baseline `4882a69f0e2b73c0afd2a90cd51af46347a85b03`; unchanged 5,635 function identities; per-function before/after instruction membership and source status; zero lost members; and the exact 21 residual unresolved CFG edges. Evidence is `decompilation/reports/direct_branch_resync_v131_2026-10-16.json` along with newly regenerated `decompilation/resynced_disassembly.json`, `decompilation/function_cfg_extents.csv`, `.json`, and full annotated provenance in this note. The large original disassembly and membership raw data remain local-only.

**Limitations:** original DOS live runtime differential tests have not been run. Machine-code CFG instruction memberships are not individually proven original gameplay semantics, compilable reimplementation, whole-executable completion or a playable native browser game. The unsupported earlier 87% and 88% semantic decompilation claims are not restored. No original executable, protected art, website or server configuration has been changed.
