# MOO2 v1.31 colony production pipeline — reconstruction packet

This packet extends the verified colony economy work into the production pipeline. It records control/data facts established directly from the official v1.31 code image; unresolved fields remain offset-labelled.

## Colony_Empire_Base_Food2_Produced_

The routine takes colony, population/race category, optional calculation-context, and player/race selector inputs. It first obtains the ordinary doubled-food contribution (or reuses colony +0xDD for the colony-owner/default path). Non-positive results bypass all bonuses.

A cached race/category calculation is keyed by colony pointer and category. When the corresponding player/race state byte at +0x32358 is 99, the routine computes and caches extra production. Categories 0..7 obtain an additive race-data value from +0x8A1. If the race flag at +0x8AB is set, climate-specific food adjustments are additionally derived from `_food_per_farmer_table` and two adjacent table constants at linker 0x5824/0x5825. Category 8 contributes a fixed +6; category 9 contributes a fixed +4. The computed components are optionally written into the calculation-context structure and are added to the doubled-food result before it is cached.

The routine therefore proves that empire/race base food is not simply `farmers * planet food`: race/category and climate state can alter the per-unit doubled-food contribution before colony-level production modifiers are applied.

## Production-stage routines captured

Exact instruction bodies have now been exported for:

- `Colony_Job_Production_` (996 bytes)
- `Colony_Food_Production_` (1209 bytes)
- `Colony_Industry_Production_` (1789 bytes)
- `Colony_Research_Production_` (1103 bytes)
- `Colony_BC_Production_` (1239 bytes)

These are retained as separate analysis inputs rather than relying on the earlier 2 KiB generic disassembly window. This avoids cross-function contamination while the higher-level arithmetic is resolved.

## Reconstruction rule

Production routines will be decoded as a pipeline: base per-job yield -> race/category contribution -> colony/player modifiers -> maintenance/tax deductions -> stored colony totals. Shared compiler tails are treated as code reuse and not as semantic ownership by the adjacent symbol.
