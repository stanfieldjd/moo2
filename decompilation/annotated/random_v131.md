# Original Master of Orion II v1.31 `Random_` — complete seed/result reconstruction

**Status:** the original Watcom support routine is fully matched by
source-function byte hash, 20 instruction anchors, named seed global,
and a portable C translation of the state/result calculations.
The derived C is tested with deterministic seed sequences and the
`Fire_Bomb_` calculation. It is not original MicroProse C,
not DOS dynamic equivalence testing, and does not establish
how the game initially seeds its RNG.

Authenticated original `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

Original Watcom routine `Random_`, CODE offset
`0x1147A0..0x11481F`, **128 bytes**.
Original function-body SHA-256:
`fed72b3293ed869db1e3ff6c93477767f0322794a2185d18c95798a49c92ff56`.

Original mutable DATA object 2 DWORD `_random_seed`
at offset **`0x41E34`**, relocated virtual address
`0x1B1E34`. The original runtime's calling convention
supplies an unsigned maximum in EAX, returns an
unsigned result in EAX, and mutates that global seed.

## Exact original integer sequence

For a **nonzero** 32-bit maximum `n`:

```c
// Equivalent mathematical dataflow with unsigned 32-bit wrapping.
divisor = UINT32_MAX / n;
limit = divisor * n;
do {
    random_seed = random_seed * 0x41C64E6D + 0x3039; // mod 2^32
} while (random_seed >= limit);
return 1 + random_seed / divisor;
```

The source instructions at original CODE
`0x1147E1..0x1147F0` implement the linear-congruential
step, and `0x1147F8..0x1147FE` implement
the unsigned rejection criterion. This discards
values in the incomplete upper interval so the
remaining divisions have equal-sized bins.
The resulting range is **1..n inclusive**.

A subtle and important edge case:
the code executes `DIV [EBP-0x14]` at **`0x1147C2`**
*before* its source's apparent zero-maximum test
at `0x1147D2`. Therefore `Random_(0)` triggers
a hardware divide-by-zero exception in the original
routine. The subsequent branch that would return 1
for zero input cannot be reached through the
ordinary entry path. Our derived C returns explicit
`ZERO_MAXIMUM` status instead, a deliberate host
safety difference.

## Verified deterministic fixtures

Starting with seed 0 and requesting `Random_(100)`
five times, the original formula produces returns:

```
1, 83, 66, 84, 6
```

The corresponding updated seeds are:

```
12345, 3554416254, 2802067423, 3596950572, 229283573
```

Rejection-loop fixture:
seed `0x0DBDBB1E` yields first updated value
`0xFFFFFFFF`, which is rejected for maximum 100,
then accepts `0xBE39E1CC`, returning **75**.
The original inclusive limit for 100 is
`0xFFFFFFA0`. The seed advances on *every*
rejected attempt, and that state change is
preserved in the derived implementation.

## Code and test artifacts

- `decompilation/reconstructed/random_v131.c`
- `tools/audit_random_v131.py`
- `decompilation/reports/random_v131_2026-10-13.json`
- `tests/test_random_v131.c`
- `tests/test_random_fire_bomb_v131.c`

The pure C helper takes a caller-held `uint32_t`
seed pointer instead of writing a DOS global address.
This allows the actual source seed to be provided
by an original-format runtime state module when
one exists. Exact wraparound arithmetic is handled
with unsigned 32-bit integers.

The C tests check original numeric seed fixtures,
range bounds, reproducibility, retry after rejection,
maximum 1, maximum UINT32_MAX, zero argument and
null-pointer safety. They passed strict C11
compilation with AddressSanitizer/UndefinedBehaviorSanitizer.

The `Fire_Bomb_` integration uses the recovered
Random_ output 1, 83, 66 from seed zero for its
first three 1..100 rolls. It reproduces the expected
planet-candidate damage accumulator under a
**test-only** planet-effect callback.

## Outstanding

Locate and reconstruct every original `_random_seed`
initialization and save/load field; trace any alternate
randomness helpers and unexpected concurrent access.
The `Apply_Damage_To_Planet_` function and other
bomb/combat effects remain independent incomplete
gameplay work. Original-seed existence alone is not
proof that the complete game behaves identically
to the derived C across dynamic DOS execution.

Original proprietary game files remain private.
Game Lab, Xbox controls, and Qwen are unchanged.
