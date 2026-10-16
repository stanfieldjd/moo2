# MOO2 v1.31 — complete food production per farmer

**Status:** The entire **136-byte** original `Colony_Food2_Per_Farmer_` routine is reconstructed into source-derived C for its input/output arithmetic and its optional breakdown-buffer writes. Original executable SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

The original Watcom function begins at CODE `0xCE03E`. Its complete 136-byte function-body SHA-256 is `6aef5f245db959b949a22eb0cfccd03b65db2c103a18c4dc47f5bbabcf9a04e4`. `tools/audit_colony_food_per_farmer_v131.py` verified the entire body, named Watcom function extent, original DATA pointers `_planet` at `0x1B0D4` and `_player` at `0x1FF98`, and **43 exact original instruction locations**. Machine-readable report: `decompilation/reports/colony_food_per_farmer_v131_2026-10-16.json`.

## Exact original arithmetic

Source EAX input is a colony pointer; EDX supplies the signed low-WORD owner; EBX is either null or a pointer to an optional per-contributor statistics buffer.

The original reads signed colony planet ID WORD `+0x02`, uses original 17-byte planet record stride, and obtains unsigned planet food BYTE `+0x0B` into **DX**, not full EDX. Consequently `MOVZX DX,BYTE` preserves the high half of the preceding EDX value. It doubles EDX with a full 32-bit `ADD EDX,EDX`. For usual original small planet IDs, this gives twice the planet's food BYTE. The derived C also preserves the full 32-bit high-half behavior for larger safe host indexes instead of silently truncating it.

If the resulting food **low WORD is zero**, the function checks original player technology BYTE `+0x134` (player stride **0xEA9**) for value **3** and, when matched, sets EDX to **2**.

When the resulting food low WORD is **strictly positive as signed 16-bit**, original colony BYTE `+0x164` nonzero adds **4**, and original colony BYTE `+0x13A` nonzero adds **2**. If food is zero without the player-technology fallback, neither building bonus is applied.

The optional original EBX buffer receives writes only when the source condition is met:

| Statistics buffer offset | Original write |
| --- | --- |
| DWORD `+0x00` | Sign-extended initial doubled food low WORD |
| WORD `+0x52` | Value 2 for player-technology fallback |
| WORD `+0x21C` | Value 4 for colony `+0x164` bonus |
| WORD `+0x1C8` | Value 2 for colony `+0x13A` bonus |

Other statistics fields are **not zeroed or overwritten** by this function.

Original `Colony_Environmental_Stuff_` calls the function with EBX=0, then tests the low AX result to set colony BYTE `+0xE0` to zero or `0xFF`. That call path is integrated in `tests/test_remove_building_environment_food_integrated_v131.c`.

## Implemented files and verification

- `decompilation/reconstructed/colony_food_per_farmer_v131.c`
- `decompilation/reconstructed/colony_food_per_farmer_v131.h`
- `tests/test_colony_food_per_farmer_v131.c`
- `tools/audit_colony_food_per_farmer_v131.py`
- `decompilation/reports/colony_food_per_farmer_v131_2026-10-16.json`

The standalone test passed **32,768** source-derived owner/planet-food/bonus combinations, the optional buffer's exact modified bytes, and an independent case exercising preservation of the high WORD of EDX. The integrated test passed **6,144** original building/planet/food/technology/environment-prerequisite cases using the actual reconstructed food function, not a synthetic food-result callback.

The C is compiled with strict C11, AddressSanitizer and UndefinedBehaviorSanitizer. Host input validation is intentionally safer than the original DOS binary on corrupt or out-of-range game data. No original DOS dynamic differential execution has been performed, and the original copyrighted game executable/media remain local.

The full original `Enforce_Population_Limits_At_Colony_`, broad `Colony_Calculation_` and other game systems remain unfinished. The public Game Lab website, Xbox controller features and Qwen services were not modified by this work.
