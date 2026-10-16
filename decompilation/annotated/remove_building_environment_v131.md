# MOO2 v1.31 — remaining environmental building-removal branches

**Source status:** Derived C for the original `Remove_Building_` environmental branch with building IDs **15, 23, 24 and 28**; original product-44 queue purge, full original 108-byte `Colony_Environmental_Stuff_` state update, and original 136-byte `Colony_Food2_Per_Farmer_` math are reconstructed. The full population-limit and colony-calculation bodies are still explicit named callbacks in this branch.

This is **not** original MicroProse source and is **not** an original DOS differential gameplay execution. No proprietary game assets were committed.

## Original executable and provenance

Authenticated `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

The read-only `tools/audit_remove_building_environment_v131.py` verifies seven complete original Watcom function-body hashes, named DATA pointers and **88 original x86 instruction checkpoints**, recorded in `decompilation/reports/remove_building_environment_v131_2026-10-16.json`. The food-function audit verifies its own entire 136-byte body and **43 instruction positions** in `decompilation/reports/colony_food_per_farmer_v131_2026-10-16.json`.

| Original named Watcom function | Original CODE | Body |
| --- | --- | ---: |
| `Remove_Building_` | `0x45EA` | 493 bytes |
| `First_Prod_Colony_Queue_Slot_` | `0xA1C5D` | 250 bytes |
| `Delete_Prod_From_Colony_Queue_` | `0xA206F` | 50 bytes |
| `Delete_From_Colony_Queue_` | `0xA1E19` | 94 bytes |
| `Colony_Environmental_Stuff_` | `0xD1CED` | 108 bytes |
| `Colony_Food2_Per_Farmer_` | `0xCE03E` | 136 bytes |
| `Enforce_Population_Limits_At_Colony_` | `0xDC97C` | 489 bytes |
| `Colony_Calculation_` | `0xD2A70` | 65 bytes |

The above functions are source-hash authenticated. **Authentication does not mean each function has been fully reconstructed**; the 489-byte population-limit function and the 65-byte colony-calculation wrapper still have unresolved effects.

## Exact source dispatch

Original `Remove_Building_` CODE `0x460A` first writes zero to colony building-presence BYTE `+0x136+building_id`.

- **ID 15** jumps directly to common environmental update at CODE `0x47AA`.
- **IDs 23 and 24** are both included in the original `CMP BX,24; JBE 0x477A` branch after the previous `CMP BX,22` condition. This was independently verified: **23 must not be omitted**.
- **ID 28** reaches CODE `0x477A` from a separate `CMP BX,28; JBE` branch.
- **For IDs 23, 24 and 28**, CODE `0x477A..0x47A5` reads the colony's signed planet index WORD `+0x02`, finds the original 17-byte planet record and checks unsigned planet BYTE `+0x08`. If it is **less than 2**, it calls `Delete_Prod_From_Colony_Queue_(colony_id,44)`; otherwise, production item 44 remains in the queue.

The original `First_Prod_Colony_Queue_Slot_` treats positive product **44** as an exact signed WORD match among seven queue entries at `colony+0x115+2*slot`. `Delete_Prod_From_Colony_Queue_` repeatedly finds and deletes its first match until none remain. Original `Delete_From_Colony_Queue_` invokes the previously source-recovered anonymous `0xA20ED` compactor, shifting the remaining slots left, setting final slot to −1 and removing consecutive −10 placeholders that reach the deleted slot. Product 44 is not a ship entry and does not trigger ship-state resets.

After that, all four building IDs call in original order:

1. `Colony_Environmental_Stuff_(colony_pointer)` at CODE `0x47BA`.
2. `Enforce_Population_Limits_At_Colony_(colony_pointer)` at CODE `0x47C6`.
3. `Colony_Calculation_(colony_id)` at CODE `0x47CD`.

The first two functions save/restore EDX. Thus `MOV EAX,EDX` at `0x47CB` supplies the original colony index to the third. The C reconstruction preserves this ordering with typed named callbacks for the latter two helpers.

## Fully recovered 108-byte environmental state update

Original `Colony_Environmental_Stuff_`:

- Copies planet status BYTE `+0x08` into colony BYTE `+0xE2`.
- If the planet status equals **1**, replaces colony `+0xE2` with **2** when either original colony flag BYTE `+0x14D` or BYTE `+0x14E` is nonzero.
- Calls `Colony_Food2_Per_Farmer_(colony_pointer,signed_colony_owner,EBX=0)`. If returned low WORD is zero, colony BYTE `+0xE0=0`; otherwise, colony BYTE `+0xE0=255`.

Original CODE `0xD1D1E` executes `CMP AL,AL`, followed by `JNE` at `0xD1D20`. Because the comparison is necessarily equal, that jump is unreachable. Its apparent check of colony BYTE `+0x152` does not have the effect a superficial C rewrite might suggest.

**Original building-flag interaction:** building ID **23** clears original colony flag `+0x14D`, and building ID **24** clears flag `+0x14E`, *before* environmental calculation. Consequently removing those buildings can alter the environmental result even if the planet's base status remains the same. This was caught by combined tests and corrected.

The source-derived original food production function now runs in the integration test. See `decompilation/annotated/colony_food_per_farmer_v131.md`.

## C, tests, and limits

- `decompilation/reconstructed/remove_building_environment_v131.c`
- `decompilation/reconstructed/colony_environmental_stuff_v131.c`
- `decompilation/reconstructed/colony_environmental_stuff_v131.h`
- `decompilation/reconstructed/colony_food_per_farmer_v131.c`
- `tests/test_remove_building_environment_v131.c`: **3,072** branch and product-44 queue cases
- `tests/test_colony_environmental_stuff_v131.c`: **6,144** planet/flag/food-result cases
- `tests/test_remove_building_environment_integrated_v131.c`: **128** building/environment cases with separate food callback
- `tests/test_colony_food_per_farmer_v131.c`: **32,768** food, bonus and owner cases
- `tests/test_remove_building_environment_food_integrated_v131.c`: **6,144** cases integrating the original food calculation
- `tools/audit_remove_building_environment_v131.py`
- `tools/audit_colony_food_per_farmer_v131.py`

All source-derived C tests passed strict C11 compilation with AddressSanitizer and UndefinedBehaviorSanitizer. Invalid colony/planet/player pointers are rejected in the host port rather than reproducing unsafe DOS reads.

**Next dependencies:** full `Enforce_Population_Limits_At_Colony_`, then the original `Colony_Calculation_` calls and their production/import subroutines. Full game source equivalence and a playable Game Lab browser engine are not yet complete.
