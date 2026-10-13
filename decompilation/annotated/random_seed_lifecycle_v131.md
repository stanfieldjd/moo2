# Master of Orion II v1.31 — original random-seed lifecycle

**Status:** Five original Watcom helper bodies have been authenticated
by complete function-byte SHA-256 and original machine-code anchor
checks. Their seed-state operations and the original
`Random_With_Restore_` behavior have been reconstructed in
isolated C. **Not original MicroProse source; not DOS dynamic
equivalence testing; not a complete game-state/save system.**

Authenticated original `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

| Original Watcom function | CODE offset | Entire original body |
| --- | --- | ---: |
| `Set_Game_Random_Seed_` | `0x0007CA` | 28 bytes |
| `Random_With_Restore_` | `0x069F05` | 33 bytes |
| `Set_Random_Seed_` | `0x114820` | 44 bytes |
| `Get_Random_Seed_` | `0x11484C` | 44 bytes |
| `Randomize_` | `0x114878` | 51 bytes |
| **Five complete original function bodies** | | **200 bytes** |

The original DATA object 2 symbols are:

- `_random_seed`: DWORD at `0x41E34`, relocated VA `0x1B1E34`.
- `_cmd_line_seed`: DWORD at `0x1B27C`, relocated VA `0x18B27C`.

## Recovered execution semantics

`Set_Random_Seed_` accepts EAX as a 32-bit seed and
stores it unmodified into `_random_seed`.
`Get_Random_Seed_` reads that DWORD back into EAX.
Both are simple 44-byte original Watcom function bodies
including register/frame preservation.

`Randomize_` zeroes EAX and calls the original
runtime `time_` function (original CODE `0x12C905`),
passing NULL in the original Watcom register protocol.
It then passes the returned EAX value directly to
`Set_Random_Seed_` (CODE `0x114820`).
The derived implementation uses a `time_null` callback;
the host clock and C library ABI are not assumed equivalent
to the original DOS runtime.

`Set_Game_Random_Seed_` invokes
`Check_Release_Version_` (CODE `0x100B5C`) **first**,
then checks the DWORD at `_cmd_line_seed`:

- **Nonzero**: load the command-line seed into EAX and
  tail-jump to `Set_Random_Seed_`.
- **Zero**: tail-jump to `Randomize_`, seeding from
  the runtime time call.

A derived callback explicitly represents the original
`Check_Release_Version_` call. Its independent effects
have not been reimplemented or dismissed.

`Random_With_Restore_` first calls
`Get_Random_Seed_`, stores the saved seed, calls
`Random_(EAX=max)`, then calls `Set_Random_Seed_`
to restore the previous seed. Its return instruction
uses **`MOVSX EAX,BX`**, meaning the result is the
**signed low 16-bit** value of the original random draw.
This is not the same as returning `Random_`'s
full unsigned 32-bit result.

When the argument max is zero, the called original
`Random_` executes unsigned `DIV` with divisor
zero before any normal return, so a DOS machine
exception occurs rather than a completed restore.
The derived helper returns an explicit
`ZERO_BOUND` error and leaves seed unchanged.
That is a deliberate safer-host behavior.

## Implementation and verification

- `decompilation/reconstructed/random_v131.h`
- `decompilation/reconstructed/random_v131.c`
- `decompilation/reconstructed/random_seed_lifecycle_v131.c`
- `tests/test_random_seed_lifecycle_v131.c`
- `tools/audit_random_seed_lifecycle_v131.py`
- `decompilation/reports/random_seed_lifecycle_v131_2026-10-13.json`

The source-audit report stores five full-body digests
and **14 selected original instruction anchors**. The
standalone C was tested with a deterministic
`time_` callback and a dummy preflight callback,
under strict C11 compilation, AddressSanitizer
and UndefinedBehaviorSanitizer.

Tests verified exact seed getter/setter roundtrips,
nonzero command-line seed taking priority over
clock initialization, zero seed requesting the
time callback, repeated seed-preserving random
draws, and host-error behavior. All passed.

## Remaining work

Reconstruct the original command-line parser that
populates `_cmd_line_seed`, the original startup
clock/runtime environment, RNG seed persistence in
save-game data and any additional seed reset sites.
The underlying 128-byte `Random_` generator
has already been reconstructed in
`decompilation/annotated/random_v131.md`.
Its seed initialization is now partially traced,
but **end-to-end original game determinism and
DOS differential equivalence are not yet proven**.

No original executable, LBX, artwork, or music was
committed to GitHub. No Game Lab website, Xbox
controller or Qwen configuration change was made.
