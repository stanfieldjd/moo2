# Original v1.31 food and industry maintenance counter classification

## Canonical original source and audit boundaries

Original official `ORION2.EXE` v1.31 SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`, extracted Watcom LE CODE SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. The audit `tools/audit_maintenance_counter_classification_v131.py` checks four full original named function hashes, code boundaries, byte-contiguous original disassembly (**272 machine instructions**), **56 exact opcode anchors**, original DATA symbol offsets and **5,130 bounded assertions**. Machine report: `decompilation/reports/maintenance_counter_classification_v131_2026-10-16.json`.

Source function names and original CODE bodies: `Colony_Food_Maintenance_` (CODE `0xCEB4B`, 330 bytes), `Colony_Industry_Maintenance_` (CODE `0xCF546`, 297), `Convert_Player_To_Flags_` (CODE `0x4AD97`, 161), `Convert_Flags_To_Player_` (CODE `0x4AE38`, 188). All bytes are authenticated. No original game assets or executable are committed.

## Packed population entry decoding

Both maintenance procedures iterate packed population DWORDs at `colony +0x0C + 4*i`. Original CODE `0xCEBBF–0xCEBCB` for food and `0xCF5BA–0xCF5C6` for industry produce two values from each entry:

- `tag = packedDWORD & 0x0F` (low nibble). Source treats 0–7 as population-player indexes and 8+ as distinct special tags.
- `bit10 = (packedDWORD << 21) >> 31` (original `SHL EAX,0x15; SHR EAX,0x1F`). This is **bit 10**, not worker participation bit9, and is used to select one foreign-population counter bucket. The source categorizes all counted population entries here; it does not first filter on industry/research worker job.

For normal tags `0..7`, the source reads **the tagged population's** player record via `_player` DATA global at `0x1FF98` with player stride **`0xEA9`**. It uses signed/byte tests at per-player BYTE `+0x8B0` and `+0x8B1` to determine count weights. The colony's own owner is BYTE `colony+0x00`; tagged race equal to that owner chooses the owner bucket. Otherwise source bit10 determines which foreign bucket receives the weight.

## Food counter rules: Colony_Food_Maintenance_

The original food source tests player BYTE `+0x8B0` at CODE `0xCEBEC`, giving **weight 1** when nonzero. Otherwise it tests player BYTE `+0x8B1` at `0xCEBFC`, giving **weight 0** when nonzero; if both are zero the original uses **weight 2** (`0xCEC09`). Thus **the +0x8B0 condition has precedence if both are nonzero**.

Food original source bucket writes for normal tag0..7:

| Condition | Original colony BYTE counter | Source instruction |
|---|---|---|
| Population tag = colony owner | `+0xFC += weight` | `0xCEC14` |
| Other player, packed bit10 set | `+0xFE += weight` | `0xCEC23` |
| Other player, packed bit10 clear | `+0xFD += weight` | `0xCEC2B` |

Additionally original source increments the tagged-player scratch category `colony BYTE +(0x104 + tag)` by the same weight at CODE `0xCEC34`.

Special-tag branch `0xCEBD1–0xCEC48`: tags >=8 do **not** enter the player lookup or scratch updates. Only **tag 9** adds **2** to original BYTE food counter `+0xFF` (CODE `0xCEC43–0xCEC48`). Tag 8 and tags 10–15 make no source counter contribution along this branch; the audit does not claim those higher tags are valid savegame population types.

## Industry counter rules: Colony_Industry_Maintenance_

Original CODE `0xCF5E1–0xCF5EC` tests tagged-player BYTE `+0x8B0` only and uses `SETNE`: **weight 1** when nonzero, otherwise **weight 0**. No corresponding `+0x8B1` branch occurs in this routine's normal path.

| Condition | Original colony BYTE counter | Source instruction |
|---|---|---|
| Population tag = colony owner | `+0x100 += weight` | `0xCF5F6` |
| Other player, packed bit10 set | `+0x103 += weight` | `0xCF605` |
| Other player, packed bit10 clear | `+0x102 += weight` | `0xCF60D` |

Original CODE `0xCF616` also updates the per-tag scratch BYTE `colony+(0x10C + tag)` by the weight.

Special-tag branch: CODE `0xCF5CC` compares tag with 8; original `JGE` branches to CODE `0xCF61F`, which adds **2** to industry counter `colony+0x101` only when the prior source comparison was **equal to 8** (`JNE` bypasses for 9–15). Therefore **tag 8** is industry special and **tag 9** has no corresponding industry contribution. These are different branches from the food case and must not be interchanged.

Every counter increment is original `ADD BYTE`, so it retains 8-bit modulo-256 storage. The previous verified audit established food and industry total BYTE maintenance output as the low BYTE of `(sum of four counters + 1)//2`; this checkpoint authenticates the source *composition* of those counters.

## Mapping player conditions to race-option storage

The original `Convert_Player_To_Flags_` reads player options from original player field base `+0x89F` and maps fields above its special index15 to WORDs in original DATA `_option_toggle` at `0x236DC`. For player source `+0x8B0`, field index is 17 and the post-special index is 18, corresponding to **`_option_toggle[8]`**. For field `+0x8B1`, field index is 18 and post-special index is 19, corresponding to **`_option_toggle[9]`**. The reverse conversion is source-authenticated in its complete named original body. These are **verified source-offset relationships**; the original visible UI labels, selection legality and default values are not inferred.

## Boundaries

Tests exercise all nibble tags 0–15, owner tags 0–7, both states of the packed bit10 and both booleans of original player BYTE+0x8B0/+0x8B1. These are **controlled hypothetical conditions**, not evidence that all combinations occur in official DOS savegames. The audit does not dynamically execute `ORION2.EXE`, simulate the complete food/industry maintenance runtime, or establish final initial-homeworld research-worker counts after multiple production and import recomputations.

No gameplay change or revised historical 87% whole-executable completion estimate is implied.
