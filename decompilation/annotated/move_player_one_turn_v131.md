# MOO2 v1.31 — source-derived one-turn movement, nebula and warp checks

**Status:** Source-backed reconstruction of the entire **422-byte**
original Watcom `Move_Player_1_Turn_To_Star_` routine, its
two named environment checks, one anonymous per-nebula
bitmap test, and previously reconstructed original `isqrt_`.
For **valid game-format map inputs and movement speeds**, the
reconstructed coordinate arithmetic and environment membership
conditions are in C, not opaque simulation callbacks.

This is **not original MicroProse source**, and no
dynamic differential comparison against the running DOS game
has been performed. Original game executable and artwork
remain private and are not included in the repository.

## Original authenticated executable

Original `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

| Original source CODE function / routine | Original CODE offset | Bytes | Source-body SHA-256 |
| --- | --- | ---: | --- |
| `Move_Player_1_Turn_To_Star_` | `0xDBB0C` | 422 | `01baaeca994622f9d2d56541ef9b5a5463ffdd619a20054c34c4230e8e2c64cb` |
| Anonymous per-nebula point lookup | `0xDB9C8` | 114 | `4cc37fb9b315c032a08140ed6bb70828d18cbab39d92f13629297a5ffc7e34a8` |
| `Point_Is_In_Some_Nebula_` | `0xDBA3A` | 66 | `78203712436446f44a76e139d6b3a899fda9595d48ad58a0d415441ba558f307` |
| `Point_Is_In_Warp_Field_Interdictor_Of_Star_` | `0xDBAC3` | 73 | `c9c753a493dd59543b8929aadcc4ea4e02bdfad1ca32c227074b91a22dbfb305` |
| `isqrt_` | `0x124C92` | 155 | `712fab862da65b98b408b6bcaf4da8352fdb00306b0e40dfeeae616211d6c1b8` |

`tools/audit_move_player_one_turn_v131.py` independently
validates all five original source-body SHA-256 digests,
four named Watcom symbol extents, four named DATA globals,
and **124 exact original x86 instruction locations**
from the authenticated executable's LE CODE object.
The report is `decompilation/reports/move_player_one_turn_v131_2026-10-15.json`.

The named DATA globals are original `_nebula` at
`0x1B068`, `_nebula_pict_seg` at `0x18298`,
`_NUM_NEBULAS` at `0x21F0D`, and `_star`
at `0x1B06C`. The per-nebula pict pointer
is loaded from `_nebula_pict_seg + 16*index+12`
(source direct memory operand `0x182A4+16*index`).

## Original movement function

The original ABI passes owner in EAX, current X in EDX,
current Y in EBX, and destination star ID in ECX.
Five original stack arguments are speed, mutable X*,
mutable Y*, optional nebula-status BYTE*, and mandatory
warp-field-status BYTE*. Source exit returns using
`RET 0x14`.

The original computes the target star's signed coordinates
from 113-byte star records at offsets `+0x0F,+0x11`.
It compares to signed low-WORD current X/Y. The original
squared distance is 32-bit arithmetic
`dx*dx+dy*dy`, and source code at `0xDBB66`
calls original `isqrt_` to obtain the integer
floor square root of that value.

For source movement steps `t=1..speed`, the
original follows these branches:

- Compute `t*t*900`. If signed comparison shows this
  has reached or exceeded the original squared
  distance, write the target star coordinates
  into mutable X/Y and set the local arrival marker.
- Otherwise compute unsigned magnitude increments
  `(t*30*abs(dx)+isqrt-1)/isqrt` and
  `(t*30*abs(dy)+isqrt-1)/isqrt`,
  using original signed division truncating to zero.
  Add or subtract the increments from the
  **initial coordinates**, write the low WORD
  of each output coordinate, and continue.
- **If an optional nebula-status pointer is supplied**
  and the new position lies inside a qualifying
  nebula bitmap, set a local nebula flag and exit.
  On exit the source writes 1 to the supplied
  optional status BYTE.
- Otherwise call original
  `Point_Is_In_Warp_Field_Interdictor_Of_Star_`
  using current position, target star record,
  and owner-bit exclusion. If it returns 1,
  set mandatory warp flag to 1 and exit.
- Otherwise stop on arrival, exhaustion of the
  allowed number of substeps, or source stop flags.

The mandatory warp-status BYTE is explicitly initialized
to 0 at the beginning. A zero speed in the original
low 16 bits is treated as one step.

**Unusual source corner case preserved:** Original CODE
`0xDBBA8` sets WORD `[EBP-0x0C]` to zero
on the direct-arrival branch; earlier CODE
`0xDBB18` had saved the input owner at that
stack location. The warp helper later reads the
signed **low WORD** of that local. Consequently,
on an arrival candidate the owner exclusion
argument becomes 0; on intermediate candidates
it remains the input owner. This nonintuitive
behavior is preserved because it is in the
machine instructions, not inferred gameplay design.

## Per-nebula bitmap membership

Anonymous CODE `0xDB9C8` accepts coordinates and
a nebula index. The original `_nebula`
array uses **five-byte** nebula records containing
signed origin WORDs X/Y at `+0,+2`.
The code subtracts the nebula origin and divides
each signed difference by **3**, with original
signed division's *truncation toward zero*.
It then reads a bitmap pointer out of
`_nebula_pict_seg`'s 16-byte records,
checks signed bitmap width and height from
its first two WORDs, and reads cell BYTE
`+0x10+cell_y*width+cell_x`.
**Cell values strictly greater than 5** count
as nebula. A cell value of 5 does not.

The named 66-byte
`Point_Is_In_Some_Nebula_` at CODE
`0xDBA3A` loops nebula indices 0 through
unsigned BYTE `_NUM_NEBULAS-1`, returning
1 as soon as any individual bitmap test
succeeds, otherwise 0.

No original copyrighted bitmap pixels were
committed; tests use synthetic in-memory grids.

## Warp-field test

The full 73-byte named
`Point_Is_In_Warp_Field_Interdictor_Of_Star_`
at CODE `0xDBAC3` loads original star
owner bitmask BYTE `+0x39`, masks out
`1<<excluded_owner` using the original
byte shifts/NOT, and returns false if no
other player's bit remains.

Otherwise it computes squared signed WORD-coordinate
distance to the star's location. Source compares
with `0x1FA4 = 8100` using a signed
32-bit comparison, so the normal in-game
radius threshold is **90 coordinate units,
inclusive**. The C implementation preserves
the original 32-bit result-bits arithmetic
before the signed comparison and checks
valid in-game owner indexes 0..7.

## Committed derived source and regressions

- `decompilation/reconstructed/move_player_one_turn_v131.c`
- `decompilation/reconstructed/point_in_nebula_v131.c`
- `decompilation/reconstructed/point_in_warp_field_v131.c`
- `decompilation/reconstructed/isqrt_v131.c`
- Matching `.h` interfaces for the three helper modules
- `tests/test_move_player_one_turn_v131.c`
- `tests/test_point_in_nebula_v131.c`
- `tests/test_point_in_warp_field_v131.c`
- `tests/test_eta_with_recovered_movement_v131.c`
- `tests/test_building45_full_original_movement_v131.c`
- `tools/audit_move_player_one_turn_v131.py`
- `decompilation/reports/move_player_one_turn_v131_2026-10-15.json`

Movement tests cover signed diagonal and axis-aligned
projection, exact arrival, source owner-bit
overwriting on arrival, optional nebula
early-stop behavior, and 500 axis-aligned
distance cases. The per-nebula tests
exhaust all 256 possible synthetic bitmap
values at each cell and test the original
three-coordinate cell scaling, negative
division rounding, and multiple-nebula scan.
Warp tests cover **eight owners x 256 masks
x nine coordinate cases**, including radius
boundary.

The ETA integration uses only these
source-derived C functions and the existing
reconstructed 253-byte
`Update_Ship_ETAs_` outer scan:
**80 owner/state/speed combinations**
plus a **1,000-turn** journey verifying that
only the low byte of the original 16-bit
turn count is stored as the ship ETA.

Finally,
`tests/test_building45_full_original_movement_v131.c`
integrates the earlier original building-45
presence-bit removal, complete 311-byte
`Compute_Star_Colony_Stuff_`, full
`Update_Ship_ETAs_` loop, this recovered
full movement step, and the environmental
helpers. It passes **80 end-to-end
source-consistency cases** with no substitute
gameplay-movement callback.

These were compiled under **strict C11
with AddressSanitizer and UndefinedBehaviorSanitizer**.

## Limitations and next work

Machine-code dataflow and the original helper-body
hashes are verified. Host pointer/index checks,
a speed bound, and controlled handling of malformed
object records are deliberate differences from
undefined or unsafe DOS execution. Precise
game equivalence is still unproven without
**dynamic DOS differential test vectors**
captured from original executable state;
the source-consistency tests do not replace that.

The larger game still has many original functions
without complete C reconstructions, including
remaining `Remove_Building_` branches,
other strategic ship commands and fleet,
combat, turn progression, galaxy, and save/load
systems. The browser Game Lab version remains
non-playable. No production Game Lab,
Xbox controller or Qwen changes were made.
