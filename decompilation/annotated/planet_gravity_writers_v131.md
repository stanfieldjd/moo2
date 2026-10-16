# v1.31 original gravity table, planet writer and home-world normalization

## Original provenance

Official MicroProse original v1.31 DOS executable SHA-256: `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Original extracted Watcom LE CODE: `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. Original initialized LE DATA: `082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b`. Source objects are used locally only and not versioned.

Complete original source-named bodies SHA-verified, instruction-contiguously decoded, and checked at independent opcode sites:

| Procedure | CODE offset | Bytes | Decoded original instructions |
|---|---|---:|---:|
| `Enforce_Gravity_` | `0x6B45C` | 88 | 30 |
| `Enforce_Mineral_Richness_` | `0x6B4DA` | 216 | 65 |
| `Modify_Home_Worlds_` | `0x6C4AF` | 576 | 147 |
| `Gravity_Player_Production_Factor_` | `0xCDF2C` | 167 | 52 |

Reproducible `tools/audit_planet_gravity_writers_v131.py`: all **294** decoded original source instructions, 30 selected exact opcode anchors, original direct CALL displacements, source DATA symbol locations, all 25 original table entries, and 159 controlled fixture assertions. Structured result: `decompilation/reports/planet_gravity_writers_v131_2026-10-16.json`.

## Original initialized _gravity_table is DATA, not CODE

Original named **DATA** `_gravity_table` is at `0x572A`. It ends immediately before distinct named DATA `_gravity_to_atmosphere` at `0x5743` (difference **25 bytes**). Exact original initialized SHA-256 for those 25 table bytes: `5e2b1977479b4a37b5911f9657539829f8c996b97973d378323c1989a7769f13`.

| planet BYTE +0x0A (row) / planet BYTE +0x05 (column) | 0 | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 1 | 1 |
| 1 | 0 | 0 | 1 | 1 | 1 |
| 2 | 0 | 1 | 1 | 1 | 2 |
| 3 | 1 | 1 | 1 | 2 | 2 |
| 4 | 1 | 1 | 2 | 2 | 2 |

The original `Enforce_Mineral_Richness_` code `0x6B598–0x6B5AA` reads source planet BYTE `+0x0A`, planet BYTE `+0x05`, computes index **5*BYTE_0A + BYTE_05**, fetches the BYTE from source **DATA** `_gravity_table` at `0x572A` and writes **planet BYTE +0x06**. This source path therefore writes only **0,1,2**, **provided both original selector fields are 0–4**. This procedure has no source bounds guard for selectors beyond that tested range; validity across all possible runtime states remains to be independently proved.

Care is required: raw `objdump -b binary` labels the extracted CODE object as section .data, but it cannot distinguish Watcom relocation segments on memory operands. The table really belongs to original initialized **DATA object 2**. Looking up CODE bytes at offset `0x572A` returns unrelated instructions and yields false values; the original `decompilation/symbols.csv` DATA symbol and initialized object hash disambiguate the reference.

## Independent home-world source override

Original `Modify_Home_Worlds_` CODE `0x6C65A–0x6C68C` reads original owner player BYTE `+0x8A9` and then `+0x8AA` and passes a chosen constant to `Enforce_Gravity_` through register EDX.

| source player BYTE +0x8A9 | player BYTE +0x8AA | selected gravity value | source branch |
|---|---|---:|---|
| nonzero | either | **0** | `0x6C663 XOR EAX,EAX` |
| zero | nonzero | **2** | `0x6C670 MOV EAX,2` |
| zero | zero | **1** | `0x6C677 MOV EAX,1` |

Thus the first option takes precedence when both flags are nonzero. CODE `0x6C685` moves the selected gravity into EDX; direct original CALL at `0x6C68C` reaches named `Enforce_Gravity_` CODE `0x6B45C`. That procedure saves input EDX and writes its low BYTE to planet record BYTE `+0x06` at CODE `0x6B474`. Its additional potential planet-rank side effect when BYTE `+0x0A==4` and another race condition holds is **not** treated as a no-op; that separate effect remains outside this gravity-only bounded test.

The prior source-verification confirmed `+0x8A9` and `+0x8AA` as the original player fields corresponding to original DATA `_option_toggle[0]` and `_option_toggle[1]` and reconstructed the gravity yield factor. On the source-normalized owner homeworld, assuming same owner race as tagged population, original gravity factor returns **4** in all four boolean race-option combinations:

- First option enabled: gravity 0 and corresponding first option enabled -> factor4.
- Second option enabled and first disabled: gravity2 and corresponding second option enabled -> factor4.
- Both disabled: gravity1 and first option disabled -> factor4.
- Both enabled: first option wins, gravity0, corresponding first option enabled -> factor4.

Since original worker production applies `-5*(4-factor)*base`, this particular owner-homeworld/race path has **zero gravity penalty**. This is source-derived conditional logic, not proof that every colony or every population group has no gravity penalty.

## Limits

Both the table-based and race-option-based paths are real original planet-gravity writers; the original scientist/research display source effects remain independent. We have **not** globally proved that every possible planet gravity BYTE is 0–2 (other writers and corrupted/save-edited states are not exhausted), that all selections/race budgets are legal, or that the prior hypothetical research-production 0-versus-1 example is reachable. Original DOS execution and native behavior comparison remain unperformed. The overall previously stated 87% estimate remains unrecalculated.
