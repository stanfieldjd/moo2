# REA/Ghidra v1.31 bounded production-function audit

## Purpose and source

This is a read-only examination of the original Master of Orion II v1.31 LE executable, SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Tools: REA 6.4.0 through ChatGPT MCP and Ghidra 12.1.4. The real game and reconstructed machine-code images remain local and uncommitted. See [the relocation research record](rea-ghidra-le-v131-2026-10-12.md).

The derived *static analysis* ELF32 SHA-256 is `5afad26278a40de4c0cecf9047dff2e3bb4d7993bcff43d03df24d475c4efeec`. It maps 28 KiB of relocated gameplay code at virtual `0xdd000..0xe4000` and initialized/BSS data at `0x170000`. This is not the game executable and does not run the DOS game.

## Direct function observations

All of the following were returned by direct REA `analyze_function` calls in the bounded Ghidra session, with pseudocode and assembly available. "Bytes" refers to Ghidra's observed function-body byte count. No bad-instruction warning was returned for these queries.

| Watcom symbol | Preferred virtual entry | Bytes |
| --- | --- | ---: |
| Colony_Food2_Per_Farmer_ | `0xde03e` | 136 |
| Colony_Job_Production_ | `0xde280` | 996 |
| Colony_Food_Production_ | `0xde664` | 1209 |
| Show_Food_Production_ | `0xdeb1d` | 46 |
| Colony_Food_Maintenance_ | `0xdeb4b` | 330 |
| Colony_Industry_Per_Worker_ | `0xdec95` | 178 |
| Colony_Industry_Production_ | `0xdee1b` | 1789 |
| Colony_Industry_Maintenance_ | `0xdf546` | 297 |
| Colony_Research_Per_Scientist_ | `0xdfdc6` | 177 |
| Colony_Research_Production_ | `0xdff74` | 1103 |
| Colony_BC_Production_ | `0xe03f1` | 1239 |
| Colony_Industry_To_Tax_ | `0xe08f6` | 89 |
| Planet_Max_Population_For_Player_ | `0xe0b4f` | 206 |

Each recovered extent matches the interval to the next CODE symbol in the original Watcom global-symbol table; this was checked against the hash-matching original file locally. **Important qualification:** Ghidra received symbol-entry labels from the same Watcom source when building the ELF container. This is a structural consistency check, not an independent discovery of the true program-function boundaries.

## Call relationships observed

Ghidra reported these direct calls within this bounded window:

- `Colony_Industry_Production_` to `Colony_Officer_`, `Format_Quotient_`, and `Colony_Job_Production_`.
- `Colony_Research_Production_` to `Format_Quotient_` and `Colony_Job_Production_`.
- `Colony_BC_Production_` to `Colony_Officer_`.
- `Colony_Job_Production_` to `Colony_Officer_`, `Gravity_Player_Production_Factor_`, and `Colony_Pop_Base_Prod_Produced_`.
- `Show_Food_Production_` to `Colony_Food_Production_`.

The underlying code uses original Watcom register conventions. Decompiled text may contain invented type names, inaccurate parameter guesses, unknown indirect calls, or incorrect aliases; do not implement gameplay solely from this pseudocode. Out-of-window target code is not proved by a reported call edge alone.

## Shared-epilogue correction

The first 16 KiB population analysis window omitted an outgoing branch target at `0xdeb17`. Expanding the mapped window to 28 KiB enabled Ghidra to follow that shared exit sequence `LEAVE, POP EDI, POP ESI, POP ECX, POP EBX, RET`, removing the earlier bad-instruction warning. The directly inspected bytes are `c9 5f 5e 59 5b c3`.

A deterministic local regression in `tools/run_tool_tests.sh` verifies that the wider ELF includes the exact bytes at the correct preferred virtual address. The test suite passed on the authenticated original. See [the shared-epilogue note](rea-v131-shared-epilogue.md).

## Persistence and reproducibility

A local REA snapshot was saved after these analyses: 23,389,026 bytes, 13 replayable primitive entries, 15 evidence records, SHA-256 `e46254e9529790d6da7cb4417da968d40b7cb424d87702ca69dd4771f5ed3343`. This snapshot is deliberately not committed because it contains provider analysis output. To reproduce analysis from lawful local source, use `tools/relocate_le_v131.py`, `tools/build_rea_window.py`, and `tools/run_tool_tests.sh`.

**Remaining uncertainties:** full LE control-flow coverage, every runtime relocation effect, indirect calls, Watcom calling conventions, and game-equivalent rule execution. No source code for a native game has been claimed or committed; no Qwen integration was performed.
