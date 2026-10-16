# Original MOO2 v1.31 Colony_Job_Production_ per-entry multiplier reconstruction

## Source identity and scope

Original executable: official local MicroProse v1.31 `ORION2.EXE`, SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Derived original Watcom LE CODE, SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. No game binary or proprietary assets are committed.

Full named source body `Colony_Job_Production_`: original CODE `0xCE280`, **996 bytes**, full SHA-256 `853acbdf8e5057e9ad4f3a34c7f5aa98392c668eee1568f8133995ca5d641860`. The original source full-body control-flow audit already exists in `tools/audit_colony_job_production_v131.py`; **this separate audit deepens the previously unresolved per-population production-modifier arithmetic** at CODE `0xCE390–0xCE61E`.

Reproduction: `tools/audit_colony_job_worker_modifiers_v131.py --exe <original v1.31 EXE> --code <original Watcom LE CODE object>`. Machine-readable evidence: `decompilation/reports/colony_job_worker_modifiers_v131_2026-10-16.json`. The audit authenticates the entire procedure source bytes, 283 decoded instructions and 62 direct call/branch transfers, 80 distinct decisive opcode anchors, original settings-record identity and 41 bounded controlled fixtures.

## 1. Source packed-entry eligibility, job and population tag

Original CODE `0xCE376–0xCE3B3` walks the colony's population entries as DWORDs **in reverse order**. For each packed DWORD entry:

- Source `TEST BYTE [EDI+1],0x2` at `0xCE393` requires **bit 9** of the packed entry to be set. Otherwise this entry contributes nothing to this job-production loop.
- Source `SHL EDX,23; SHR EDX,30` extracts packed **bits 7 and 8**, an unsigned two-bit selector; only entries matching the job selector 0 (food), 1 (industry), or 2 (research) enter the calculation.
- Source `entry & 0xF` at `0xCE3B3` supplies the population tag passed to the original `Gravity_Player_Production_Factor_` and `Colony_Pop_Base_Prod_Produced_` routines.

The audit models these bit selections explicitly and limits tag fixtures to 0..9. Job type 3 is outside the three verified source callers and is not assigned gameplay semantics.

## 2. Original work-component multipliers

Let `B` be the signed low-WORD per-entry production value returned by `Colony_Pop_Base_Prod_Produced_`; `G` is the source gravity factor returned from `Gravity_Player_Production_Factor_` (source-derived bounded outcomes 2, 3 or 4). Let `L` be the local leader bonus computed through `Colony_Officer_` and `Owned_Officer_Level_`, and `M` the signed colony morale BYTE at `+0x07`. These are **external original helper results/state**, not newly invented numeric constants.

For bounded values without signed x86 overflow, the original named-body instructions calculate the following independent components for an eligible population entry:

| Original CODE | Source contribution before aggregation |
|---|---|
| `0xCE479–0xCE485` | `+20 * B` |
| `0xCE4A7–0xCE4BC` | `-5 * (4 - G) * B` |
| `0xCE4BF–0xCE4CC` | `+L * B` |
| `0xCE4CF–0xCE4DE` | `-5 * B` if packed entry BYTE `[EDI+1]` has bit `0x4` set (packed DWORD **bit 10**) |
| `0xCE4E1–0xCE4FD` | `+M * B` when morale is enabled |
| `0xCE500–0xCE5A3` | `+government_adjustment(job,government_group) * B`, plus a separate source owner/star flag for jobs 0 or 1 |
| `0xCE5A6–0xCE5D0` | Optional **unscaled signed-byte** production setting `S`, **not multiplied by B** |
| `0xCE609` | An additional original breakdown component inherited from the nested population-production helper; its distinct source lifetime is not re-derived in this packet |

Government group is the original source signed government BYTE `player[owner].BYTE+0x89F`, divided by two with the source's signed truncation sequence. For **food and industry** (job 0/1), government group 6 gives `+10*B` and group 7 gives `+20*B`; other bounded groups give 0. An independently derived owner/star state flag contributes `-10*B` on those two job types when set.

For **research** (job 2), the original group-specific contribution is:

| Government group | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| Multiplier of B | -10 | -5 | 0 | 0 | +10 | +15 | 0 | 0 |

The source original `0xCE385–0xCE387` disables the morale term when government group equals 3. Separately, CODE `0xCE488–0xCE4A3` disables the morale term for **population tag 8 on food/research**, but leaves it enabled for industry (assuming group !=3). Population tag 9 is not suppressed by that rule. These two independent guards must both be preserved.

## 3. Original signed CODE-indexed settings table

The signed settings contribution `S` is present only when original owner-player BYTE `+0x28` is **not** decimal 100. Source `0xCE5BC` loads the selector from original **DATA** `0x21CB0`, which is a field at `+0xD4` within the original named DATA `_settings` record beginning `0x21BDC`. Original `0xCE5C3` sign-extends a BYTE from original **CODE** at `0xCD4D7 + selector`, with no in-body bounds check.

The exact 15-byte source CODE slice is `[246,0,10,20,40,5,8,10,15,20,2,4,6,8,10]`. In signed-byte form: `[-10,0,10,20,40,5,8,10,15,20,2,4,6,8,10]`, SHA-256 `348ad136315e48429a9a5c1d1be7c999dcbe1d34abd267e26a4615d08d38e522`. An unverified table selector at or beyond index 15 is **not** modeled. The table is described by its original address rather than assigned an unproven symbol name.

## 4. Original signed accumulation and final division

Source `0xCE5D3–0xCE61B` sums the independent per-entry contributions (and an inherited original nested-helper component) into a **signed 32-bit** worker total `W`. An initialized but otherwise unchanged breakdown component also participates in the ADD sequence; for normal zero-initialized frames this is zero. Crucially, it then performs `TEST EDX,EDX; JLE ...; ADD [aggregate],EDX`: **only when W is strictly positive** is W added to the job's aggregate.

The larger original routine finishes by optionally copying **0x256 bytes** of accumulated per-worker breakdown state to the caller's buffer, then performs original signed `IDIV`: for food, `(aggregate + 20)/40` truncating toward zero; for industry/research, `(aggregate + 10)/20` truncating toward zero. That final arithmetic was independently audited earlier.

The source has no evidence here of independent worker-level saturation, and the raw signed worker contribution is retained even when it is excluded from the aggregate. The controlled model has an explicit positive-only addition and validates each multiplier independently, government/morale guards, negative settings contributions, packed-entry bit selection, and negative worker-gate exclusions.

## Confidence and limitations

**Verified from original bytes:** authentic full function, 283 contiguous decoded instructions, 62 control transfers, 80 selected exact machine instructions spanning all arithmetic gates, original CODE settings table, DATA settings record, packed bit-selection, original sign-extension/multiplication and positive-only aggregate gate.

**Still unverified:** whether any out-of-domain table selectors occur in genuine states; comprehensive helper-return or leader/planet state lifecycle; signed 32-bit wraparound outside bounded fixtures; actual original DOS-runtime differential output and eventual native-game parity. The C-like formula is an **analyst reconstruction from original machine instructions**, not the game's original source or a newly completed native engine. Previously recorded 87% whole-executable completion estimate has not been remeasured.
