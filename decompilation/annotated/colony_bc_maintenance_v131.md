# Colony_BC_Maintenance_ — v1.31 source-verified static reconstruction

## Provenance

- Canonical source: local official ORION2.EXE v1.31 SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
- CODE: extracted Watcom LE object 1, SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`.
- Initialized DATA: extracted Watcom LE object 2, SHA-256 `082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b`.
- Procedure: CODE `0xD094F`, complete named 197-byte body SHA-256 `2a9e964cfbd9c9068ba9998f3d4e8c55ddc39bb4546107fc097a915b6133bfe5`.
- Direct callee: `Event_Check_Space_Anomaly_`, CODE `0x1341E`, complete 80-byte body SHA-256 `dd82062b1a3404b5917ee04dceea3459291b8f96f1fda2b0b9ded5e7041932b4`.
- Original analyzed symbol map: `decompilation/functions.csv`, `decompilation/symbols.csv`.
- Reproduction: `tools/audit_colony_bc_maintenance_v131.py` with official EXE, exact derived CODE object and initialized DATA object. The audit checks complete body digests, source globals, table data, branch/call instructions, and controlled arithmetic fixtures.

## Verified source behavior, expressed as pseudocode

The following is an annotated behavioral interpretation of disassembly, **not** original source code and **not** dynamically verified DOS behavior. Source instruction offsets are specified below.

```c
void Colony_BC_Maintenance_(Colony *c) {
    uint8_t upkeep;
    if (c->byte_0A == 0 || Event_Check_Space_Anomaly_(colony_index(c))) {
        upkeep = 0;
    } else {
        int32_t sum = 0;
        for (int16_t i = 0; i < 49; ++i) {
            if (c->bytes_136[i] != 0)
                sum += ((int16_t *)&_buildings[i].byte_12)[0];
        }
        int32_t base_100 = 100 * (sum + c->byte_114);
        int32_t scaled = base_100 * (100 + _climate_maintenance_modifiers[c->byte_E2]);
        int32_t value = trunc_toward_zero((scaled + 5000) / 10000);
        upkeep = (uint8_t)value; // AL only, no observed saturation
    }
    c->byte_F2 = upkeep;
    c->word_F9 = (uint16_t)(uint16_t(upkeep) - c->word_ED);
    // Shared leave/pop register epilogue at CODE 0xD1F97.
}
```

The real source performs arithmetic through 32-bit signed x86 registers and `IDIV`. The pseudocode describes observed normal arithmetic, not established overflow behavior for all possible game-state inputs.

## Control-flow evidence

- `0xD095A–0xD0967`: zero at colony `+0x0A` causes upkeep `+0xF2` to be set to zero.
- `0xD096C–0xD098C`: compute a colony index by subtracting the global `_colony` base and dividing by record stride `0x169`; call `Event_Check_Space_Anomaly_` at CODE `0x1341E`; a nonzero AX result zeroes upkeep.
- `0xD0994–0xD09BD`: loop over 49 colony building flags at `+0x136+i` (indices 0 through 48). A present building contributes a signed WORD from DATA `_buildings+12+(i*19)`.
- `0xD09BF–0xD09F1`: scale building total plus unsigned BYTE `+0x114` by 100, multiply by `100 + _climate_maintenance_modifiers[BYTE+0xE2]`, add decimal 5000, divide by decimal 10000 using signed x86 `IDIV`; store the low byte into `+0xF2`.
- `0xD09F7–0xD0A0F`: read unsigned BYTE `+0xF2`, subtract the WORD at `+0xED`, save low WORD at `+0xF9`, jump to shared epilogue CODE `0xD1F97`. The source has `mov dx`, not `movzx edx`, but only low 16 bits of subtraction are stored.
- `0xD1F97–0xD1F9D`: shared `leave; pop edi; pop esi; pop edx; pop ecx; pop ebx; ret` tail.
- `0x1341F–0x1346D`: anomaly predicate admits global event codes 2, 4, and 6, and requires the selected colony's planet anomaly byte to match the global WORD event parameter. Returns EAX 1 for match and 0 otherwise.

## Cross-segment data verification

The CODE address `0x6B49` would be unrelated executable material. The load at `0xD09AF` uses a **DATA** reference: global `_buildings` at DATA `0x6B3D`, plus 12 bytes into each 19-byte entry. The 49-entry raw DATA table has SHA-256 `5d20847fb80f0a7668ead6e3afc36300cbce9edf11bee04b77903711800cf9e2`.

The climate modifier source is **CODE** global `_climate_maintenance_modifiers` at `0xCD4BA`: `[50, 25, 0, 25, 0]`. No behavior is claimed for a climate index outside this five-entry observed table.

## Limits and next dependencies

This work establishes a static original-machine-code reconstruction of one callee in `Pre_Import_Computing_`. No complete DOS runtime differential test, complete native port, global upkeep reconciliation, or game-wide feature coverage is claimed. In particular, `Compute_Player_Maintenance_` and the eight other unresolved `Pre_Import_Computing_` callbacks require their own source-anchored audits. Avoid mistaking the shared epilogue for the beginning of another logical gameplay routine.

Do not commit or redistribute original executable, game assets, or proprietary original extracted binary objects.
