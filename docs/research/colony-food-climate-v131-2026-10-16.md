# MOO2 v1.31 original food-production climate adjustment

Original official `ORION2.EXE` v1.31 SHA-256: `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Source-original CODE `Colony_Empire_Base_Food2_Produced_` is the 358-byte named function at `0xCE0C6`. The source audit uses authenticated original Watcom LE CODE and initialized DATA images, but publishes neither game binary nor assets.

## Source finding

The food producer's optional climate correction is conditional on source population tag **0–7**, positive initial food base, cache miss, and tag-indexed player flag BYTE `+0x8AB !=0`. Its climate index is the source colony BYTE `+0xE2`. Two specific source branches calculate:

- For climate **4 or 6**: `2 * (_food_per_farmer_table[8] - _food_per_farmer_table[climate])`.
- For climate **5 or 8**: `2 * (_food_per_farmer_table[9] - _food_per_farmer_table[climate])`.
- All other unsigned climate BYTEs (including 10–255): **zero adjustment**, without a table lookup.

The original DATA `_food_per_farmer_table` is at `0x581C` and consists of exactly ten bytes `[0,0,0,1,1,2,2,1,2,3]`, SHA-256 `00723b29c9735d5b593affde81837443b627641360d56ca40823caf383978979`. Therefore the only nonzero selected branch adjustments are **+2 for climate 4, 5, or 8**; climate 6 evaluates to **0**. The function uses `0x5824` and `0x5825`, which are entries 8 and 9 of the **same** food table, rather than the adjacent separate DATA `_climate_modifier_table` at `0x5817`.

For this source-only cache-miss computation, player BYTE `+0x8A1` contributes a signed BYTE amount for tags 0–7; tag 8 has constant +6 and tag 9 constant +4, with no climate adjustment for either. After the calculation, original CODE stores a low BYTE into the food result cache. When a component breakdown buffer is supplied, the source stores the population contribution as WORD `+4+2*tag` and the climate delta as DWORD `+0x222`, even for a zero climate delta. The earlier separate cache-source audit establishes the cache-hit signed-byte return behavior and the cache bypass for initial nonpositive food production.

The exact body digest, all 95 decoded source instructions, all 23 direct internal branch destinations, 54 selected exact original opcode anchors, authenticated CODE/DATA symbols and **31 controlled synthetic fixtures** are reproduced by `tools/audit_colony_food_climate_v131.py` and `decompilation/reports/colony_food_climate_v131_2026-10-16.json`; annotated machine-code and input-domain evidence appears in `decompilation/annotated/colony_food_climate_v131.md`.

These tests are source-derived static checks, **not** a DOS runtime differential comparison or proof of full valid-game-state/native-engine parity. This closes this specific climate branch question without changing the historical unrecalculated 87% whole-executable estimate.
