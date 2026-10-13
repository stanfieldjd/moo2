# Master of Orion II v1.31 — reconstructed `Fire_Bomb_`

**Status:** The entire original 224-byte function's machine instructions
and Watcom symbol identity are authenticated. Its main damage arithmetic
and outer firing-count loop have been translated into standalone C, while
the called `Random_` and `Apply_Damage_To_Planet_` interfaces remain
explicit. `Random_` itself has since been independently reconstructed,
so that callback can now use original seed-update behavior.

This is **not original MicroProse source code** and is not a complete
planet-bombing or combat engine. No original copyrighted binary or art is
committed or published.

## Original code provenance

Authenticated `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

- `Fire_Bomb_` original Watcom CODE offset `0x2A6CA`,
  through `0x2A7A9` inclusive; **224 bytes**.
- Complete original function-body SHA-256:
  `3911947f8cdc202cb3a815dc354a95f5e5edc06c1433c9fb262b5096073af5d8`.
- All **44 selected original instruction anchors**, all three
  named original DATA symbols, and both original direct CALLs were
  checked by `tools/audit_fire_bomb_v131.py`.
- Machine-readable original-code evidence:
  `decompilation/reports/fire_bomb_v131_2026-10-13.json`.

Original callee relationships:

| Original CODE offset | Name | Role observed |
| --- | --- | --- |
| `0x1147A0` | `Random_` | Called with EAX=100; low AX sign-extended by `CWDE` |
| `0x2A3C3` | `Apply_Damage_To_Planet_` | Called with EAX=&candidate damage, EDX=0, and EBX=WORD from weapon definition+0x12 |

## Source-backed record layout

`Fire_Bomb_` accepts combat-ship index in input AX and weapon-slot
index in BX. It reads these original game data objects:

- `_combat_data`, DATA object 2 at `0x1A864`, supplies a pointer
  to combat-ship records with **313-byte (`0x139`) stride**.
- The selected weapon slot starts at combat record `+0x52+11*slot`;
  the signed 16-bit weapon ID is at slot `+0` and the
  byte firing-count control is at slot `+9` (record `+0x5B+11*slot`).
- `_ordnance_bonus`, DATA object 2 at `0x21224`, has
  a signed WORD selected by the byte at combat record `+0x20`.
  The original scales damage by that signed bonus / 100;
  the ordinary valid range and producer of the owner byte
  and bonus table still require cross-reference.
- `_weapons`, DATA object 2 at `0x7803`, has 28-byte
  weapon-definition stride. The original signed 16-bit fields
  are read at definition `+0x14`, `+0x16`, and `+0x12`.
  These control the candidate damage range and the parameter
  passed to the planet-damage helper.

## Original calculation reconstructed

In machine-code order:

```c
// Derived pseudocode, not the original DOS ABI or MicroProse C.
bonus = signed16(ordnance_bonus_words[ship_record[0x20]]);
low = trunc_toward_zero(signed16(weapon[0x14]) * bonus / 100);
high = trunc_toward_zero(signed16(weapon[0x16]) * bonus / 100);
spread = high - low;
total = 0;
for (each attack permitted by BYTE ship_weapon_slot[9]) {
    rand = signed16(low16(Random_(100)));          // original RNG returns 1..100
    candidate = signed16(low16(low)) +
                trunc_toward_zero(rand * signed16(low16(spread)) / 100);
    Apply_Damage_To_Planet_(&candidate,
                            signed16(weapon[0x12]), /* EDX=*/0);
    total += candidate;                            // modulo 2^32
}
return total;
```

The source tests count at the **end** of each loop:
`0x2A797 MOVZX AX,BYTE PTR [combat_ship+slot*11+0x5B]`,
then `0x2A79D CMP AX,WORD PTR [EBP-0x8]`
and signed `JG` back to `0x2A740`. The loop can
execute 0..255 iterations on unchanged original byte count.
It rereads the byte after the effect callback, so a callback
that changes that memory can change the subsequent loop count.

Some intermediate calculations are narrowed back to **signed 16-bit**
at `0x2A745` (spread) and `0x2A75A` (scaled minimum);
the signed `IDIV` operation truncates toward zero.
A host port using floating-point or ordinary real-number
rounding would change those values.

**Do not treat the original `Random_(100)` result as 0..99.**
The recovered original routine returns 1..100 inclusive.
The derived bomb unit-test fixtures were corrected accordingly.

## Derived implementation and independent checks

- `decompilation/reconstructed/fire_bomb_v131.c`
- `tests/test_fire_bomb_v131.c`
- `tests/test_random_fire_bomb_v131.c`
- `decompilation/reconstructed/random_v131.c`

The derived implementation takes checked original-format record
buffers and two callbacks. The **random callback can now be
implemented by the independently reconstructed `Random_`**,
using its original 32-bit seed state. The planet-damage callback
still stands in for the **775-byte**
`Apply_Damage_To_Planet_` routine; its effects are not
simulated by this file.

Compiled under strict C11 warnings and tested with
AddressSanitizer/UndefinedBehaviorSanitizer. Unit tests covered
the entire 0..255 byte firing-count domain, signed negative
damage values, external callback effects, modifications of the
firing count during a callback, and original-format host
bounds. An integrated test feeding the true reconstructed
`Random_(100)` sequence from seed zero produced returns
1, 83, 66, with original final seed 2,802,067,423
after three draws; the derived bomb accumulator and final
RNG state reproduced independently calculated expected
values.

**This is not DOS differential execution.** The original
planet damage helper and caller state, original seed
initialization and all low-level animations/effects must
still be reconstructed and compared before declaring a
game-compatible engine.

No Game Lab website, Xbox controller, or Qwen changes
were made during this reconstruction.
