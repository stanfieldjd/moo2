# MOO2 v1.31 — verified colony morale calculation / UI breakdown boundary

## Question and evidence

Determine which operations inside the original named `Colony_Morale_` procedure affect original colony game-state morale, and which operations only format an optional text breakdown. Examine the official local v1.31 executable and the original exported Watcom function map; never infer gameplay behavior from display strings alone.

Source identity is recorded in `decompilation/annotated/colony_morale_v131.md` and `decompilation/reports/colony_morale_v131_2026-10-16.json`. The untouched local reference executable is SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. No game binaries or original game assets are committed. The raw text-mode instruction extraction is in `analysis/Colony_Morale_.disasm`.

## Source findings

- The named body is exactly 982 bytes at CODE `0xCDB25`; the full body was independently hashed and its complete decoded 280-instruction sequence checked for byte-contiguous coverage.
- `Mixed_Race_Morale_Penalty_` is a directly called 81-byte original helper. It treats distinct low-nibble tags less than 8 as mixed and returns `-4`; early-exit guards are observed on colony `+0x0A` and `+0x137`.
- `Colony_Officer_` and `Owned_Officer_Level_` are original direct calls, with leader flag bits `0x80` and `0x40` selecting distinct formulas. Neither returned bonus should be substituted with guessed faction behavior.
- The original executable has three distinct CODE-resident lookup slices: `0xCD4C4`, `0xCD4CC`, and `0xCD4CF`. Each is matched against original bytes and separately SHA-256 authenticated by `tools/audit_colony_morale_v131.py`.
- Colony BYTE `+0x07` is the gameplay-state output affected by baseline and bonus arithmetic. For government group 3, the procedure directly skips the ordinary accumulation. On other paths, additions use AL and BYTE operations which wrap modulo 256, not a guessed saturation/clamp.
- Text formatting is optional and selected by a non-null EDI pointer at CODE `0xCDD33`. It makes thirteen explicit `sprintf_` calls plus an external shared formatting tail, or copies an external unification message when group 3. This conditional text path is **not** evidence that the gameplay-state BYTE calculation depends on the formatter.
- There are 52 total source-decoded direct branches and calls, and 30 controlled source-derived arithmetic/branch fixtures. The complete branch inventory and all exact callee source addresses are in the evidence JSON report.

## Consequences and open questions

The original code establishes an explicit separation between game-state morale computation and optional descriptive UI construction. Any future native reconstruction must preserve this separation and source-exact BYTE overflow semantics. The valid domain of signed government indices, leader/planet lookup lifetime, external string data and full DOS runtime behavior remain unverified. No runtime differential test or native-game implementation is claimed.

This research does **not** revise the recorded 87% overall executable-decompilation estimate. Its contribution is one independently source-verified 982-byte named function and its directly referenced helper paths.
