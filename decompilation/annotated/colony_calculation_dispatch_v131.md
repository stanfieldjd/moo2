# MOO2 v1.31 — original colony-calculation dispatcher

**Status:** The complete **65-byte** original `Colony_Calculation_` named Watcom routine at CODE `0xD2A70` has been source-reconstructed as an order-preserving C dispatcher. Its original three called gameplay routines have been independently source-hash authenticated and remain **named unresolved callbacks**, rather than guessed economic or statistic calculations.

Authenticated local original `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

| Original named function | Original CODE offset | Complete CODE bytes | Original full-body SHA-256 |
| --- | --- | ---: | --- |
| `Colony_Calculation_` | `0xD2A70` | 65 | `e667850010cdc8cb620bb98fcc6fe0c2b12971f572a8c48930c88833b940d63d` |
| `Pre_Import_Computing_` | `0xD1D59` | 198 | `7aa1ea0d54d5e89f82905724eb7fc1609c1e2b9a715c828f557fb4a9224d6628` |
| `Pass_Out_Imports_` | `0xCF8F0` | 1,238 | `e35af6d4ee3106edd7af2f4f6377a18453e107323c620993b3f577871eff4234` |
| `Update_Player_Stats_` | `0xD2710` | 864 | `5b3d2b6948da42581600e270488ee10b4044851de96bcca00ba5358d6f00a38d` |

Read-only original-byte audit `tools/audit_colony_calculation_dispatch_v131.py` checks all four complete Watcom body hashes, original `_colony` DATA `0x1AB18`, original `_player` DATA `0x1FF98`, and **21 exact original x86 opcode sites**, including every direct call. Output: `decompilation/reports/colony_calculation_dispatch_v131_2026-10-16.json`.

## Exact source dispatch and argument routing

The original routine sign-extends EAX low WORD (`CWDE`) to a colony index, multiplies by original colony-record stride **0x169 (361)**, and reads the referenced colony BYTE `+0x06`.

If colony BYTE `+0x06 ==0`, it calls:

1. `Pre_Import_Computing_(colony_pointer)` at original CODE `0xD2A89` → `0xD1D59`, using EAX colony pointer.
2. `Pass_Out_Imports_(owner,colony_pointer)` at original CODE `0xD2A93` → `0xCF8F0`, using EAX **signed owner BYTE** `colony+0` and EDX colony pointer.

For colony BYTE `+0x06 !=0`, **both** production/import calls are skipped.

In either case, the routine calls `Update_Player_Stats_(player_pointer)` at original CODE `0xD2AA9` → `0xD2710`. The player pointer is original `_player + signed_colony_owner * 0xEA9`.

**Important source property:** The original reloads the colony owner BYTE separately **after pre-import** and again **after imports**. A callee mutating the owner can therefore affect the subsequent call arguments. The reconstructed dispatcher preserves this.

## Verified source files and tests

- `decompilation/reconstructed/colony_calculation_dispatch_v131.c`
- `decompilation/reconstructed/colony_calculation_dispatch_v131.h`
- `tests/test_colony_calculation_dispatch_v131.c`
- `tests/test_building_population_colony_dispatch_v131.c`
- `tools/audit_colony_calculation_dispatch_v131.py`
- `decompilation/reports/colony_calculation_dispatch_v131_2026-10-16.json`

The standalone regression covers **64** player-owner, active/inactive, and owner-reload scenarios, source callee order and three named callback failure conditions. The full integrated building-removal regression passes **32** scenarios across building IDs 15/23/24/28, original product-44 production-queue deletion, actual environmental and food arithmetic, original population cap tables, original seeded Random/Shuffle and population enforcement, then the original **65-byte colony-calculation dispatch** with separate verified call boundaries.

Both compile with strict C11, AddressSanitizer and UndefinedBehaviorSanitizer. **The integrated callbacks do not implement the actual pre-import production equations, import transfers or player-statistics changes.** Those are separate original named routines that still need source reconstruction and dynamic game-state validation.

No original DOS differential execution was performed. Invalid host pointers/owner bounds produce explicit errors not present in the DOS binary, and earlier effects are not automatically rolled back. The original copyrighted executable and art remain local. The Game Lab web version is still non-playable; Game Lab, Xbox and unrelated Qwen server configurations were not modified.
