# Original v1.31 combat weapon-state helper reconstruction

**Status:** three small Watcom functions have complete source-byte
coverage, instruction-supported derived C, and host-side regression
tests. This is **not the original MicroProse C source**, not the
complete firing/ammunition-consumption implementation, and not
differential execution inside the DOS game.

Original authenticated `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

## Three entire function bodies independently identified

| Original Watcom function | CODE offset | Exact length |
| --- | --- | ---: |
| `Weapons_Left_` | `0x26C60` | 60 bytes |
| `Weapon_Is_On_` | `0x3584C` | 32 bytes |
| `Weapon_Is_Off_` | `0x3586C` | 32 bytes |
| **Total** | | **124 bytes** |

The original x86 bytes of *each entire function* were checked using
a source-body SHA-256, in addition to the executable's own checksum.
The verification script also individually decodes **26 selected
machine-instruction sites**, including signed `IDIV`, original
conditional branches, the two 32-byte flag routines and the
original `_combat_data` DATA object global.

Source audit:
`tools/audit_combat_weapon_status_v131.py`.
Evidence:
`decompilation/reports/combat_weapon_status_v131_2026-10-13.json`.

## `Weapons_Left_` — original integer calculation

This routine receives a combat record pointer in EAX and a
signed 16-bit bank/slot index in DX. It calculates:

```
base = record_pointer + 2 * sign_extend(DX)
numerator   = signed_word(base + 0x104)
denominator = signed_word(base + 0x114)

quotient  = trunc_toward_zero(numerator / denominator)   // IDIV
remainder = signed_remainder(numerator, denominator)      // IDIV
if remainder != 0 && numerator > 0:
    quotient = quotient + 1
return quotient
```

This is **not generic mathematical ceiling division** for a
negative denominator. For example, numerator 5, denominator
−2 gives truncation quotient −2, remainder 1, and a final
result of **−1**. The original computes `IDIV` twice, once
for quotient and again for remainder. The routine does not
check for zero denominator, so the original machine would
raise an x86 division exception if it encounters one.

The original per-bank words at `+0x104` and `+0x114`
are within the 313-byte combat record for the eight
weapon banks. No extra widening, float rounding or
unsigned interpretation was introduced in derived C.

## `Weapon_Is_On_` and `Weapon_Is_Off_`

Both routines receive combat ship index AX and
signed weapon-slot index DX. The original:

- Sign-extends AX, multiplies by `0x139` (**313-byte
  combat ship record stride**), then loads original
  `_combat_data` pointer from DATA offset `0x1A864`.
- Sign-extends DX, multiplies by `0x0B` (**11 bytes per
  weapon slot**).
- Compares the status byte at
  `ship+0x5A+11*slot` against literal **1**.

`Weapon_Is_On_` executes `SETE AL`, producing
AL=1 if the byte equals 1 and AL=0 otherwise;
`Weapon_Is_Off_` executes `SETNE AL`, the
logical complement.

**Register caveat:** the original sets **AL only**.
It does not explicitly zero or normalize the full EAX
register before returning. The derived C exports
normalized `uint8_t` booleans; this is faithful
to the observed low-byte result, not necessarily
the entire original register state.

Original routines perform no explicit bounds checks.
The derived C introduces validated ship/slot indexes,
an explicit zero-divisor status, and host memory
guards as **deliberate safety differences**.

## Verification results

Code:
`decompilation/reconstructed/combat_weapon_status_v131.c`

Regression:
`tests/test_combat_weapon_status_v131.c`

The C source was built with strict C11 settings
(`-Wall -Wextra -Werror -pedantic`) and executed with
AddressSanitizer and UndefinedBehaviorSanitizer.

Tests cover positive/negative/zero numerator, positive
and negative denominator, nonzero remainder, large
signed endpoints including `INT16_MIN / -1`,
zero-divisor rejection, each of the eight weapon banks,
and **4,096 flag-byte combinations** covering two
ship records × eight slots × 256 byte values.
All passed.

These tests check our derived implementation against
an independently specified branch calculation and
the recovered structure. **They do not execute the
original DOS code and therefore do not establish full
binary equivalence.**

## Relationship to earlier combat reconstruction

The previous verified
`Is_Ship_Out_Of_Ammo_` (241 bytes),
`Check_For_Launched_Fighters_` (95 bytes),
`Does_Combat_Ship_Have_Special_` (75 bytes),
and `Test_Bit_Field_` (34 bytes) are documented at
`decompilation/annotated/combat_ammo_v131.md`.

Together, these recover weapon usability, some
fighter state, the original special-bitfields,
active-flag tests and the auxiliary remaining-weapon
quotient calculation. They **do not recover the
actual ammunition decrement after firing**, which
must be traced through the original firing routines
(e.g. `Fire_Ship_`, `Fire_Beam_Weapon_`,
`Fire_Missile_`, `Fire_Special_Weapon_`)
and caller dataflow.

The original game remains incompletely decompiled.
No original copyrighted assets are committed.
No changes were made to Game Lab's public website,
Xbox controller support, or Qwen.
