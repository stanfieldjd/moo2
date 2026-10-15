# MOO2 v1.31 — complete `isqrt_` and remaining ship-movement dependencies

**Status:** The original Watcom `isqrt_` routine at CODE `0x124C92` has been reconstructed completely as unsigned 32-bit integer arithmetic. It is a source-authenticated building block of `Move_Player_1_Turn_To_Star_`, not the whole ship-movement algorithm.

Original authenticated local `ORION2.EXE` SHA-256: `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

The original **155-byte** `isqrt_` full function body has SHA-256 `712fab862da65b98b408b6bcaf4da8352fdb00306b0e40dfeeae616211d6c1b8`. The source audit `tools/audit_isqrt_v131.py` checks the complete body checksum, exact original Watcom symbol extent, and **53 original x86 instruction checkpoints**. Output report: `decompilation/reports/isqrt_v131_2026-10-15.json`.

## Source-defined algorithm

The input is unsigned 32-bit EAX, and the result is unsigned integer floor square root, with a maximum output of 65,535.

The original machine code uses the following exact decisions:

1. For input at least `0xFFFE0001` (the square of 65,535), return 65,535.
2. For input at most 65,535, initialize binary-search bounds `low=0, high=256`.
3. Otherwise initialize `low=256, high=65535`.
4. Set `middle=(low+high)/2` rounded down. If the unsigned 32-bit `middle*middle` is no greater than input, assign `low=middle`; otherwise `high=middle`.
5. Repeat until `low+1>=high`, then return `low`.

The original prologue calls Watcom support stack-probe CODE `0x12F1E0`. The portable derived implementation does not need this stack-frame management operation, so it reconstructs the numeric algorithm only.

This is the original named callee of `Move_Player_1_Turn_To_Star_` at original movement CODE `0xDBB66`. That movement code first computes the sum of squared differences between a ship's current coordinates and its target star coordinates, then calls the authenticated integer-square-root function. The movement routine also invokes additional gameplay helper functions for coordinates and obstacles, and those effects are not covered by `isqrt_`.

## Source, independent tests, limitations

- `decompilation/reconstructed/isqrt_v131.c`
- `tests/test_isqrt_v131.c`
- `tools/audit_isqrt_v131.py`
- `decompilation/reports/isqrt_v131_2026-10-15.json`

The test uses an **independent digit-by-digit restoring integer-square-root reference**, not the original binary-search implementation, and checks every 16-bit input, all possible unsigned 16-bit root squares and their neighboring input values, 200,000 pseudorandom 32-bit inputs, and upper-end saturation boundaries. Strict C11/AddressSanitizer/UndefinedBehaviorSanitizer tests passed.

These are source-byte verification and host-function math regressions. They are not a differential execution of the original DOS executable.

**Outstanding movement work:** The authenticated original 422-byte `Move_Player_1_Turn_To_Star_` body contains the distance/coordinate projection loop and original named helpers `Point_Is_In_Some_Nebula_` (CODE `0xDBA3A`) and `Point_Is_In_Warp_Field_Interdictor_Of_Star_` (CODE `0xDBAC3`). The exact movement step, speed and rounding, obstacle handling, and callback replacement must be recovered with original source evidence before claiming game-equivalent ETAs. The ETA outer loop is independently source-reconstructed in `decompilation/reconstructed/update_ship_etas_v131.c` with its movement dependency deliberately exposed.

Original copyrighted binaries/media remain local. The GitHub changes do not alter the Game Lab public site, Xbox controller integration or unrelated Qwen service.
