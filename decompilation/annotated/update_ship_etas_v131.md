# MOO2 v1.31 — `Update_Ship_ETAs_` original-source control flow

**Status:** Complete original **253-byte** named `Update_Ship_ETAs_` routine translated as a bounded source-derived C loop with an explicit movement callback. The original **422-byte** `Move_Player_1_Turn_To_Star_` callee is authenticated but **not yet reconstructed**; its movement and collision behavior cannot be replaced by an arbitrary test callback in the finished game.

This is derived C, not original MicroProse source, and it has not been differentially executed against DOS.

Original authenticated `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

| Original Watcom routine | Original CODE offset | Complete source body | SHA-256 |
| --- | --- | ---: | --- |
| `Update_Ship_ETAs_` | `0xF041C` | 253 bytes | `5a1ebf719a02098beadf2b344252ce74850a8f6fc2c978dbb0f21910b603e78b` |
| `Move_Player_1_Turn_To_Star_` | `0xDBB0C` | 422 bytes | `01baaeca994622f9d2d56541ef9b5a5463ffdd619a20054c34c4230e8e2c64cb` |

The caller's shared external Watcom return is CODE `0xEF792..0xEF798`, with bytes `LEAVE; POP EDI; POP ESI; POP EDX; POP ECX; POP EBX; RET` and SHA-256 `1c903070ad87dea1760b46e99addec3215f3983c955b643356bd4e063a57466a`. That return is in the original `Can_Order_Ship_` symbol interval. The caller's prologue `PUSH EBX ECX EDX ESI EDI; ENTER 0x1C` agrees with its shared exit.

The original-byte audit `tools/audit_update_ship_etas_v131.py` verifies the entire two named source bodies, shared epilogue, DATA globals, and **76 specific machine-instruction checkpoints**. Machine-readable report: `decompilation/reports/update_ship_etas_v131_2026-10-15.json`.

## Original ship selection and ETA write

The source uses original DATA globals `_NUM_SHIPS` at `0x21994` (signed WORD), `_ship` at `0x1FF9C` (pointer to **129-byte**, `0x81`, ship records), and `_star` at `0x1B06C` (pointer to **113-byte**, `0x71`, star records).

Original code `0xF0426..0xF045F` scans from the **highest ship index to zero**, selecting ships whose BYTE `+0x64` is 1 or 2. It skips any ship whose **signed owner BYTE `+0x63` equals the original function's supplied EAX low WORD**. The exclusion is counterintuitive but is *verified from the original `JE`*, not inferred from the function name. After building 45 is removed, the caller passes the colony's signed owner, so ETAs are recomputed for eligible ships **not owned by that player**.

The selected ship's destination star is encoded in WORD `+0x65`: subtract **500** for state 1, subtract **1,000** for state 2, and sign-extend the resulting low 16 bits. The original destination star pointer uses `0x71` stride. Target signed coordinate WORDs are at star `+0x0F` and `+0x11`. Initial ship signed coordinate WORDs are at ship `+0x67` and `+0x69`. These ship coordinates are copied to *local* variables and **not updated in the ship record by this ETA routine**.

Original CODE `0xF04B8..0xF0505` repeatedly checks local coordinates against the target and calls original `Move_Player_1_Turn_To_Star_` at CODE `0xDBB0C` until they match. The original call passes:

- EAX = signed ship owner BYTE `+0x63`.
- ECX = destination star index.
- EDX / EBX = signed local X and Y.
- Five stack arguments: unsigned ship BYTE `+0x6C`, mutable local X and Y pointers, an optional byte pointer **only if ship BYTE `+0x6B` is zero**, and a mandatory status-byte pointer.

Each movement call increments the original local **WORD** counter. Once local coordinates reach their destination, only its **LOW BYTE** is written to ship `+0x6D`. An already-arrived ship gets ETA zero. A 300-turn simulated journey therefore writes `300 mod 256 = 44`, consistent with the source-byte truncation.

## Source-derived C, tests and original limits

- `decompilation/reconstructed/update_ship_etas_v131.c`
- `tests/test_update_ship_etas_v131.c`
- `tests/test_remove_building45_star_eta_integration_v131.c`
- `tools/audit_update_ship_etas_v131.py`
- `decompilation/reports/update_ship_etas_v131_2026-10-15.json`

The outer loop is reconstructed using caller-owned original-format arrays and a typed callback for `Move_Player_1_Turn_To_Star_`. The callback is **not** the original movement physics; the real source involves original motion, rounding, helper calls, obstacles, and ship/star state. The complete movement routine must be separately reconstructed before claiming original ETA outcomes.

Standalone tests cover original backward ship ordering, owner exclusion, ship states 1/2 and ignored state 3, destination star ID +500/+1000 encodings, signed coordinates, the conditional optional argument, already-at-destination ships, low-byte ETA wraparound, unchanged stored coordinates, invalid star indices, failed callbacks, and non-progressing callback protection.

The building-45 integration combines:

1. Actual source-derived `Remove_Building_` ID45 flag clear.
2. Full earlier source-derived `Compute_Star_Colony_Stuff_` rebuilding star BYTE `+0x39` and other fields.
3. Source-derived `Update_Ship_ETAs_` reverse traversal, with a deterministic *test-only* movement callback.

It passes all **eight** colony-player owners and confirms star recomputation precedes the ETA update, that eligible ships belonging to a different owner receive the counted ETA, and that ships of the changed owner are skipped.

Both programs compile and pass strict C11, AddressSanitizer and UndefinedBehaviorSanitizer. These are source-consistency tests rather than DOS dynamic differential executions. The C implementation has deliberate safety differences: validation of pointers and star IDs, movement callback failure reporting, and a maximum step count to prevent an unbounded loop. The DOS original lacks these guards, and earlier ship ETA writes are not rolled back if a later host validation fails.

The next essential dependency is the original **422-byte `Move_Player_1_Turn_To_Star_`** plus its own named helper calls. Its source dataflow should be independently authenticated and reconstructed before replacing the callback. The full game, browser engine, and other game systems remain incomplete. Original proprietary game binaries/assets stay private; public Game Lab, Xbox and unrelated Qwen services were not modified.
