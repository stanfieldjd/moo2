# MOO2 v1.31 — original size, climate and race population capacity

**Status:** Completely reconstructed the original 49-byte `Size_And_Climate_Max_Population_` and 188-byte `Size_And_Climate_Race_Pop_Limit_` numerical functions. Both of their **original lookup tables** have been independently byte-verified against the authenticated v1.31 executable objects. The existing 81-byte `Colony_Race_Pop_Limit_` wrapper now uses real numerical functions instead of a synthetic capacity callback.

Original authenticated `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

## Original Watcom body and table provenance

| Original routine/data | Original object offset | Bytes | Full original body SHA-256 |
| --- | --- | ---: | --- |
| `Size_And_Climate_Max_Population_` | CODE `0xD0A18` | 49 | `405533edb6bdde5d69b314322b9a8a024bacd606529689968521f5c02b54bb14` |
| `Size_And_Climate_Race_Pop_Limit_` | CODE `0xD0A93` | 188 | `7c8629ad880163c090835f05037b1bde31bf058a183d30069b2af1b014eb032d` |
| `_planet_max_population` lookup | initialized DATA `0x5806` | 5 | `40872669c921a1dcd7c03fa241ebe872f8e6e0adb7f17f9583edd7347cb7e480` |
| Climate percentage lookup | CODE `0xCD4EB` | 16 | `2da9ae3d665157adb1edb27e449f922b394ca5759cd607e3b5849af221ea8468` |

The original full read-only audit `tools/audit_size_climate_pop_limit_v131.py` independently verifies both full named code bodies, **80 exact i386 opcode locations**, both original lookup sequences, the original DATA/CODE symbol addresses, and original executable SHA-256. See the committed machine report `decompilation/reports/size_climate_pop_limit_v131_2026-10-16.json`.

## Exact lookup values and arithmetic

Original planet sizes indexed 0..4 map to base maximum populations:

| Planet size index | 0 | 1 | 2 | 3 | 4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Base capacity | 5 | 10 | 15 | 20 | 25 |

Original climate indexes 0..15 map to integer percentages:

| Climate index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Percentage | 25 | 25 | 25 | 25 | 25 | 25 | 40 | 60 | 80 | 100 | 30 | 60 | 30 | 60 | 60 | 120 |

The original `Size_And_Climate_Max_Population_` source receives planet-size index in EAX, climate index in EDX and a boolean population bonus in BL, then calculates:

`min(100, climate_percentage[climate] + 25*bonus) * base_population[size]`, adds **50**, and performs original signed division by **100** (integer rounding nearest for positive source values).

The original `Size_And_Climate_Race_Pop_Limit_` uses the following exact race rules before calling the 49-byte maximum-population helper:

- For race indexes **0..7**, BYTE `player +0x8B6` nonzero activates the 25-point climate-percentage bonus.
- Race index **8** always activates that bonus; race **9** does not. Races 8/9 do not use player records.
- For races **0..7**, nonzero BYTE `player +0x8AB` remaps climate indexes **4→8**, **5→9**, **6→8** and **8→9** before the lookup. Other climate indexes remain unchanged. The colony environmental status is *not* written by this function.
- After the result, nonzero BYTE `player +0x8AC` for races 0..7 adds **2 × (planet_size + 1)**, with the original low-WORD sign extension.

This source is present in `decompilation/reconstructed/size_climate_pop_limit_v131.c` and its header.

## Integration and limits

The previously reconstructed 81-byte `Colony_Race_Pop_Limit_` then applies separate owning-player research BYTE `+0x11A ==3` bonus **+5** and colony building BYTE `+0x145` bonus **+2**. The full building ID15/23/24/28 → production-queue cleanup → environment → food → race capacity → seeded population shuffle and limits regression now calls these real size/climate functions, removing the last synthetic capacity fixture from the population-management chain.

New tests:

- `tests/test_size_climate_pop_limit_v131.c`: **160** base size/climate/bonus lookups plus **6,400** player/race/trait combinations, climate remapping and clamping, and original-safe bounds.
- `tests/test_building_population_full_original_capacity_v131.c`: **32** cases across the original four building IDs, population-capacity changes, food-state flags, seeded shuffle and actual limit enforcement. This integration retains a callback for the subsequent original `Colony_Calculation_` routine, not for capacity, food, or shuffle.

Compiled under strict C11 with AddressSanitizer and UndefinedBehaviorSanitizer. **No original DOS dynamic differential game-state execution** has occurred; host safety validation is not asserted to match corrupted original DOS state. The complete game and browser version are still unfinished. No original proprietary game binary or artwork is committed. No Game Lab site, Xbox controller or Qwen configuration change occurred.
