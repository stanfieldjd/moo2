# Original v1.31 `Apply_Bomb_Hits_`: shared-epilogue routine

**Status:** original 95-byte named function and its external
seven-byte shared return are independently byte-hash verified.
The entire visible loop has been reconstructed in isolated C
with explicit callbacks for the actual ordinary and biological
hit resolvers. **The resolver functions are not reimplemented
here, and this does not complete the planet/combat engine.**

Original authenticated `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

- Watcom `Apply_Bomb_Hits_` original CODE `0xCD2F2..0xCD350`;
  **95 source bytes**, SHA-256
  `baec81af1f295344473a9fe92e85220822ba595802e3e81b130efd2bcce538a4`.
- A conditional branch at `0xCD31F` jumps to **`0xCCDA5`**,
  outside the named function interval.
- That shared epilogue comprises **7 bytes**
  (`LEAVE; POP EDI; POP ESI; POP EDX; POP ECX;
  POP EBX; RET`) at `0xCCDA5..0xCCDAB`,
  SHA-256
  `1c903070ad87dea1760b46e99addec3215f3983c955b643356bd4e063a57466a`.
- The `Apply_Bomb_Hits_` prologue pushes
  `EBX ECX EDX ESI EDI` and enters a 4-byte local
  frame, so the external epilogue restores its
  stack/register layout correctly.
- The shared return occurs inside the original
  `Handle_Leader_At_Lost_Colony_` named function interval.
  This is a **real cross-function control-flow edge**.
  Linear exported function-interval CFGs that exclude
  that target misrepresent `Apply_Bomb_Hits_` completion.

The read-only original audit:
`tools/audit_apply_bomb_hits_v131.py`.
Source-byte report:
`decompilation/reports/apply_bomb_hits_v131_2026-10-13.json`.
It independently verifies the original body and epilogue
SHA-256 hashes and **40 original instruction sites**,
including named direct calls.

## Original combat result-event layout

The input EAX is a pointer to a structure large enough
for the fields below. These are original byte offsets,
not a standalone documented game save format.

| Result-event offset | Original access | Observed purpose |
| --- | --- | --- |
| `+0x01` | unsigned BYTE | Index into original `_colony` pointer, 361 bytes per colony |
| `+0x03` | signed WORD | Ordinary bomb-hit count loaded into ESI |
| `+0x06` | signed WORD | Biological-hit count loaded into EDI |
| `+0x45` | DWORD | Accumulator incremented by returned ordinary-hit values |

The original `_colony` global resides at
DATA object 2 offset `0x1AB18`.

## Recovered control flow

```c
// Derived pseudocode, NOT complete original effects or DOS ABI.
colony = _colony + 361 * unsigned_byte(event[1]);
normal = signed16(event + 3);
biological = signed16(event + 6);
while ((int32_t)(normal + biological) > 0) {
    if (biological != 0) {
        Resolve_Biological_Hit_(colony, event);
        biological--;
    } else {
        int32_t n = Resolve_Bomb_Hit_(colony, normal, event);
        if (n != 0) {
            normal -= n;
            event->dword_at_0x45 += n; // 32-bit machine wraparound
        } else {
            normal = 0;
        }
    }
}
return (int32_t)(normal + biological); // shared external epilogue
```

The original ordinary resolver is named
`Resolve_Bomb_Hit_` at CODE `0xCCEBD`,
641 bytes; the original biological resolver is
`Resolve_Biological_Hit_` at CODE `0xCD13E`,
436 bytes. These are separate outstanding
decompilation targets.

The original **prioritizes a nonzero biological count**,
calls its resolver, then decrements the local
biological count. Only when that count becomes
zero does it attempt normal hit resolution. The
ordinary resolver's returned EAX both decrements
the local pending ordinary count and increments
the result-event DWORD at `+0x45` when nonzero.
When EAX is zero, the original clears the local
normal count. It does not automatically write
either original hit-count WORD back to the event
during these local decrement operations.

## Derived C and tests

- `decompilation/reconstructed/apply_bomb_hits_v131.c`
- `tests/test_apply_bomb_hits_v131.c`

The C port uses callbacks for the two unresolved
original hit resolvers. It validates the event
allocation (at least 73 bytes), colony index, and
colony-record count. It also adds an explicit
maximum callback-iteration safety cap in case
malformed state or a nonprogressing resolver
would otherwise cause an unbounded loop.
These are **modern safety differences** not
present in the original DOS implementation.

The regression tests cover biological-before-normal
ordering, ordinary resolver returning multiple
consumed hits, zero-result clearing of local count,
32-bit event accumulation wraparound,
immediate negative/zero-sum shared returns,
invalid pointers/indices, and the host safety cap.
They compiled under strict C11 warnings and
passed AddressSanitizer/UndefinedBehaviorSanitizer.

Tests exercise the recovered loop and controlled
callbacks, **not** the original DOS executables
or unresolved hit-resolver side effects.

## Next work

Reconstruct original `Resolve_Bomb_Hit_`
and `Resolve_Biological_Hit_`, then remove the
callback stand-ins only after verifying their data
writes and all branch paths. Reconcile those
results with the full `Apply_Damage_To_Planet_`
branch map, `Fire_Bomb_`, original `Random_`,
and remaining game turn/save systems.

No Game Lab website, Xbox controller,
Qwen service or original copyrighted game
assets were modified in this pass.
