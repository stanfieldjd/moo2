# Function-level reconstruction: `Colony_Specialty_` (v1.31)

**Status:** machine-instruction-supported *C-like reconstruction* of this
isolated function. **Not** original C source, not a complete colony turn,
and not yet run against the original executable as a differential test.

Source: original official `ORION2.EXE` SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
Original LE CODE offset `0xD1E1F` (decimal 859679), analysis-image
virtual entry `0xE1E1F`; 84-byte contiguous body through `0xE1E72`.
Watcom passes the colony-record pointer in **EAX**, not the default
cdecl stack convention guessed by some decompilers.

## Independently decoded operations

- Save caller registers; retain the colony pointer in EBX.
- Initialize EDX (sum), ECX (running maximum), EAX (loop index) and the
  local 16-bit winner index to zero.
- Loop `index = 0, 1, 2`. Read a 16-bit value from record offsets
  `0xE7`, `0xE9`, and `0xEB`, respectively.
- Accumulate the low 16 bits of the three values; this is equivalent to
  16-bit modular addition for the value ultimately tested.
- Compare `CX` and `SI` **as signed 16-bit integers**. Replace the
  winner only on a **strict increase** (`CMP CX,SI; JGE skip`);
  equal maximum values retain the earlier index. Initial maximum is 0.
- Recover signed sum with `MOVSX EAX,DX`; divide by two **toward zero**
  using `CDQ; SUB EAX,EDX; SAR EAX,1`.
- Compare that half-sum to the signed running maximum. If maximum is
  **strictly greater**, write its index (0, 1 or 2) to the record byte at
  `+0x0B`. Otherwise write `0xFF`. No other colony-record fields are
  stored by this routine.

## Compact C-like translation of observed semantics

```c
// Derived algorithm, NOT MicroProse original C code.
// read_s16_le must decode signed little-endian 16-bit values.
// write_u8 represents the original final byte store.
void derived_colony_specialty(uint8_t *colony) {
    int16_t maximum = 0;
    uint8_t winning_index = 0;
    uint16_t sum_mod_65536 = 0;

    for (uint8_t i = 0; i < 3; ++i) {
        int16_t value = read_s16_le(colony + 0xE7 + 2*i);
        sum_mod_65536 = (uint16_t)
                         (sum_mod_65536 + (uint16_t)value);
        if (value > maximum) {
            maximum = value;
            winning_index = i;
        }
    }

    // Decode the final low 16 bits with signed 16-bit semantics.
    int32_t signed_sum = (sum_mod_65536 & 0x8000u)
        ? (int32_t)sum_mod_65536 - 65536
        : (int32_t)sum_mod_65536;

    // C99+ integer division truncates toward zero, as does the original
    // CDQ; SUB EAX,EDX; SAR EAX,1 instruction sequence.
    int32_t half = signed_sum / 2;
    write_u8(colony + 0x0B,
             (maximum > half) ? winning_index : (uint8_t)0xFF);
}
```

## Key non-obvious properties

1. A **2-to-1 threshold comparison** is being performed here; it is
   wrong to choose the highest counter on every call.
2. Ties keep the first strictly higher candidate; ties with initial
   zero never replace it.
3. Signed behavior and wrapping are important. Do **not** silently
   widen the summation to a full-precision integer with no 16-bit
   narrowing, or replace signed division with an unsigned shift.
4. These source counters may be associated with colony production
   categories, but their semantic labels and actual update sites must
   be cross-referenced. No real in-game job reassignment or turn
   behavior is proven by this isolated translation.

## Next verification

Derive independent test vectors from the original executable or
controlled traces (not from merely rerunning this translation), compare
its result byte, verify all callers and the `colony+0x0B` consumers, and
then connect any retained behavior to the complete colony-turn graph.
