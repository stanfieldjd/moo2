# MOO2 v1.31 — pre-import calculation recovery

The original `Pre_Import_Computing_` (CODE `0xD1D59`, 198 bytes) has an order-preserving C reconstruction in `decompilation/reconstructed/pre_import_computing_v131.c`. The original executable SHA-256 is `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

`tools/audit_pre_import_computing_v131.py` verifies **six complete original function body hashes, all fifteen direct calls, the original mineral table and 107 exact x86 instruction sites**. Machine report: `decompilation/reports/pre_import_computing_v131_2026-10-16.json`.

The reconstructed routine zeros colony bytes `+0xEF..+0xF2`, computes original food output at `+0xDD`, environmental status, industry-per-worker output at `+0xDE`, and scientist output at `+0xDF`. After the original replicators call, it writes `WORD+0xF5 = signed_min(zero_extend(BYTE+0xF0), signed_WORD+0xE9)`.

Five original source-derived routines now execute within pre-import:

- `Colony_Food2_Per_Farmer_` (136 bytes)
- `Colony_Environmental_Stuff_` (108 bytes)
- `Colony_Industry_Per_Worker_` (178 bytes)
- `Colony_Research_Per_Scientist_` (177 bytes)
- `Colony_Industry_To_Tax_` (89 bytes)

The worker function's original `_minerals_per_mine` table at CODE `0xCD4B5` contains exactly `[1,2,3,5,8]`. The worker adds building and technology bonuses, preserving original partial-DX and optional statistics writes. Scientist base production is 3, with original building bonuses and planet special type 10 (+2) or 11 (+5).

Industry-to-tax uses signed colony industry WORD `+0xE9` minus replicator BYTE `+0xF0`; if positive, it converts by the owner-player tax percentage BYTE `+0x31`, stores low WORD `+0x127`, and subtracts the converted low WORD from industry. For nonpositive taxable industry, `+0x127` becomes zero.

**Nine named original economy effects remain callbacks:** morale, industry maintenance, industry production, food production, food maintenance, replicators, research production, BC production and BC maintenance. They have not been replaced with fake calculations. The following original `Pass_Out_Imports_` (1,238 bytes) and `Update_Player_Stats_` (864 bytes) also remain unfinished.

Tests are in `tests/test_colony_worker_scientist_v131.c`, `tests/test_colony_industry_to_tax_v131.c`, `tests/test_pre_import_computing_v131.c` and `tests/test_building_population_pre_import_v131.c`. They cover **2,560 worker cases, 512 scientist cases, 19,200 tax cases, 1,440 pre-import cases and 32 building-to-colony integration cases**. Tests use strict C11, AddressSanitizer and UndefinedBehaviorSanitizer.

This is source-recovery and host state-consistency testing, **not a running DOS differential comparison**. The full game and browser version are not finished. Original proprietary game media remain local. The Game Lab website, Xbox support and unrelated Qwen services have not been modified.
