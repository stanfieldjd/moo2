# MOO2 v1.31 — single-population bomb outcome and first building-removal write

**Status:** Source-verified **single-entry branch** of original
`Resolve_Bomb_Hit_` translated into bounded derived C. Original
`Remove_Building_` entry and first byte-clearing mutation verified
and reconstructed separately. **Neither 641-byte bomb resolver nor
493-byte building-removal function is fully translated.**
This is not original MicroProse source, DOS differential execution,
or a complete Game Lab browser game.

Authenticated original `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

Source function coverage:

| Watcom source function | Original CODE offset | Entire source-body size | Source byte-hash status |
| --- | --- | ---: | --- |
| `Resolve_Bomb_Hit_` | `0xCCEBD` | 641 bytes | Complete original body SHA-256 verified |
| `Remove_Building_` | `0x45EA` | 493 bytes | Complete original body SHA-256 verified |

The new audit `tools/audit_colony_single_entry_bomb_v131.py`
verifies **47 exact machine-instruction sites** across these
two original functions, including the known Watcom function
symbols, original DATA globals, original signed comparison
and call addresses.

Machine-readable result:
`decompilation/reports/colony_single_entry_bomb_v131_2026-10-13.json`.

## Original path qualification and effect ordering

Original `Resolve_Bomb_Hit_` reaches the special case
if colony entry count BYTE `colony+0x0A` equals **1**
and the aggregate weight of the other ordinary bomb
targets is exactly zero. Original CODE `0xCCF56..0xCCF6A`.

This source state calculation includes the eligible
49-position building scan and colony words `+0x130`,
`+0x132`, and nonzero `+0x125` described in
`decompilation/annotated/colony_hit_resolvers_v131.md`.
For host safety, the derived single-entry helper requires
each of those independent categories to be empty/zero.
That is a sufficient but **narrower** condition than
an original signed aggregate of zero where invalid
negative values might cancel positive counts.

The source then reads the sole entry DWORD at
`colony+0x0C`, masks its lowest nibble,
and reads a signed 16-bit defense field at
`colony+0xB4 + 2*(entry & 0x0F)`.

- **If signed defense is greater than 100**:
  CODE `0xCCFDD` subtracts 100 from the original
  defense WORD, sets result-event BYTE `+0x41`
  to 1, and returns EAX=1.
  It does **not** remove the population entry
  or call `Remove_Building_` in this case.
- **If signed defense is 100 or less**:
  original CODE `0xCCF7E..0xCCFDB`
  increments result-event WORD `+0x0C`,
  zeros that defense WORD, changes colony
  entry-count BYTE `+0x0A` from 1 to 0,
  checks the original building-presence byte
  at `colony+0x13F`, conditionally calls
  `Remove_Building_(colony_index,9)`,
  sets result-event BYTE `+0x42` to 1,
  increments the original owner/opponent player
  stat WORD by 10, then sets event BYTE `+0x41`
  to 1 and returns EAX=1.

Original player stat addressing uses
`_player` at DATA `0x1FF98`,
3,753-byte (0xEA9) per-player record
stride, signed `colony[0]` owner and
signed `event[0]` opponent, with statistic
WORD offset `+0x6FF + 2*opponent`.
The C implementation reuses the previously
verified owner-stat helper.

The original branch sees negative signed
16-bit defense values as **100 or less**;
it does not clamp them to zero before
making the branch decision.

## First original `Remove_Building_` mutation

The 493-byte `Remove_Building_` function begins
at CODE `0x45EA`. The source prologue takes
colony index AX and building ID DX, sign-extends
both, multiplies the colony index by original
361-byte (0x169) stride, loads original
`_colony` DATA pointer at `0x1AB18`, and
executes the source first memory write at
`0x460A`:

```
BYTE [_colony + 0x169*colony_index + 0x136+building_id] = 0
```

For building ID **9**, the target is original
colony byte `+0x13F`, precisely the marker
checked before the call by `Resolve_Bomb_Hit_`.

**Important scope boundary:** original `Remove_Building_`
then handles additional conditional building,
colony, ship, and derived-statistics effects,
including calls to other original code.
Only its **first field-clear write** is
present in
`decompilation/reconstructed/remove_building_first_write_v131.c`.
The rest remains an explicit callback in the
`colony_single_entry_bomb_v131.c` helper.
Do not claim that merely clearing the flag
replaces the original building-removal function.

The original `Remove_Building_` full-body
source SHA-256 is
`8e0eb8d52268bf214d1ce3ec73d0e9970f0b4db1b0d1cae035810ace87179875`.
Full-body source checksum authentication
does not mean that body has been entirely
decompiled into C.

## Derived source and test evidence

- `decompilation/reconstructed/colony_single_entry_bomb_v131.c`
- `decompilation/reconstructed/remove_building_first_write_v131.c`
- `decompilation/reconstructed/colony_hit_player_stats_v131.c`
- `decompilation/reconstructed/colony_hit_player_stats_v131.h`
- `tests/test_colony_single_entry_bomb_v131.c`
- `tests/test_remove_building_first_write_v131.c`
- `tests/test_colony_hit_player_stats_v131.c`
- `tools/audit_colony_single_entry_bomb_v131.py`
- `decompilation/reports/colony_single_entry_bomb_v131_2026-10-13.json`

The integrated original single-entry branch test covers
all **65,536** possible 16-bit defense patterns,
all 16 entry low-nibble types, the exact
building-9 callback ordering, 16-bit event
and player-stat wraparound, and malformed host
inputs. The source first-write helper test
covers 3 colony IDs x 49 flag positions
x 256 possible initial flag values,
checking that exactly the selected byte
becomes zero.

The original player-stat tests remain in place.
All were compiled using strict C11 warnings
and passed AddressSanitizer and UndefinedBehaviorSanitizer.

## Source follow-on: verified home-planet reassignment

The building-9 `Remove_Building_` path at original CODE `0x4674..0x467C` calls `Assign_New_Home_Planet_` with the colony's **signed owner BYTE in EAX** and the **excluded colony index in EDX** (preserved from `0x45F6`). That complete original 146-byte function has now been reconstructed in `decompilation/reconstructed/assign_new_home_planet_v131.c`: descending search over `_NUM_COLONIES`, greatest eligible population (lowest colony index wins ties), and player WORD `+0x29` set to that colony's planet-index WORD or `0xFFFF`. The integrated regression `tests/test_remove_building9_assign_home_integration_v131.c` verifies both original arguments, flag-clear ordering and final home-planet write. The machine-code audit verifies 57 instructions and both full original function-body hashes. See `decompilation/annotated/assign_new_home_planet_v131.md`.

## Outstanding

The full original `Remove_Building_` needs
its branch table, follow-on named calls,
and other colony/global state effects
reconstructed. This single-entry branch
is only one of several actual weighted
bomb-hit target outcomes. Broader planetary
combat, game turns, galaxy construction,
and browser engine are still incomplete.

No original game executable/media was
committed or deployed publicly. Game Lab
website, Xbox controller and Qwen were
not modified by this pass.
