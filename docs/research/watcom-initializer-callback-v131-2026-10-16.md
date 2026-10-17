# Authenticated Watcom DOS v1.31 original initialization callback

The original Master of Orion II DOS v1.31 executable has SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Original CODE object SHA-256 is `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. Its original initialized DATA image SHA-256 is `082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b`. These game binaries are **not** included in GitHub.

## The last apparently unrecognized runtime entry

The previous full 32-bit CFG recorded original CODE address `0x12F1D8` as an *unproven synthetic function* (`anon_runtime_0012F1D8`) because its source instruction start had been lost inside the prior Watcom compiler symbol span. We have now recovered authoritative **original initialization-table provenance**, not merely an appealing eight-byte instruction decode.

At original initialized DATA object offset `0x12FF2`, the authentic third six-byte `__InitRtns` record contains:

```text
00 20 D8 F1 12 00
|  |  \___ original CODE offset 0x12F1D8 (little-endian)
|  \______ Watcom priority 32
\_________ initialization state 0
```

The original Watcom initialization dispatcher `__InitRtns` is a complete 75-byte executable source body, CODE `0x12EF6C..0x12EFB6`, with full SHA-256 `5d6e1ef83bad86b6e9a0d8c05c3f61d36e1f57a957ebd7e5c0b2749c06677af9`. Its original instructions establish the complete mechanism:

- `0x12EF73`: `3E BE E6 2F 01 00` — start of initializer array at original `0x12FE6`.
- `0x12EF79`: `3E BF 10 30 01 00` — end of initializer array at original `0x13010`.
- `0x12EF96`: `83 C6 06` — six-byte record stride, seven records in the exact source range.
- `0x12EF9F`: `8B 43 02` — loads callback CODE pointer from record DWORD at byte offset +2.
- `0x12EFA9`: `FF D0` — actual indirect **CALL EAX** to original callback.

The third original initializer record has no Watcom-named target, but its original machine callback CODE body at `0x12F1D8..0x12F1DF` has exactly eight source bytes `66 8C 15 34 CA 00 00 C3` and full SHA-256 `661acfe780d89bf88734a87eae4bfd629555259e4bb02cc56b2180b46427a098`. The source instructions are `MOV WORD PTR DS:[0xCA34],SS` and `RET`. This is compiler/runtime segment register initialization, not a reconstructed game decision or evidence that Windows 95-specific native code was present.

## Complete global conservative CFG comparison

The source-authenticated exporter `tools/export_resynchronized_disassembly.py` now requires the original initialized DATA image, checks its source fingerprint, validates the complete dispatcher, source table record, and callback bytes, and restarts CODE disassembly **only** at that proven original callback entry. The exporter produces 5,580 code decoding segments rather than 5,579. Its source CFG results differ in exactly one entry:

| Source measurement | Before | After |
|---|---:|---:|
| Original/synthetic CODE function entries | 5,635 | 5,635 |
| Per-function CFG instruction memberships | 396,305 | **396,307** |
| Provisional boundary matches | 5,039 | **5,040** |
| Failed CODE entry decoding | 7 | **6** |
| Raw conservative CFG unresolved edges | 20 | **19** |
| `anon_runtime_0012F1D8` reachable original instructions | 0 | **2** |

All other 5,634 source function memberships are unchanged. The previously unproven synthetic entry now has a source **initializer caller/entry record**; no guessed target or branch was inserted.

Independent reproducibility: `tools/audit_watcom_init_callback_v131.py`, structured report `decompilation/reports/watcom_init_callback_v131_2026-10-16.json`, regenerated `decompilation/resynced_disassembly.json` and `decompilation/function_cfg_extents.*`. Prior source-compatible mode/data evidence separately explains the **19 residual apparent i386 CFG edges** using real-mode routines, inline CODE data, mixed storage and runtime markers. The global raw count is still **19**; this does not mean every underlying executable path, runtime semantic, or native game feature has been recovered.

The original game executable, assets, website, and server were not changed. Dynamic original DOS comparison and native browser-playable game/graphics/controller implementation remain incomplete.
