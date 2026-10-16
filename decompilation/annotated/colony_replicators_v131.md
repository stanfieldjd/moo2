# Colony_Replicators_ — v1.31 authenticated stage reconstruction

## Original-source identity

- Original official local `ORION2.EXE` v1.31 SHA-256: `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
- Original derived Watcom LE CODE SHA-256: `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`.
- Watcom symbol `Colony_Replicators_`: CODE `0xCF66F..0xCF8C0` inclusive, 594 bytes, full original body SHA-256 `3f8ba1af2428e08626ee378742b5045e0e9a8d6bb0a80dd5635dd27fd3bf5447`. Extent cross-checked with `decompilation/functions.csv`.
- The function's direct source caller `Pre_Import_Computing_` calls CODE `0xCF66F` from CODE `0xD1DD7`; source caller was independently authenticated in `tools/audit_pre_import_computing_v131.py`.
- Shared return tail: CODE `0xD1F97`, outside this named function's original 594-byte range.
- Reproduce: `tools/audit_colony_replicators_v131.py --exe <official v1.31 EXE> --code <verified LE object 1>`. Test evidence in `decompilation/reports/colony_replicators_v131_2026-10-16.json`.
- No executable or proprietary game assets are included in version control.

## Source-observed stages and exact branch order

All findings below refer to original x86 instructions. The names `spent`, `used`, `budget`, `demand`, and `capacity` describe the arithmetic *mechanically*; they do not establish game-design terminology or the validity of arbitrary input memory.

- `0xCF67A`: always reset colony BYTE `+0x114` to zero.
- `0xCF681–0xCF688`: if BYTE `+0x146` equals zero, **return immediately** through the common tail. Original WORD `+0xE9` and WORD `+0xE7` remain unmodified.
- `0xCF68E–0xCF6BC`: load WORD `+0xE9` into DI and WORD `+0xE7` into SI, double each relevant 16-bit value, compute first signed-half capacity from `2*(WORD+0xE9) - BYTE+0x100`. Initialize ECX accumulator to zero. If the capacity is nonpositive, jump straight to final accounting.
- `0xCF6C2–0xCF6FF` (stage 1): use BYTE `+0xFC` minus doubled WORD `+0xE7` to produce signed-half demand. For a positive demand, cap twice the demand by first capacity, round the allocation down to an **even** value and accumulate it into ECX; advance the doubled-used accumulator and reduce the resource accumulator by half the allocated amount.
- `0xCF6FF–0xCF72D`: recalculate capacity after subtracting BYTE `+0x100`, `+0x101`, `+0x102` from the updated resource accumulator. Nonpositive capacity jumps directly to final accounting.
- `0xCF733–0xCF77F` (stage 2): demand comes from BYTE `+0xFC + BYTE+0xFD - used`; apply the same positive-demand, capacity-capped, even-allocation process and update the accumulators.
- `0xCF77F–0xCF7B7`: subtract four capacity counters `+0x100..+0x103`, divide signed low WORD by two, and if nonpositive jump to final accounting.
- `0xCF7BD–0xCF815` (stage 3): demand comes from BYTE `+0xFC + BYTE+0xFD + BYTE+0xFE - used`; cap and allocate even amounts as in stages 1 and 2, updating the accumulators.
- `0xCF815–0xCF84A`: calculate next remaining capacity after all four capacity counters. Nonpositive result jumps to final accounting.
- `0xCF84C–0xCF893` (stage 4): demand comes from BYTE `+0xFD + BYTE+0xFC + BYTE+0xFE + BYTE+0xFF - used`. Only ECX total-spent accumulator is increased by this final even, capacity-limited allocation.
- `0xCF895–0xCF8BC`: halve the signed low WORD of ECX using original `CDQ; SUB; SAR` truncation, write its low BYTE to `+0x114`; subtract ECX low WORD from WORD `+0xE9`; add the half amount to original WORD `+0xE7`; jump to common return CODE `0xD1F97`.

For nonnegative bounded fixture inputs, define `T(x) = (x + (x<0 ? 1 : 0)) >> 1` (signed division by two truncating toward zero). Positive stage demand is obtained with the original `CWDE; INC; CDQ; SUB; SAR` sequence. Four ordered stages select even increments `2*T(min(2*positive_demand, positive_capacity))`. Intermediate branch decisions use signed 16-bit forms of the original x86 registers at the observed `MOVSX`/`CWDE` points. The implementation in `tools/audit_colony_replicators_v131.py` models these steps **only for controlled synthetic non-overflowing ranges**.

## Control transfers and integrity

The authenticated 594-byte function contains **no nested CALL instructions**; all observed direct jumps remain inside the named body except for jumps to the shared epilogue at `0xD1F97`. The audit independently checks complete original bytes, source symbol extent, selected opcode and branch anchors, and permissible branch destinations.

Eight deterministic synthetic fixtures cover the disabled-feature early exit, zero-capacity exit, each of four distinct stages, capacity capping, multiple stages, and early negative capacity. The control model is tested against source-derived arithmetic identities. **No comparison against actual DOS execution was performed.**

## Remaining proof obligations

The correct in-game ranges of the three WORD fields and the meaning of the counter BYTEs are not established by this analysis; they require source-cross-referencing. Exact behavior for arbitrary invalid state, high-half Watcom register liveness, signed overflow and any external callers beyond the verified `Pre_Import_Computing_` call path is **not** claimed. This is a self-contained *static* instruction and control-flow reconstruction, not a finished native-game port.
