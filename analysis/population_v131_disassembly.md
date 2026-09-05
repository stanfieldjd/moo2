# Official v1.31 population routine findings

Source: official April 11 1997 ORION2.EXE, SHA-256 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f.
Addresses are resolved through Watcom symbols and the LE object/page map.

## Size_And_Climate_Max_Population_

Symbol: segment 1, offset 0x000D0A18. Length 49 bytes.

Verified instruction behavior:

1. Load a size-dependent base maximum-population byte.
2. Load a climate-dependent percentage byte.
3. Add `25 * BL` to that percentage (BL is a boolean/0-or-1 modifier at this call boundary).
4. Clamp the resulting percentage to 100.
5. Multiply by the size-dependent base population.
6. Add 50.
7. Signed-divide by 100.

Equivalent arithmetic for valid nonnegative game values:

    result = (base_population[size] * min(climate_percent + 25 * modifier, 100) + 50) / 100

with integer division at the final step.

This is direct executable evidence that this routine rounds to nearest whole population unit after applying the percentage. Fractional capacities do not survive this routine's return value.

The extracted `_planet_max_population` table is exactly:

    5, 10, 15, 20, 25

## Size_And_Climate_Race_Pop_Limit_

Symbol: segment 1, offset 0x000D0A49. Length 188 bytes.

Verified structural behavior:

- Handles special population/race categories before calling `Size_And_Climate_Max_Population_`.
- Contains explicit race-data checks rather than a generic environmental-hardiness statistic.
- Certain climate values are remapped for a qualifying racial trait before the base max-population calculation.
- A separate qualifying racial trait adds a size-dependent amount after the base calculation.

This supports keeping Aquatic/Tolerant/Subterranean-style behavior as explicit race mechanics rather than inventing a generalized hardiness attribute.

## Planet_Max_Population_For_Player_

Symbol: segment 1, offset 0x000D0B05. Length 206 bytes.

Verified structural behavior:

- Distinguishes uncolonized/invalid owner state from an existing colony owner.
- Calls the size/climate/race population-limit path.
- Applies an additional +5 population for one player/race condition.
- For colonies containing multiple population races/categories, evaluates their individual limits and retains the greatest applicable result rather than blindly using one colony-wide race value.

## Colony_Race_Pop_Limit_

Symbol: segment 1, offset 0x000D0BD3. Length 81 bytes.

Verified structural behavior:

- Starts from the colony's planet size/climate/race population-limit calculation.
- Applies +5 when the owning player field at offset `0x11A` equals 3. This is identified as the Advanced City Planning population-capacity effect: the official rule is +5 maximum population, and this is the player-wide +5 path shared by the planet- and colony-limit routines.
- Applies +2 when the colony byte at offset `0x145` is nonzero. This is identified as the Biospheres presence flag: the official rule is +2 maximum population, and this is the colony-local +2 path.

The two previously unresolved capacity modifiers are therefore resolved as Advanced City Planning (+5, player-wide) and Biospheres (+2, colony-local). The raw offsets remain recorded for player/colony structure reconstruction.

## Implementation consequence

Do not replace the original max-population path with Wiki fractional-capacity arithmetic. The official executable explicitly performs integer rounding in `Size_And_Climate_Max_Population_`. Preserve the original primitive tables and calculation ordering in the remaster.

## Colony_Pop_Grows_ — verified arithmetic core

Symbol: segment 1, offset 0x000D1839.

Instruction-level findings from the official executable:

- The routine obtains a race/category-specific population limit before calculating growth. If the current population has reached that limit, the contribution is zero.
- The race growth modifier is loaded from the owning race/player data and converted to a percentage around a base of 100.
- Two separate player technology/status fields add +50 or +25 percentage points respectively. They are mutually selected by the code path (`+50` takes precedence over `+25`), matching the replacement rather than stacking behavior previously observed for the two medical growth technologies.
- Additional race/leader/colony conditions modify that same percentage accumulator before natural growth is calculated. Their semantic names remain deliberately unresolved until the owning structure fields are identified.
- The natural-growth core computes `(limit - population) * race_population * 2000 / limit`, then calls an internal helper at relative offset `0x53459`. The helper's return is multiplied by the accumulated percentage and integer-divided by 100.
- A separate additive accumulator is added after the percentage-scaled natural-growth result. This proves that not every population-growth source belongs inside the natural-growth percentage multiplier.
- The final per-category result is accumulated into the colony record at `pop_grow` offset `0xC8` (two-byte entry for the current population category).

Equivalent structure, without prematurely naming unresolved fields:

    natural_base = helper(((limit - population) * race_population * 2000) / limit)
    natural_modified = (natural_base * growth_percent) / 100
    pop_grow[group] += additive_growth + natural_modified

This replaces the remaster's earlier assumption that all growth bonuses can be represented by one generic additive percentage. The implementation must preserve the original separation and integer operation order.


## isqrt_ — natural-growth helper resolved

The call at `Colony_Pop_Grows_ + 0x485` resolves exactly to the Watcom global symbol `isqrt_` at segment 1, offset `0x00124C92` (physical file offset `0x001BA2E6`).

The official routine is an unsigned integer square root. For normal population-growth inputs it returns `floor(sqrt(n))`. It uses a binary search and never performs floating-point arithmetic or nearest-integer rounding. Inputs at or above `0xFFFE0001` saturate to `65535`.

Therefore the verified v1.31 natural-growth core is now: 

    q = ((limit - population) * race_population * 2000) / limit
    natural_base = isqrt(q)
    natural_modified = (natural_base * growth_percent) / 100
    pop_grow[group] += additive_growth + natural_modified

Every division and the square root are integer operations. For the ordinary nonnegative population domain, this means truncating the quotient, then taking the floor square root, then truncating the percentage division.
