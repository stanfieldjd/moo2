# MOO2 v1.31 colony economy reconstruction — verified assembly layer

This note records only behavior directly established from the official v1.31 code image. Unknown colony/player flags remain named by record offset until independently identified.

## Per-farmer food (`Colony_Food2_Per_Farmer_`)

The routine works in doubled-food units.

1. Read the colony planet id at colony `+0x02`.
2. Read planet byte `+0x0B` from the 17-byte planet record and multiply by 2.
3. If that result is zero and player record `+0x134 == 3`, replace it with 2.
4. If colony flag `+0x164` is set, add 4.
5. If colony flag `+0x13A` is set, add 2.
6. Return the integer doubled-food value.

No floating-point arithmetic occurs.

## Per-worker industry (`Colony_Industry_Per_Worker_`)

The five-byte `_minerals_per_mine` table embedded at linker offset `0xCD4B5` is:

`[1, 2, 3, 5, 8]`

The planet mineral class (`planet +0x0A`) indexes this table. The routine then adds:

- colony `+0x13A`: +1
- colony `+0x13D`: +1
- colony `+0x15A`: +2
- colony `+0x142`: +3
- player `+0x183 == 3`: +1

The result is integral industry per worker.

## Per-scientist research (`Colony_Research_Per_Scientist_`)

Base research per scientist is exactly 3. Additive modifiers are:

- colony `+0x13A`: +1
- colony `+0x154`: +2
- colony `+0x149`: +3
- colony `+0x159`: +1

A player-record byte selected through the colony owner/race index at record `+0x0F` supplies a final special modifier:

- value 10: +2
- value 11: +5
- otherwise: +0

The routine is integer-only.

## Industry converted to tax (`Colony_Industry_To_Tax_`)

Let `industry = colony.word[0xE9]` and `reserved = colony.byte[0xF0]`.

If `industry - reserved <= 0`, tax conversion at colony `+0x127` is zero.
Otherwise:

`tax = ((industry - reserved) * player.byte[0x31]) / 100`

using signed integer division. The computed tax is stored at colony `+0x127` and subtracted from colony industry `+0xE9`.

## Research cost (`Player_Research_Cost_`)

For a non-positive field/application id, cost is zero. Otherwise the routine loads the 32-bit base cost from the 23-byte research-definition record selected by the id.

For ids >= 75 it additionally adds:

`player.byte[0x1D1 + id] * 10000`

This is an explicit late/repeat-level cost extension in the executable; its semantic label remains unresolved here.

## Breakthrough percentage (`Chance_For_Research_Breakthrough_Aux_`)

For `cost <= 0` or `cost <= accumulated`, return 0. Otherwise:

`chance = ((accumulated - cost) * 100) / cost`

when accumulated is beyond the cost threshold represented by the routine's calling convention, clamped to 100, with a minimum nonzero result of 1 once the integer quotient would otherwise be zero.

The wrapper `Chance_For_Research_Breakthrough_` supplies current research state from player offsets `+0x321`, `+0xAC`, and `+0x1EB` to this helper.

## Turns-until-research (`Player_N_Turns_Until_Research_Complete_`)

This routine simulates future turns with integer arithmetic rather than using a closed-form floating estimate. It repeatedly adds the player's per-turn research (`player.word[0xAC]`) to accumulated research (`player.dword[0x1EB]`), counts turns, and after reaching the nominal cost repeatedly evaluates the breakthrough helper. A special state selected by `player.byte[0x321]` returns zero immediately. A zero per-turn rate can return `-1` when the current accumulated amount has not crossed the required state.

This behavior should be reproduced by integer simulation in the remaster rather than replaced with floating-point ETA arithmetic.

## Compiler tail merging discovered during this pass

Watcom reuses code tails across nominal function boundaries. `Colony_BC_Maintenance_`, for example, jumps into the common epilogue at linker address `0xD1F97`, which lies inside the provisional symbol extent of `Player_N_Turns_Until_Research_Complete_`. This is compiler code sharing, not evidence that the maintenance routine semantically contains the research routine.

The CFG recovery tool now treats unconditional jumps into another provisional function body as shared-tail edges instead of following them and falsely inflating function extents.

## Food maintenance / consumption (`Colony_Food_Maintenance_`)

The routine clears an eight-byte per-race accumulator at colony `+0x104` and four aggregate counters at `+0xFC..+0xFF`, then iterates every population unit (`colony.byte[0x0A]`) through the packed population records beginning at colony `+0x0C`.

For population categories 0..7, the consumption weight is selected from player/race flags:

- player/race `+0x8B0` set: weight 1
- otherwise player/race `+0x8B1` set: weight 0
- otherwise: weight 2

Population category 9 contributes weight 2 through a separate path. Each weight is accumulated both into the category bucket and one of the colony aggregate buckets according to owner/category and a packed population status bit. The final colony food-maintenance byte `+0xEF` is:

`(total_weight + 1) / 2`

using integer arithmetic, i.e. `ceil(total_weight / 2)` for nonnegative totals.

An anomaly/event guard can force maintenance to zero before the population scan.

## Industry maintenance / consumption (`Colony_Industry_Maintenance_`)

This is structurally parallel to food maintenance. It clears the eight category counters at colony `+0x10C` and aggregate counters `+0x100..+0x103`, then scans every population unit.

For categories 0..7, each unit contributes 1 only when player/race flag `+0x8B0` is set; otherwise it contributes zero. Category 9 contributes 2 through its special path. The final colony industry-maintenance byte `+0xF0` is again:

`(total_weight + 1) / 2`

An anomaly/event guard can force the value to zero.

These two routines establish that food and industry upkeep are computed from individual packed population records, not merely from the colony's total population count.

## BC maintenance (`Colony_BC_Maintenance_`)

For an active, non-anomaly colony, the routine sums the maintenance values of all present buildings represented by the 49 building flags beginning at colony `+0x136`, then adds colony byte `+0x114`. The sum is converted to hundredths, multiplied by a climate percentage, rounded, and stored at colony `+0xF2`.

The embedded `_climate_maintenance_modifiers` table is exactly:

`[50, 25, 0, 25, 0]`

For base maintenance `M` and climate index `c`, the assembly computes:

`maintenance = (M * 100 * (100 + climate_modifier[c]) + 5000) / 10000`

with integer division. This is nearest-integer rounding of the climate-adjusted maintenance for normal nonnegative values. The routine then subtracts colony word `+0xED` and stores that signed difference at colony `+0xF9`.

Inactive/anomaly colonies set the maintenance byte to zero.

## Shared-tail census

The whole-code pass found 1,410 unconditional cross-symbol interior jumps targeting 548 distinct interior addresses. The most reused target in gameplay code is the common cleanup sequence at linker `0xD1F97`, with 21 incoming jumps. This quantitatively explains most of the earlier apparent CFG over-extension: after recognizing shared tails, functions classified as extending beyond their provisional next-symbol boundary fell from 149 to 33.
