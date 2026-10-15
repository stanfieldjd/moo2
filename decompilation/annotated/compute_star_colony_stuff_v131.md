# MOO2 v1.31 — complete `Compute_Star_Colony_Stuff_` reconstruction

**Scope:** A standalone, source-backed C reconstruction of the entire original **311-byte** Watcom `Compute_Star_Colony_Stuff_` routine. This is derived source, **not** original MicroProse C, a running DOS differential test, or completion of the whole game.

Authenticated local `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

Original CODE offset `0xD5296`, complete 311-byte body SHA-256:
`b599c172a8a790494eb319c9edd73c881f6fea26a6e708ebf75cd3feae9d1ee0`.

At CODE `0xD53C8`, the original jumps to a **shared external Watcom return** at `0xD1F97`: `LEAVE; POP EDI; POP ESI; POP EDX; POP ECX; POP EBX; RET`. The 8-byte shared epilogue SHA-256 is `a0a1f6af6d85bfeba680dfae738040640b858b18484a2aff60f23f3f7f7b6dc1`; its stack/register restore agrees with this function's `PUSH EBX ECX EDX ESI EDI; ENTER 8` prologue. There are no additional direct function CALL instructions in the named 311-byte function.

The authenticated audit `tools/audit_compute_star_colony_stuff_v131.py` verifies the original entire-function hash, **84 individual machine-instruction checkpoints**, the external epilogue hash, and three original DATA symbols. Its reproducible report is `decompilation/reports/compute_star_colony_stuff_v131_2026-10-15.json`.

## Recovered original dataflow

The input EAX is an original **113-byte star-record pointer**. Source CODE `0xD529F..0xD52C0` clears the following eight original star BYTE fields before rebuilding them: `+0x38`, `+0x39`, `+0x3E`, `+0x3D`, `+0x3B`, `+0x3C`, `+0x3F`, `+0x40`.

The function scans **five** signed WORD star planet IDs at `star+0x4A+2*i` in *descending* order, indices 4 to 0. Planet ID −1 is skipped. Otherwise it follows the original `_planet` DATA pointer at offset `0x1B0D4`, with **17-byte planet stride**; the signed WORD at planet `+0x00` is the associated colony ID, and −1 means there is no colony.

A colony ID references the original `_colony` pointer at DATA `0x1AB18` using **361-byte (`0x169`) colony stride**. Signed colony owner BYTE `+0x00` is used to create the original one-byte player bitmask `1 << owner`. When multiple colonies share an owner, source operations combine status with **bitwise OR**, not addition or overwriting.

Player-specific conditions read original `_player` at DATA `0x1FF98`, **3,753-byte (`0xEA9`) player stride**. The original compares precise technology/feature BYTE values to **3**, not nonzero.

| Rebuilt star BYTE | Original condition to OR owner bit |
| --- | --- |
| `+0x38` | Colony is present on this star |
| `+0x39` | Colony building BYTE `+0x136+45` is nonzero |
| `+0x3B` | Any building `+40`, `+8`, or `+41` present, **and** owner player BYTE `+0x1CB == 3` |
| `+0x3C` | Same three-building predicate, **and** owner player BYTE `+0x1C7 == 3` |
| `+0x3D` | Owner player BYTE `+0x1C1 == 3` |
| `+0x3E` | Owner player BYTE `+0x17A == 3` |
| `+0x3F` | Colony building `+3` nonzero |
| `+0x40` | Colony building `+14` nonzero |

These are *source-defined bit fields*; the actual gameplay names of each bit can be researched separately. They should not be assigned guessed game-feature labels without evidence.

## Derived source and integration

- `decompilation/reconstructed/compute_star_colony_stuff_v131.c`
- `decompilation/reconstructed/compute_star_colony_stuff_v131.h`
- `tests/test_compute_star_colony_stuff_v131.c`
- `tests/test_remove_building_compute_star_integration_v131.c`
- `tests/test_remove_building_queue_compute_star_integration_v131.c`
- `tools/audit_compute_star_colony_stuff_v131.py`
- `decompilation/reports/compute_star_colony_stuff_v131_2026-10-15.json`

The isolated regression covers **8,192 combinations** (8 owner bits × 64 building-flag masks × 16 player-feature masks), five simultaneous planet slots, repeated owner OR combinations, uncolonized entries, skipped planet IDs, unchanged unrelated star bytes, and rejection of unsafe host pointers without partially clearing source fields.

The direct building-removal integration uses the actual reconstructed star computation after original `Remove_Building_` paths for **building IDs 3, 14 and 45**. Star BYTE `+0x3F`, `+0x40`, then `+0x39` clears as the corresponding original building presence byte is cleared. ID45 still requires the external original `Update_Ship_ETAs_` callback and confirms callback order.

The queue-dependent integration for **building IDs 8, 40 and 41** runs the earlier reconstructed original seven-slot queue scan, actual `Delete_From_Colony_Queue_` ship-state write/compactor, and this now-complete star-field recomputation. The three building IDs correctly lose the combined `+0x3B` and `+0x3C` flags only after the last qualifying building is removed. Original ID22 executes queue deletion but **does not recalculate star fields** on that branch.

All three new programs passed strict C11 compilation, AddressSanitizer and UndefinedBehaviorSanitizer. Their expected results are source-derived consistency tests, **not** original DOS dynamic differential executions.

## Current limits

For **valid original-format game state**, the 311-byte function's observed source dataflow has been translated, without unresolved original function calls. The derived host C deliberately validates planet/colony/player indices before clearing star fields; the original DOS code does not provide equivalent safe error handling and may behave differently for malformed records.

This does **not** fully reconstruct `Remove_Building_`, `Update_Ship_ETAs_`, other star/combat systems, galaxy generation, game turns, save/load, or the eventual Game Lab browser engine. The original copyrighted executable and assets remain local; the public Game Lab deployment and unrelated Qwen services were not modified.
