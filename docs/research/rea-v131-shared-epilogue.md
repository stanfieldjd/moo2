# MOO2 v1.31: cross-function population-limit epilogue

## Scope and provenance

Static analysis of the hash-verified MicroProse v1.31 executable (SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`). Tools: REA 6.4.0, Ghidra 12.1.4, locally reconstructed LE32 code/data images and applied internal LE relocations. See `rea-ghidra-le-v131-2026-10-12.md` for detailed source provenance. No game code or proprietary assets are included here.

## Observed problem and root cause

The initial 16,384-byte window at virtual `0xe0000..0xe4000` returned an invalid-instruction warning for Watcom symbol `Planet_Max_Population_For_Player_` at `0xe0b4f`. Disassembly identified a direct jump at `0xe0c18` targeting `0xdeb17`, outside that selected window.

Independent examination of the underlying LE object found these source bytes at `0xdeb17`:

`c9 5f 5e 59 5b c3`

Disassembled as: `LEAVE; POP EDI; POP ESI; POP ECX; POP EBX; RET`.

The target is inside `Colony_Food_Production_`, whose entry is `0xde664`, and immediately precedes `Show_Food_Production_` at `0xdeb1d`. It is a shared tail/epilogue, **not an invalid instruction**.

## Correction and verification

Built a bounded synthetic analysis ELF32 using `tools/build_rea_window.py` with `--first-page 205 --page-count 7 --entry-symbol Planet_Max_Population_For_Player_`. The code is mapped at `0xdd000..0xe4000`, exclusive upper bound. ELF SHA-256: `5afad26278a40de4c0cecf9047dff2e3bb4d7993bcff43d03df24d475c4efeec`.

A direct REA/Ghidra call recovered `Planet_Max_Population_For_Player_` (206 bytes) **without the prior warning**, with a normal return in decompiled pseudocode. Another direct analysis verified `Colony_Food_Production_` spans 1,209 bytes through the shared epilogue, with `Show_Food_Production_` starting at the next address.

The regression in `tools/run_tool_tests.sh` reconstructs this expanded window, validates its hash and verifies that `0xdeb17` contains the six expected instruction bytes. That test passed locally against the official hash-matching executable, and the updated test runner was committed as `55854669be684ea41164117179ed622600341f74`.

## Additional direct function evidence

The following function body extents were returned by Ghidra from the bounded analysis window:

| Symbol | Virtual entry | Body bytes |
| --- | --- | ---: |
| `Colony_Food2_Per_Farmer_` | `0xde03e` | 136 |
| `Colony_Job_Production_` | `0xde280` | 996 |
| `Colony_Food_Production_` | `0xde664` | 1,209 |
| `Show_Food_Production_` | `0xdeb1d` | 46 |
| `Colony_Food_Maintenance_` | `0xdeb4b` | 330 |

No bad-instruction warning was reported for these observed function queries. Direct call edges recovered include `Show_Food_Production_` to `Colony_Food_Production_`, and `Colony_Job_Production_` to `Colony_Pop_Base_Prod_Produced_`.

Six direct analysis results were saved into a local REA snapshot of 7,784,844 bytes, outside GitHub. Earlier recovered results and the original executable were retained separately.

## Verification status and limitations

**Verified:** SHA-256 of original source, LE relocation and image maps, exact shared-epilogue bytes, bounded ELF identity, the successful direct Ghidra queries, and the passing deterministic regression.

**Not established:** overall decompilation completeness, correct high-level gameplay semantics, full Watcom calling conventions, cross-window and indirect-call coverage, and DOS/4GW runtime behavior. Synthetic ELF is for static analysis only. Do not commit original or derived machine code to the repository; do not claim pseudocode is recovered original source.
