# MOO2 v1.31 — Remove_Building_ direct star recalculation (IDs 3,14,45)

**Status:** The original `Remove_Building_` contains source-verifiable
direct branches for building IDs **3, 14 and 45**. These branches have
been recovered as safe, callback-bounded C dataflow. The original
`Compute_Star_Colony_Stuff_` and `Update_Ship_ETAs_` effects are
not reimplemented by the callbacks; neither is the full 493-byte
`Remove_Building_` function.

Local authenticated original `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
Original `Remove_Building_` CODE `0x45EA`, length **493 bytes**,
complete original function-body SHA-256
`8e0eb8d52268bf214d1ce3ec73d0e9970f0b4db1b0d1cae035810ace87179875`.

The source audit `tools/audit_remove_building_star_recalc_v131.py`
verifies that entire original function-body hash, **37 distinct original
instruction checkpoints**, both named helper calls and the exact
original DATA symbols. Evidence:
`decompilation/reports/remove_building_star_recalc_v131_2026-10-13.json`.

## Original branch conditions

The original function first clears the selected building's
presence BYTE at original `_colony +0x169*colony_id +
0x136+building_id` at CODE `0x460A`.

Original building-ID conditions then select the common direct
recomputation path at CODE `0x46D4`:

- **ID 3**, via comparison at `0x466E` and conditional
  jump at `0x463A`.
- **ID 14**, via comparison at `0x4668` and the
  same conditional jump at `0x463A`.
- **ID 45**, via comparison at `0x4636`
  and that conditional jump.

Other building IDs have different code paths.
In particular, IDs **8, 40 and 41** may reach the same
recomputation block only **after construction-queue cleanup**
at `0x4681..0x46D4`. They must NOT simply be treated
as direct recomputation IDs until that cleanup has been
reconstructed.

## Original colony -> planet -> star lookup

This branch also independently establishes the correct type of
original colony WORD `+0x02` and corrects an earlier
inferred label in the home-planet research:

1. Source `0x46E2` reads signed WORD colony `+0x02`
   as **planet index**. Source `0x46E7` multiplies it by
   `0x11` (**17-byte original planet-record stride**).
2. Source `0x46EA` loads original `_planet` DATA global
   at `0x1B0D4`. Source `0x46EF` reads unsigned
   BYTE `_planet[planet_id].+0x02` as **parent star index**.
3. Source `0x46F4` multiplies that star index by
   `0x71` (**113-byte original star-record stride**).
4. Source `0x46F7` loads original `_star` DATA pointer
   at `0x1B06C`; source `0x46FF` passes the computed
   star-record pointer in EAX to
   `Compute_Star_Colony_Stuff_` at CODE `0xD5296`.

The original shared branch at `0x4704` checks whether
the building ID is **45**. Only for ID45 does it
proceed to CODE `0x4713`, reread the colony's
signed owner BYTE and call `Update_Ship_ETAs_`
at CODE `0xF041C`. IDs 3 and 14 skip that
second callback and reach the shared
`LEAVE; POP EDI; POP ESI; POP ECX; POP EBX; RET`
at CODE `0x45E4`.

## Source-derived C and tests

- `decompilation/reconstructed/remove_building_star_recalc_v131.c`
- `decompilation/reconstructed/remove_building_first_write_v131.c`
- `tests/test_remove_building_star_recalc_v131.c`
- `tools/audit_remove_building_star_recalc_v131.py`
- `decompilation/reports/remove_building_star_recalc_v131_2026-10-13.json`

The C interface takes original-format colony, planet and star
record buffers and the two named helper callbacks. It
validates the signed planet index, unsigned star index,
buffer boundaries and required callbacks **before** the
first write, so invalid input does not leave the host
game state half-mutated. That is a safety addition,
not original DOS behavior.

Regression tests covered all three direct building IDs
across **256 planet-to-star index values**, callback
ordering (flag clear precedes `Compute_Star_Colony_Stuff_`),
and reading the owner BYTE **after** the star callback
for ID45. Queue-dependent building IDs 8,40,41 are
explicitly rejected by this isolated helper rather than
skipping missing original queue effects.

The regression passed strict C11 compilation with
AddressSanitizer/UndefinedBehaviorSanitizer. The original
source audit passed its 37 opcode checks. These tests
are not a dynamic run of the DOS original.

## Work remaining

Reconstruct the actual downstream implementations of
`Compute_Star_Colony_Stuff_` and
`Update_Ship_ETAs_`, and queue-specific paths
for original building IDs 8, 22, 40, 41, plus
other building-dependent economy and environment
effects. Only then can the source-reconstructed
building removal function replace the full
original behavior.

No proprietary original game executable or art was
published. The Game Lab website, Xbox controls,
and Qwen were not modified.

## Follow-on: complete source-derived star recalculation

Original `Compute_Star_Colony_Stuff_` at CODE `0xD5296` (311 bytes) is now reconstructed as C rather than left as an unknown callback. `decompilation/reconstructed/compute_star_colony_stuff_v131.c` rebuilds eight star-byte bitmasks from five planet slots, colony building flags and player feature bytes. `tests/test_remove_building_compute_star_integration_v131.c` uses the real derived C in the previously recovered direct ID 3/14/45 callback slot, exercising eight original owners and all three building removals. `Update_Ship_ETAs_` for ID45 remains a separate unresolved callback. See `decompilation/annotated/compute_star_colony_stuff_v131.md` and its full original-body hash/84-opcode audit.

## Follow-on: complete derived `Update_Ship_ETAs_` caller loop

The original ID45-only named callee `Update_Ship_ETAs_` at CODE `0xF041C` (253 bytes) is now independently source-audited and reconstructed as a bounded C loop in `decompilation/reconstructed/update_ship_etas_v131.c`. It reverse-scans the `_ship` records, skips ships with the same owner as the supplied EAX argument, decodes destinations from status 1/2 and `ship+0x65`, and calls original movement logic repeatedly to calculate the ETA byte `+0x6D`. The real 422-byte `Move_Player_1_Turn_To_Star_` remains an explicit callback. The integration `tests/test_remove_building45_star_eta_integration_v131.c` runs the actual reconstructed star-field recomputation followed by the full derived ship ETA loop across all eight player IDs, with a deterministic *test-only* movement callback. Original hashes and 76 x86 sites are verified in `decompilation/reports/update_ship_etas_v131_2026-10-15.json`. See `decompilation/annotated/update_ship_etas_v131.md`.
