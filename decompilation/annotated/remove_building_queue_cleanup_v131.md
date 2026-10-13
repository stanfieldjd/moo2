# MOO2 v1.31 — building queue cleanup and original ship release

**Status:** Four original construction-queue removal branches in
`Remove_Building_` have been translated into source-backed C,
and the complete original 94-byte `Delete_From_Colony_Queue_`
plus the **99-byte colony-specific compaction routine**
called at CODE `0xA20ED` are reconstructed as independently
testable C. The much larger overall game, original
`Compute_Star_Colony_Stuff_` and all building-removal
cases are **not yet reconstructed**. This is derived,
not original MicroProse source and not DOS differential testing.

Authenticated original `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

## Original executable provenance

| Original CODE body / region | Original CODE offset | Size | Verified |
| --- | --- | ---: | --- |
| `Remove_Building_` | `0x45EA` | 493 bytes | Full original body hash |
| `Delete_From_Colony_Queue_` | `0xA1E19` | 94 bytes | Full original body hash |
| Named `Defragment_Queue_` interval | `0xA20BD` | 147 bytes | Full original named interval hash |
| Anonymous colony-specific compactor, a separately called routine within previous named interval | `0xA20ED` | 99 bytes | Full original region hash |

The original source audit
`tools/audit_remove_building_queue_cleanup_v131.py`
verifies all four SHA-256 digests, **100 exact original x86
instruction checkpoints**, named Watcom source-function
identities and `_colony`, `_ship`, `_planet`
and `_star` DATA globals. Machine-readable evidence:
`decompilation/reports/remove_building_queue_cleanup_v131_2026-10-13.json`.

**Naming correction:** Although the 99-byte compactor at
`0xA20ED` resides inside the 147-byte
`Defragment_Queue_` symbol interval, it has a distinct
entry, stack frame, and original direct CALL target.
The routine beginning at **`0xA20BD`** handles a
different, global queue. The colony queue deletion
helper's original CALL at **`0xA1E6E`** targets
**`0xA20ED`**, not `0xA20BD`.
The implementation and audit deliberately preserve this distinction.

## Building ID dispatch and filtering

The original `Remove_Building_` source clears
colony BYTE `+0x136+building_id` first
(original CODE `0x460A`). Then:

| Original building ID | CODE loop | Original criterion | After loop |
| ---: | --- | --- | --- |
| 8 | `0x4681..0x46D4` | Referenced ship BYTE `+0x10 >=2` | Star-colony recomputation |
| 40 | `0x4681..0x46D4` | Same | Star-colony recomputation |
| 41 | `0x4681..0x46D4` | Same | Star-colony recomputation |
| 22 | `0x4721..0x4775` | Referenced ship BYTE `+0x11 ==2` | Shared return, **no star recomputation** |

The seven signed WORD queue entries are at
`colony+0x115+2*i`, i=0..6.
An entry **−100 or less** represents
an original `_ship` index `-(signed_value+100)`.
The original `_ship` record stride is
**129 bytes (`0x81`)**.

The original loop calls `Delete_From_Colony_Queue_`
with EAX colony ID and EDX queue slot. After a
deletion it decrements the loop index, which is
immediately incremented again by the common
iteration step; consequently it **revisits the same
slot** to process entries that shifted left.

IDs 8, 40 and 41 subsequently use the independently
recovered original **colony → planet → star**
pointer chain, then call the original
`Compute_Star_Colony_Stuff_` with the star
record pointer. The side effects of that named
callee remain an explicit callback in the
derived C. ID22 does **not** call that function
on this original branch.

## Original `Delete_From_Colony_Queue_` effects

Original CODE `0xA1E19..0xA1E76`:

1. Fetch signed queued WORD at the selected original
   `colony+0x115+2*slot`.
2. If that WORD encodes a ship (`<= -100`),
   access original `_ship` record at
   `ship_id*0x81`, setting **BYTE `+0x64` to 5**
   and **WORD `+0x65` to `0xFFFF`**.
3. Call the original anonymous colony queue compactor
   at `0xA20ED` with colony ID and slot.

The compactor shifts queue WORDs
`[slot+1..6]` into `[slot..5]`,
writes `0xFFFF` (−1) to slot 6, and **repeats the
compaction from the same slot if the newly shifted
value at that slot equals −10**. This
preserves the original handling of consecutive
`-10` markers.

Original DOS code reads a queue WORD before an
explicit `-1` slot-index check. The derived C
rejects unsafe negative/out-of-range indexes
instead of reproducing an out-of-bounds read.

## Implemented C and tests

New reconstructed source:

- `decompilation/reconstructed/remove_building_queue_cleanup_v131.c`
- `decompilation/reconstructed/delete_colony_queue_slot_v131.c`
- Existing `decompilation/reconstructed/remove_building_first_write_v131.c`
- Existing direct star-branch
  `decompilation/reconstructed/remove_building_star_recalc_v131.c`

New regression programs:

- `tests/test_remove_building_queue_cleanup_v131.c`:
  all four building-ID branches, repeated queue
  slot visits, appropriate ship status check,
  parent-star callback order, host error guards.
  768 parent-star cases plus one ID22 case.
- `tests/test_delete_colony_queue_slot_v131.c`:
  336 colony/slot/ship-index cases, exact ship-status
  and owner-word writes, queue shift, repeated
  `-10` compaction, and host invalid-pointer tests.
- `tests/test_remove_building_queue_delete_integration_v131.c`:
  all four original building-ID paths with the
  actual source-derived ship reset + queue
  compactor, demonstrating that the outer loop
  revisits shifted positions and star recomputation
  happens only for IDs 8, 40, and 41.

All three tests passed strict C11 compilation
with AddressSanitizer and UndefinedBehaviorSanitizer
on the original-source decompilation computer.
The isolated host API accepts an explicit
maximum number of deletions; this avoids hanging
on a non-progressing callback, a non-DOS safety
difference. The internal deletion helper has
no such callback and models the original source
queue and ship writes directly.

## Outstanding

The source calls to `Compute_Star_Colony_Stuff_`
and other remaining `Remove_Building_` branches
still require substantive decompilation.
The named `Defragment_Queue_` function's
other/global-queue behavior is **not** equivalent
to the anonymous colony compactor and is not
implemented here. No original DOS dynamic
differential test has been run.

No proprietary game executable, artwork or
media was committed to the public GitHub source
repository. No Game Lab website, Xbox controller
or Qwen configuration was changed.
