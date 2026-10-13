# v1.31 research cost — two original-function reconstructions

**Decompilation status:** both routines have been transcribed to C-like
logic and cross-checked against machine instructions and original LE data
object. **Not** the original MicroProse source code and **not** a
differential execution proof. Original assets remain private.

## Provenance and relocation

Original `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

Original Watcom functions and entry offsets:

- `Get_Tech_Cost_`: `0xFF93B`, 16 bytes, conditional branch at
  `0xFF940`, exits through two **cross-symbol jumps**.
- `New_Get_Tech_Cost_`: `0xFF85D`; shared conversion steps at
  `0xFF861`, `0xFF86C` and subsequent tail jump to `0xD1E96`.
- `Player_Research_Cost_`: `0xD1E96`, 48 bytes, ends in RET at
  `0xD1EC5`; the latter is the executed callee *body*, despite a tail
  jump rather than CALL from `Get_Tech_Cost_`.

**Important:** Original object 1 stores LE fixup placeholders in machine
instructions. For instance `Player_Research_Cost_` has raw
`MOV EAX,[EAX+0x5916]`, but the reconstructed relocated instruction
has `MOV EAX,[EAX+0x175916]`. `0x175916` is the derived relocated
VA for **data object 2 offset `0x5916`**, not code object offset
`0x5916`. Reading the raw CODE bytes at that offset produces nonsense;
reading the correctly relocated DATA object yields real technology
costs. The special technology-index mapping uses DATA offset `0x607F`
(relocated VA `0x17607F`).

The original object is little endian. The relevant technology
record has **23-byte stride**, its first four bytes being the base
research cost. The special mapping table has **13-byte stride**, with
the first two bytes forming a signed technology identifier. The
player/race record has **`0xEA9` stride**.

## Recovered C-like behavior

```c
// Isolated derived pseudocode, NOT the original game's C source.
// All pointers refer to validated in-game storage and all IDs must
// be legitimate game values. Original code has no added bounds checks.
// uint8_t *data_object2 is the original LE DATA object, not the CODE object.

uint32_t recovered_Player_Research_Cost_(
    const uint8_t *data_object2,
    const uint8_t *player_record,
    int16_t technology_id
) {
    if (technology_id <= 0)
        return 0;

    // Original 0xD1EA4: technology_id * 0x17 (23 bytes per record).
    uint32_t cost = read_u32_le(data_object2 + 0x5916
                                + (int32_t)technology_id * 23);

    // Original 0xD1EAD: CMP DX,0x4B; JL skip.
    if (technology_id >= 75) {
        uint8_t modifier = player_record[0x1D1
                                      + (int32_t)technology_id];
        cost += (uint32_t)modifier * 10000U;
    }
    return cost;
}

uint32_t recovered_Get_Tech_Cost_(
    const uint8_t *data_object2,
    const uint8_t *race_records_base,
    int16_t empire_index, // BX at the entry
    int16_t technology_arg, // AX at the entry
    uint16_t selector        // DX at the entry
) {
    int16_t technology_id = technology_arg;

    // Original 0xFF93B: CMP DX,0x2000; JNE 0xFF86C.
    // Special case jumps to code at 0xFF861 instead.
    if (selector == 0x2000) {
        technology_id = read_s16_le(data_object2 + 0x607F
                                    + (int32_t)technology_arg * 13);
    }

    // Original 0xFF86C..0xFF87F prepares EAX/EDX and performs
    // a tail JMP into Player_Research_Cost_.
    const uint8_t *record =
         race_records_base + (int32_t)empire_index * 0xEA9;
    return recovered_Player_Research_Cost_(
         data_object2, record, technology_id);
}
```

The C-like text is a *semantic translation*, not a byte-identical
reconstruction of the original Watcom register protocol. Original
arithmetic is 32-bit, with 16-bit sign extension where noted. A
faithful runtime port must preserve overflow if a legitimate game
state can reach those conditions.

## Independent static-data cross-check

Read from authenticated v1.31 relocated DATA object 2, first DWORD of
record at `0x5916 + 23*index`:

| Technology index | Original base cost |
| ---: | ---: |
| 0 | 0 (but routine independently returns 0 for nonpositive IDs) |
| 1 | 400 |
| 2 | 650 |
| 3 | 150 |
| 4 | 80 |
| 5 | 250 |
| 8 | 1500 |
| 30 | 2750 |
| 74 | 15000 |
| 75 | 15000, **before** any player modifier |
| 76 | 15000, **before** any player modifier |

From the `0x607F + 13*index` special lookup, index 0 maps to technology
0, 1 maps to technology 49, 2 to technology 48, 3 to technology 42.
These are derived fixture observations, **not an assertion of the
meaning or full valid range** of selector `0x2000`.

## Unresolved

The complete range of valid technology IDs, meanings of the
special-selector mode, provenance of the per-player modifier byte
and possible saturation/wraparound behavior in higher-level calls
remain unverified. The full research-tree, technology selection,
research accumulation and end-of-turn technology processing are
**not yet reconstructed**.

This document makes no deployment or game-engine changes.
