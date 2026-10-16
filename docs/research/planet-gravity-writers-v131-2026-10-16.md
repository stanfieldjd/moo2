# Original MOO2 v1.31 gravity state creation and home-world normalization

Investigation of the gravity-factor helper's unmodeled original input values located **original initialized Watcom DATA `_gravity_table` at `0x572A`**, not CODE. Its 25 authenticated BYTE values are:

```text
0 0 0 1 1
0 0 1 1 1
0 1 1 1 2
1 1 1 2 2
1 1 2 2 2
```

Original `Enforce_Mineral_Richness_` at CODE `0x6B4DA` indexes this table as `5 * planet BYTE +0x0A + planet BYTE +0x05` and writes the selected BYTE to source planet BYTE `+0x06`. All original 5×5 table outputs are **0, 1 or 2**, matching the bounded gravity-factor audit. The original code does not validate out-of-range selectors, so source correctness for abnormal inputs is not inferred.

The original `Modify_Home_Worlds_` overrides the gravity code using the source owner's race settings: if player BYTE `+0x8A9` is nonzero it chooses **0**, else if player BYTE `+0x8AA` is nonzero it chooses **2**, else **1**, then calls source `Enforce_Gravity_`. The original `Enforce_Gravity_` writes the selected BYTE to the same planet `+0x06` field. Under the source original normal owner-population setting, all four boolean combinations of those two options produce gravity factor **4** and therefore zero gravity penalty at this stage. Other population tags or planets may follow different original branches.

Source verified by canonical local official `ORION2.EXE` v1.31 SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`; extracted CODE SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`; initialized DATA SHA-256 `082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b`. Full four named original function bytes, direct CALL edges, 294 machine instructions, 30 decisive opcode anchors, entire DATA table and 159 bounded fixtures are authenticated in `tools/audit_planet_gravity_writers_v131.py` and its machine-readable report `decompilation/reports/planet_gravity_writers_v131_2026-10-16.json`. Detailed original source locations and important caveats are in `decompilation/annotated/planet_gravity_writers_v131.md`.

No original DOS dynamic test, proven global valid-state domain, gameplay correction, full native implementation or recomputed executable completion percentage is claimed. Original game assets and website are unchanged.
