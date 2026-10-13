# MOO2 v1.31 — complete home-planet reassignment and original building-9 call

**Status:** Source-backed derived C reconstruction of the entire **146-byte**
original Watcom function `Assign_New_Home_Planet_`, connected to the
verified building-ID-9 branch inside the still-incomplete
`Remove_Building_`. Original DOS gameplay has **not** been differentially
executed. This is not the original MicroProse source.

## Original provenance

Authenticated local `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

| Original Watcom symbol | Original CODE offset | Complete body | SHA-256 verification |
| --- | --- | ---: | --- |
| `Assign_New_Home_Planet_` | `0xDCB65` | 146 bytes | `b246802362b4d87ded1ea4efca66c4adaa18aa67f3f8b0ba6ba79b34374efd05` |
| `Remove_Building_` | `0x45EA` | 493 bytes | `8e0eb8d52268bf214d1ce3ec73d0e9970f0b4db1b0d1cae035810ace87179875` |

`tools/audit_assign_new_home_planet_v131.py` authenticates both complete
original function bodies and **57 exact original opcode sites**.
Machine-readable evidence:
`decompilation/reports/assign_new_home_planet_v131_2026-10-13.json`.

## Original call path after removing building 9

`Remove_Building_` first clears the presence byte at
`colony+0x136+building_id` (original CODE `0x460A`).
For building ID 9, the field cleared is `colony+0x13F`.

The original caller then executes these significant instructions:

- `0x45F6 MOVSX EDX,AX`: preserve **signed original colony index**.
- `0x4674 MOVSX EAX,BYTE PTR [EAX]`: load **signed owner BYTE**.
- `0x4677 CALL 0xDCB65`: invoke `Assign_New_Home_Planet_`,
  retaining **EDX=excluded original colony index**.
- `0x467C JMP 0x45E4`: use a shared
  `LEAVE; POP EDI; POP ESI; POP ECX; POP EBX; RET` epilogue
  located inside the preceding `Add_Building_` symbol interval.

The first iteration of the derived building-9 callback interface
carried only the owner. Source inspection established that **EDX
also carries the colony index**, so the callback signature and tests
were corrected before considering the function verified.

## Fully recovered `Assign_New_Home_Planet_` dataflow

The original routine receives **EAX = owner** and **EDX = excluded
colony index**. It reads three named original DATA object-2 globals:

- `_NUM_COLONIES` at `0x21996`: signed WORD count.
- `_colony` at `0x1AB18`: pointer to 361-byte (`0x169`) colony records.
- `_player` at `0x1FF98`: pointer to 3,753-byte (`0xEA9`) player records.

The original source initializes selected colony index ECX to −1
and best population DWORD to zero. It scans the colony array
from **count−1 downward through zero**, excluding the colony ID
passed in EDX. It accepts only entries whose signed owner
BYTE `colony[0]` equals the owner EAX.

The candidate comparison is **`population >= best`**, using
the unsigned population BYTE at `colony+0x0A`.
Consequently a zero population value is still a possible candidate,
and **ties prefer the lowest matching colony index** because the
scan proceeds backwards.

The final write is precisely one player WORD:

```c
player[owner].home_planet_id_word_at_0x29 =
    matched ? selected_colony.planet_id_word_at_0x02 : 0xFFFF;
```

That value is a **planet ID WORD** read from colony `+0x02`,
not the selected colony index and not a guessed boolean.

The source instruction range `0xDCB65..0xDCBF6` includes the
complete loop, both branches and a normal return, with no
unresolved original callee inside this 146-byte function.

## Derived code, test coverage and safety differences

- `decompilation/reconstructed/assign_new_home_planet_v131.c`
- `decompilation/reconstructed/assign_new_home_planet_v131.h`
- `decompilation/reconstructed/remove_building9_v131.c`
- `decompilation/reconstructed/remove_building_first_write_v131.c`
- `decompilation/reconstructed/remove_building_first_write_v131.h`
- `tests/test_assign_new_home_planet_v131.c`
- `tests/test_remove_building9_v131.c`
- `tests/test_remove_building9_assign_home_integration_v131.c`
- `tools/audit_assign_new_home_planet_v131.py`

The standalone function was tested with every possible 16-bit
planet ID, all 65,536 pairs of population byte values,
tie precedence, excluded colony indices, zero-population
candidates, no candidates, and invalid host buffers.
The building-9 tests covered all 256 original signed owner
BYTE values across three colony IDs, asserting that the
`+0x13F` flag is cleared before the callback with EAX owner
and EDX excluded colony index.

An additional integrated test uses the derived building-9
callback to invoke the **complete derived home-reassignment
function**, asserting the original exclusion rule prevents
the removed colony from being reselected and verifying the
player's newly written home-planet WORD.

These C programs passed strict C11 warnings,
AddressSanitizer and UndefinedBehaviorSanitizer.
Bounds checking and validation errors are deliberate
modern host changes, not behavior claimed of the DOS routine.

## Limits and next work

`Assign_New_Home_Planet_` itself is fully reconstructed at the
verified original machine-code level, but the original 493-byte
`Remove_Building_` function has numerous other building-specific
branches. This work does **not** complete those branches or
the gameplay-wide effects of `Remove_Building_`.

The next source targets are the colony-production queue removal,
star-colony recalculation and environmental updates invoked for
specific building IDs. Full combat, turns, galaxy generation,
save/load and a playable browser engine remain incomplete.

No original proprietary executable, artwork or game media was
published to GitHub. No Game Lab site, Xbox controller or Qwen
runtime changes were made.

**Independent type verification:** the original `Remove_Building_` star-recalculation branch at CODE `0x46E2..0x46FF` uses colony WORD `+0x02` to index the original `_planet` array (17-byte stride), then uses the BYTE at planet `+0x02` to index `_star` (113-byte stride). Thus the `+0x02` value stored by `Assign_New_Home_Planet_` is the **planet index**, not the star index. This second source audit is `tools/audit_remove_building_star_recalc_v131.py`.
