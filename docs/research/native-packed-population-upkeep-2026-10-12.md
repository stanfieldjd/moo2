# Verified packed-population upkeep reconstruction — 2026-10-12

## Scope

The native browser engine now contains two **isolated** arithmetic/state
transformations from the official Master of Orion II v1.31 executable:
`Colony_Food_Maintenance_` and `Colony_Industry_Maintenance_`.

These routines do not implement workforce assignment, total production,
treasury, anomaly detection, turn progression, save/load, or the complete game.

Evidence was obtained through REA 6.4.0 and Ghidra 12.1.4 on a relocated
32-bit x86 analysis image derived from the canonical original
`ORION2.EXE` (SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`).
The source executable and converted game artwork were left unchanged and
were not included in GitHub.

## Original function evidence

| Original symbol | Preferred virtual entry | Ghidra body bytes |
| --- | --- | ---: |
| `Colony_Food_Maintenance_` | `0xdeb4b` | 330 |
| `Colony_Industry_Maintenance_` | `0xdf546` | 297 |

Both functions use a signed colony-owner selector at `+0`, an unsigned
population count at `+0x0a`, and four-byte packed population records
starting at `+0x0c`. The original `AND EDX,0x0f` selects population
categories 0–15; `SHL EAX,0x15; SHR EAX,0x1f` isolates **bit 10** of
the packed 32-bit entry for one of two non-owner accumulator groups.
Race records have stride `0xea9`; for categories 0–7, maintenance flags
are at race offsets `+0x8b0` and `+0x8b1`.

**Food:**
- Category 0–7 weight: 1 if race flag `+0x8b0` is nonzero; otherwise 0
  if `+0x8b1` is nonzero; otherwise 2.
- A category 9 entry contributes 2 to the special group at colony `+0xff`,
  established by `CMP DX,9` at `0xdec3d`.
- Category buckets `+0x104..0x10b`; four group buckets `+0xfc..0xff`.
  The final food maintenance value is the rounded-up half-sum stored as
  a byte at colony `+0xef`.

**Industry:**
- Category 0–7 weight: 1 if race flag `+0x8b0` is nonzero; otherwise 0.
- **Category 8**, not 9, contributes 2 to the special group at colony
  `+0x101`. The original instruction at `0xdf5cc` is `CMP DX,8`,
  followed by a later `JNZ` at `0xdf61f` that branches for other categories.
- Category buckets `+0x10c..0x113`; four group buckets `+0x100..0x103`.
  The final industry maintenance value is the rounded-up half-sum stored
  at colony `+0xf0`.

The original routines each call a separate external colony/event guard
(`0x2341e` as resolved by Ghidra). If it indicates the early-exit case,
the routine zeros **only** its final maintenance output, leaving previous
category/aggregate buckets intact. The browser module takes this outcome
as an explicit boolean `anomaly` input; the guard's internal rules are
**not** inferred or implemented here.

## Implemented safe native interface

`web/engine/colony-maintenance.mjs` exports
`applyFoodMaintenance`, `applyIndustryMaintenance` and
`applyColonyMaintenance`. Each accepts explicit `Uint8Array` colony
and race-record buffers plus the external guard result. Original buffers
are not mutated: returned colony records are clones. The combined form
runs food then industry without pretending it advances a turn.

For conservative memory safety, a supplied population list must end
before the first known downstream colony field at `+0xe9`. That allows
up to 55 four-byte entries from `+0x0c`, **but does not establish that
55 is the actual v1.31 gameplay population limit**. Confirming the true
maximum and all population-slot semantics remains separate work.

`web/engine/tests/colony-maintenance.test.mjs` has **nine passing
automated tests**, covering owner/non-owner grouping, bit 10, special
category distinction, both race maintenance flags, original accumulator
locations, anomaly early exit, signed owner byte, source-buffer
immutability, all 16 packed categories, and conservative bounds.
The checked-in module and test source were matched to the locally
executed version by Git blob SHA-1:

- module: `ee158e641391c391fc2daa4dd996cb83da3ad4db`
- tests: `c75b22dedf7fc6d26f79c6a4e8d47aec155dcfc8`

The repository's existing `tools/run_tool_tests.sh` invokes
`node --test web/graphics/tests/*.test.mjs web/engine/tests/*.test.mjs`,
so the new tests are included in its JavaScript glob automatically.
The local remote `penguin` command transport was intermittent during
this pass; **the complete remote original-executable test suite was not
re-run after publication**. Do not infer that a complete end-to-end
regression or a real Xbox One Edge test has occurred.

## Known unknowns and next original-code targets

- `Pop_To_Pop_State_` and `Give_Colonist_New_Job_`: packed status and
  job assignment mutations.
- `Colony_Job_Production_`, `Colony_Pop_Base_Prod_Produced_`:
  workforce selection, effects of gravity and race/category modifiers,
  production aggregation and final colony total stores.
- Exact semantics of the external anomaly guard, valid in-game population
  slot count, player/race pointer selection, actual turn update order,
  original save-file compatibility and full browser/Xbox deployment.

Do not enable New Game or call the browser prototype playable until
the native game state and turn mechanics actually work.
