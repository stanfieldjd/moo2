# v1.31 `Resolve_Bomb_Hit_` and `Resolve_Biological_Hit_`: source-backed target selection

**Status:** both complete named Watcom function byte ranges authenticated,
their original target-selection subgraphs traced, and safe isolated C
selection logic verified against the original RNG. This does
**not** mean the complete hit resolvers, damage effects, player
statistics, or DOS gameplay have been reimplemented.

Authenticated `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
Original LE CODE object 1: 1,410,709 bytes, unrelocated.

## Entire original code-function provenance

| Original Watcom symbol | CODE offset | Length | Original function-body SHA-256 |
| --- | --- | ---: | --- |
| `Resolve_Bomb_Hit_` | `0xCCEBD` | 641 bytes | `ee665889d157c0882ac1512a67f1f940bf25a1d3d76811dcad0f30558d53dc89` |
| `Resolve_Biological_Hit_` | `0xCD13E` | 436 bytes | `b19a11cb99d998a561924d948cb77b58fa2c69f246aca89e6c9f9379c6a81dd8` |
| **Combined original code** | | **1,077 bytes** | |

The source audit `tools/audit_colony_hit_resolvers_v131.py`
independently checks both original function-body SHA-256 hashes,
**68 original machine instruction anchors**, original Watcom
named callees and DATA globals, and the external biological
return sequence. Its machine-readable output is
`decompilation/reports/colony_hit_resolvers_v131_2026-10-13.json`.

## Biological target selection: reverse-scan reservoir algorithm

At original CODE `0xCD146..0xCD185`,
`Resolve_Biological_Hit_` receives EAX =
pointer to an original `_colony` record and
EDX = combat hit-result event pointer.

1. Read the unsigned BYTE population/entry count
   at colony record `+0x0A`. Colony record stride
   is the original **361 bytes** (`0x169`).
2. Iterate from `count-1` down to `0`, examining the
   DWORD located at `colony+0x0C+4*index`.
   If `DWORD & 0x0F == 8`, skip that entry.
3. For each eligible entry, increment the running
   eligible count EDI and call the original
   `Random_(EDI)` at CODE `0x1147A0`.
   Select that index if and only if the returned
   EAX equals **1**. Later eligible entries can
   replace the previous choice: this is
   *reservoir sampling* in reverse source order.
4. If the selected index remains −1, the original
   executes `JL 0xCCEB7` from CODE `0xCD185`.
   This exit is **outside the 436-byte symbol interval**,
   in a **six-byte shared epilogue** inside the
   `Destroy_Colony_` named symbol interval:
   `LEAVE; POP EDI; POP ESI; POP ECX; POP EBX; RET`.
   The original biological resolver pushes
   `EBX ECX ESI EDI`, then `ENTER 4`,
   so this external return restores its stack correctly.
   It is a genuine cross-function CFG edge,
   not a fall-through into ordinary bomb code.

The exact external return bytes at CODE
`0xCCEB7..0xCCEBC` have SHA-256
`0488d06b31fc4e6e52f9e400c94ead43b0ebe94d902f47cab4c51cbf59946c54`.

**Remaining biological effects:** Once a candidate exists,
source instructions set original event flag `+0x41`,
consult colony count `+0x0A`, draw additional random
values weighted by colony WORDs `+0x130` and
`+0x132`, and conditionally decrement population
counts, rearrange a colony entry, modify player-record
statistics, and increment original result-event
WORDs such as `+0x08`, `+0x0A`, `+0x0C`,
`+0x3F`. The original also manipulates
defense-state WORDs at colony `+0xB4+2*index`.
These effects are **not implemented by the
isolated selection C**.

## Ordinary bomb target eligibility

The original `Resolve_Bomb_Hit_` scans **49 positions**
in descending order, source CODE `0xCCEE4..0xCCF30`:

```
for (index = 48; index >= 0; --index)
    if (colony[0x136 + index] != 0 &&
        index not in {8, 9, 26, 27, 40, 41, 42, 47})
        append index to eligible_indices[];
```

The eight excluded positions are backed by explicit
original `CMP EBX,constant; JE` sequences.
The saved indices are in **descending order**,
written to an original local byte array
at `[EBP-0x44 + index]`. The source calls the
group a set of possible hit targets; the semantic
names of all 49 positions should be recovered
from original colony data tables rather than
inferred from array position.

## Original weighted bomb target draw

The original CODE `0xCCF30..0xCD102` builds a
candidate weight total from:

- The number of eligible building positions in that 49-slot scan.
- The **signed WORD** at colony `+0x130`.
- The **signed WORD** at colony `+0x132`.
- One weight when signed WORD colony `+0x125`
  is **nonzero** (including a negative nonzero
  bit pattern).
- The unsigned entry-count BYTE at colony `+0x0A`,
  but **only when count differs from exactly 1**.

If the count equals 1 and all other weights total
zero, the original enters its dedicated
single-entry path at `0xCCF6A`
without calling `Random_` for a weighted draw.
If the count differs from 1 and the total is zero,
it exits without a weighted draw.

Otherwise the source calls
`Random_(total_weight)`, which returns an
original inclusive value from **1 to total_weight**,
then computes `EAX-1` for its zero-based
weighted index. Successive comparison/subtraction
partitions that index across:

1. Eligible original building positions
2. Colony population WORD `+0x130`
3. Colony population WORD `+0x132`
4. Nonzero colony status/defense WORD `+0x125`
5. Ordinary colony entry count BYTE `+0x0A`
   (only in the branch where that count is not 1)

The original `Resolve_Bomb_Hit_` then applies
separate damage rules, player-tech modifiers
and colony/result-event writes according to
this selected target class. Those effects,
including conditional population decrements
and building destruction, **remain unresolved**.

## Derived C scope and safety differences

The source-backed selection code is in
`decompilation/reconstructed/colony_hit_target_selection_v131.c`.
It uses the previously reconstructed
`decompilation/reconstructed/random_v131.c`
for the actual original seed-advance, unbiased
range selection, and state persistence.

The C API validates colony buffer lengths,
rejects unsafe host counts and missing pointers,
does not assume undefined memory is accessible,
and returns an explicit "no target" status.
These differences improve host safety but are
**not original DOS error behavior**.

The weighted group helper returns a target kind,
original draw position and within-group
source offset. It is **read-only** with respect
to colony and result-event data, apart from
advancing the explicitly supplied RNG seed.
It does not simulate the actual original
`Resolve_Bomb_Hit_` or `Resolve_Biological_Hit_`
mutations.

## Verified tests

- `tests/test_colony_hit_target_selection_v131.c`:
  1,280 deterministic seed/count/category fixtures
  for reverse reservoir selection, plus the
  complete 49-position ordinary eligibility scan
  and all eight original excluded indices.
- `tests/test_bomb_weighted_target_v131.c`:
  4,096 deterministic seeds compared with an
  independent original LCG/RNG formula and
  expected target-group boundaries, plus
  special single-entry, empty, negative-nonzero
  word, and malformed host-state cases.

Both compiled under strict C11 and passed
AddressSanitizer and UndefinedBehaviorSanitizer.
This is strong **derived-selection consistency**,
not an original DOS differential test.

## Next steps

Reconstruct and separately validate the original
mutation branches inside both hit resolvers,
starting with colony population WORDs `+0x130`
and `+0x132`, and the original
`[player+0x6FF+2*owner]` statistics changes.
Follow the original `Do_Building_`-related
helper calls for building damage and destruction.
Then connect the resolvers to the already
reconstructed `Apply_Bomb_Hits_` callback loop,
`Apply_Damage_To_Planet_`, and `Fire_Bomb_`.
The complete original game and playable engine
remain unfinished.

No original proprietary game binaries/assets
were distributed. No Game Lab website,
Xbox controller or Qwen changes were made.
