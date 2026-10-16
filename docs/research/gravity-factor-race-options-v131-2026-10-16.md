# Source-derived v1.31 gravity modifiers and race-option dependency

The official original `ORION2.EXE` v1.31 (SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`) and its extracted Watcom LE CODE (SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`) establish the missing input behavior for the original `Gravity_Player_Production_Factor_` nested economy helper.

The original helper at CODE `0xCDF2C` (167 bytes) returns factor **4** when colony BYTE `+0x14F` is nonzero or the population tag is 8/9. Otherwise the source reads the planet BYTE `+0x06` through colony planet-ID WORD `+0x02` and original DATA `_planet`. Gravity code 0 returns 3 absent player BYTE `+0x8A9`, or 4 when enabled; code 1 returns 4 absent `+0x8A9`, or 3 when enabled; code 2 returns 2 absent player BYTE `+0x8AA`, or 4 when enabled. Original `Colony_Job_Production_` uses the returned factor in `-5 * (4-factor) * population base`, yielding original normal penalties of -10, -5 and 0 times base for factors 2, 3 and 4.

The original two player BYTEs are converted to the first two WORD slots of original DATA `_option_toggle` (at 0x236DC and 0x236DE) by the fully authenticated `Convert_Player_To_Flags_` and `Convert_Flags_To_Player_`. This advances game-state source provenance without inventing user-facing racial trait names, default choices or legality.

**Original undefined/unproven case:** planet gravity codes 3+ follow `MOV EAX,EBX` at CODE `0xCDF60` without a local EBX assignment proven on that path. The audit therefore covers only source-verified normal cases 0/1/2. This is not a finding that such out-of-domain states occur in normal gameplay.

`tools/audit_gravity_production_factor_v131.py` validates four entire original body SHA digests, 441 decoded x86 machine instructions including all 52 instructions and original direct branches of the gravity helper, 49 exact opcode anchors and 145 bounded fixtures. Machine-readable evidence is `decompilation/reports/gravity_production_factor_v131_2026-10-16.json`; detailed source offsets and qualification are in `decompilation/annotated/gravity_production_factor_v131.md`.

No DOS original-runtime parity comparison, valid complete saved-game production fixture, or full native implementation is claimed. No game binary/assets or website changed. Previously recorded 87% overall estimate remains unrecalculated.
