# Colony_Job_Production_ — authenticated source control flow and return arithmetic

## Original-source provenance

- Official locally supplied `ORION2.EXE` v1.31 SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
- Derived original Watcom LE CODE SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`.
- **Complete named `Colony_Job_Production_` body**: CODE `0xCE280..0xCE663`, 996 bytes, SHA-256 `853acbdf8e5057e9ad4f3a34c7f5aa98392c668eee1568f8133995ca5d641860`. The named extent is verified against `decompilation/functions.csv`. It is an original code-byte provenance finding, not recovered original C source.
- Reproducible machine-byte, decoder, and branch audit: `tools/audit_colony_job_production_v131.py`; JSON evidence: `decompilation/reports/colony_job_production_v131_2026-10-16.json`. Pre-existing `analysis/Colony_Job_Production_.disasm` preserved unchanged.
- Audit verifies **283 complete contiguous decoded instructions spanning all 996 bytes**, **62 direct call/branch transfers**, **40 exact machine instruction anchors**, seven correctly combined disassembler continuation rows, the complete names/bytes of all five direct callee functions, and 15 bounded source-derived final arithmetic fixtures.

## Why the helper is critical

The original source directly invokes this function from `Colony_Food_Production_` (job-type **0** at CODE `0xCE6FA`), `Colony_Industry_Production_` (**1** at `0xCEEA5`), and `Colony_Research_Production_` (**2** at `0xCFFE8`). The caller-body audits prove the call targets and output WORD writes independently.

The helper **returns** a signed division result in EAX and does **not** directly write the caller's final colony production WORD. It can optionally populate a fixed-size breakdown buffer used by the text renderer.

## Machine-observed phases

- CODE `0xCE280–0xCE2B9`: establish Watcom frame and save the job-type selector (original EDX), breakdown pointer (original EBX), and colony pointer (original EAX). Resolve colony's planet record and player details through DATA globals `_planet`, `_player`, and other source records.
- CODE `0xCE2BB–0xCE376`: invoke `Colony_Officer_`; derive government and race/player flags; zero **0x256 bytes** of local per-source breakdown structure via `memset_`; inspect leader flags specific to job-type selector **0, 1, or 2** and conditionally call `Owned_Officer_Level_` up to three distinct original call sites. Do not assume this is one unconditional multiplier.
- CODE `0xCE376–0xCE3B3`: calculate end/start pointers over the colony's packed DWORD population entries, then traverse them **in reverse**. Job assignment is selected by packed entry flag bits, not simply the low nibble.
- CODE `0xCE3B3–0xCE61E`: call `Gravity_Player_Production_Factor_` (CODE `0xCDF2C`) and `Colony_Pop_Base_Prod_Produced_` (CODE `0xCE22C`); the worker loop contains numerous conditional original player/planet/race modifier branches and accumulates only positive per-worker totals into the aggregate at local `[EBP-0x2A]`. Complete exact source transfer targets are in the JSON report. **Game-rule meanings of every modifier and all valid input ranges have not been separately proved.**
- CODE `0xCE5A6–0xCE5D3`: conditionally add a source CODE-indexed modifier to a worker component when player BYTE `+0x28` is not decimal 100. The original setting reference DATA address `0x21CB0` is a *field inside* the `_settings` record whose base is DATA `0x21BDC`; the two addresses are not interchangeable.
- CODE `0xCE627–0xCE63B`: if an optional breakdown pointer was supplied, copy exactly `0x256` bytes from the initialized local structure using the original `REP MOVS` instruction. No game assets or formatter data are copied into Git.
- CODE `0xCE63D–0xCE663`: if job selector is **0**, source computes `IDIV ((aggregate + 20), 40)`; otherwise it computes `IDIV ((aggregate + 10), 20)`. `IDIV` is signed x86 division truncating toward zero, so blindly substituting unsigned division or saturation would change original behavior. It returns through its own `LEAVE/POP/POP/POP/RET` sequence at `0xCE65F–0xCE663`.

## Original nested call inventory and code identity

| Authenticated named callee | CODE address | Direct call sites | Original full bytes |
|---|---|---:|---:|
| `Colony_Officer_` | `0xCD9F2` | 1 | 68 |
| `memset_` | `0x119C70` | 2 | 24 |
| `Owned_Officer_Level_` | `0x84951` | 3 | 86 |
| `Gravity_Player_Production_Factor_` | `0xCDF2C` | 1 | 167 |
| `Colony_Pop_Base_Prod_Produced_` | `0xCE22C` | 1 | 84 |

Original full callee SHA-256 digests and all direct call/jump addresses are verified in the source-linked audit JSON.

## Limits and next step

This **closes the exact-body control-flow audit** of the shared job-production helper, but it is not the full original producer algorithm translated into native code. The next substantive work is to reconstruct `Gravity_Player_Production_Factor_` and `Colony_Pop_Base_Prod_Produced_`, then trace source-original modifier operations, player flag semantics and DOS differential behavior. The fixtures cover only the helper's final division in small non-overflowing synthetic states; they are not runtime observations.

Do not treat the nine completed caller-body audits or this shared helper audit as a new whole-executable completion percentage. No original game binaries, proprietary assets or guessed derived data have been committed.
