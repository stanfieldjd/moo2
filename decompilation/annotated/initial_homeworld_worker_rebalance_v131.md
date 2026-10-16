# v1.31 original initial home-world worker redistribution

## Source-authenticated scope

Official original `ORION2.EXE` v1.31 SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Extracted original Watcom LE CODE SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`.

`tools/audit_initial_homeworld_worker_rebalance_v131.py` and machine-readable `decompilation/reports/initial_homeworld_worker_rebalance_v131_2026-10-16.json` reproduce this audit of **six entire original named function bodies**, each with full-body SHA, original named extent, and byte-contiguous x86 instructions. Together: **1,396 instructions**, **77 targeted opcode anchors**, **10 direct CALL sites**, **1,170 bounded assertions**. The source contains some objdump continuation rows that are recombined before claiming contiguous decode.

Source functions and CODE locations:

| Named function | CODE offset | Authenticated size |
|---|---|---:|
| `Twiddle_Initial_Homeworld_` | `0xD55BE` | 530 |
| `Twiddle_Initial_Homeworlds_` | `0xD5832` | 693 |
| `Init_Homeworld_Colony2_` | `0x3A3D` | 1,386 |
| `Pre_Import_Computing_` | `0xD1D59` | 198 |
| `Pass_Out_Imports_` | `0xCF8F0` | 1,238 |
| `Colony_Job_Production_` | `0xCE280` | 996 |

Original global DATA `_colony` at `0x1AB18` and per-colony record stride `0x169` are independently source authenticated.

## Source record layout and job reallocation

Original `Init_Homeworld_Colony2_` gives each colonist a packed entry at colony `+0x0C + i*4` for `i` from zero to original colony population BYTE `+0x0A - 1`. That initial assignment can allocate several different jobs. Original `Colony_Job_Production_` tests participation bit **9** and its requested job selector against packed bits **7–8**, so those fields directly control numeric worker production.

Later, `Twiddle_Initial_Homeworlds_` steps backward through existing colony records (CODE `0xD5862`) and CALLs `Twiddle_Initial_Homeworld_` at CODE `0xD586A`.

At the start of the latter procedure, CODE `0xD55C5` obtains pointer `colony+0x0C`, CODE `0xD55C8` reads population BYTE `colony+0x0A`, and CODE `0xD55D1–0xD55DF` computes the packed-entry end pointer `start+4*count`. The backward initialization loop at `0xD55E3–0xD55F1` **changes every counted worker to research job 2**. Each iteration:

```text
entry DWORD low WORD &= 0xFE7F    // clear job bits 7 and 8
entry BYTE + 1       |= 0x01     // set packed job bit 8 => job 2
```

The mask `0xFE7F` clears exactly `0x0180`, the job fields, and **does not clear participation bit `0x0200`**. The exact population count governs how many entries are reset; the zero-count reverse loop itself does no iteration.

Following the reset, original CODE `0xD561A` CALLs `Pre_Import_Computing_`, then CODE `0xD5626` CALLs `Pass_Out_Imports_`, before the subsequent balance loops.

## Four subsequent conditional stages

| Source stage | Original guard; comparisons operate on specified original field widths | Change |
|---|---|---|
| First industry assignment, CODE `0xD562B–0xD5657` | Cursor before end; **unsigned BYTE** `+0xF0` zero-extended to AX greater than **signed WORD** `+0xE9` | Clear bits7/8, set bit7 => **job1 industry** |
| Conditional food assignment, CODE `0xD5659–0xD5690` | Original BYTE `+0xDD !=0`, cursor before end; unsigned BYTE `+0xEF` greater than signed WORD `+0xE7` | Clear bits7/8 => **job0 food** |
| Second industry balancing, CODE `0xD5692–0xD56C2` | Cursor before end; **signed WORD** `+0xE9` less than signed WORD `+0xEB` | Clear bits7/8, set bit7 => **job1 industry** |
| Final possible return to research, CODE `0xD56C4–0xD56EC` | Signed WORD `+0xEB <= +0xE9`; source decrements cursor **4 bytes before** changing an entry | Clear bits7/8, set bit8 => **job2 research** |

These are the literal original x86 conditional branches. For the first three stages, the signed comparison is significant: `JLE` and `JGE` interpret their 16-bit operands as signed even though the stage's 8-bit field is zero-extended into AX. The source audit validates those distinctions, including `WORD 0xFFFF` treated as **-1**.

Each iteration's numeric guards are **not invariant**. Exact original direct CALL sites to `Pre_Import_Computing_` are `0xD561A`, `0xD564C`, `0xD567E`, `0xD56B2`, and `0xD56E4`. Exact direct CALL sites to `Pass_Out_Imports_` are `0xD5626`, `0xD568B`, `0xD56BD`, and `0xD56EC`. These named original functions themselves have fully SHA-authenticated and contiguously decoded original bodies, and their call graph is checked against `decompilation/game_call_edges.csv`.

Because the original program re-evaluates colony production and imports along the way, it is **invalid** to run all phases against one frozen snapshot of output values and call that final DOS behavior. `0xD56D4` decrements the cursor before its last reassignment without a new explicit cursor-start guard in that immediate block; source provenance does not by itself establish safety under artificial states.

## Bounded test model and remaining evidence

Controlled fixtures check all worker job representations, preservation of non-job packed bits and active participation, reverse initialization for population sizes 0–15, exact signed/unsigned stage-guard truth tables including signed boundaries, and stage-specific job changes. They do **not** invent changing outputs of colony production or imports. The entire 1,170-check fixture suite is reproducible.

**Verified:** source initial all-research reset, precise packed job bit mutations, four subsequent branch predicates, original source call ordering and recalculation/import dependencies.

**Not established:** an exact final distribution for all initial configurations; legal full race/government/planet/player combinations in an official savegame; a DOS original runtime differential for the previously identified report-buffer-to-research-total path. No change to the original game rules, source executable, proprietary assets or native remaster implementation is claimed. The older 87% whole-executable completion estimate is not recalculated.
