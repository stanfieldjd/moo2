# Original MOO2 v1.31 `Colony_Morale_` — source-verified static decompilation

## Provenance and scope

- Official local v1.31 DOS `ORION2.EXE` SHA-256: `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`; the executable and assets are not committed.
- Original Watcom LE CODE image SHA-256: `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`; the raw extracted CODE image is not committed.
- Full named `Colony_Morale_` code body: CODE `0xCDB25..0xCDEFA` (982 bytes), SHA-256 `48ceed247ef96250b8d8f42d877f40be558159fad96e7e1e382c5754fe42cdac`.
- Full original named callee extents separately checked: `Mixed_Race_Morale_Penalty_` (0xCDAD4, 81 bytes), `Colony_Officer_` (0xCD9F2, 68 bytes), `Owned_Officer_Level_` (0x84951, 86 bytes), and `sprintf_` (0x1165F2, 48 bytes). Full SHA digests, 66 exact machine-instruction anchor checks, 280 original decoded instruction addresses, 52 direct transfer edges and 30 controlled source-derived fixtures appear in the auditable report.
- Caller provenance: `Pre_Import_Computing_` directly calls `Colony_Morale_` at CODE `0xD1DB0`; source caller authenticated separately by `tools/audit_pre_import_computing_v131.py`.
- Raw extraction in `analysis/Colony_Morale_.disasm`. Reproducible full-byte and control-flow verification in `tools/audit_colony_morale_v131.py`. Report in `decompilation/reports/colony_morale_v131_2026-10-16.json`.

## Reconstructed source-observable algorithm

This is **pseudocode of original decoded machine instructions**, not recovered original C and not a claim of whole-game native behavioral equivalence. Input types and names are descriptive; original Watcom register liveness and all possible invalid game states are not reproduced. Original player and planet global variables are **DATA** pointers, whereas lookup tables listed below live in the **CODE** image.

```c
void Colony_Morale_(Colony *c, char *optional_display_buffer) {
    int8_t owner = (int8_t)c->byte_00;
    Player *p = _player + (owner * 0xEA9);
    int8_t government = (int8_t)p->byte_89F;
    int32_t government_group = signed_trunc_towards_zero(government / 2);

    // Calls original Mixed_Race_Morale_Penalty_(c) even on the special
    // government-group path, but that return is only added on normal path.
    int mixed = Mixed_Race_Morale_Penalty_(c);
    c->byte_07 = CODE_table_CD4C4[government];  // BYTE assignment

    if (government_group != 3) {
        int officer = Colony_Officer_(c); // original return -1 means none
        int leader_bonus = 0;
        if (officer != -1) {
            Leader *l = _leaders + 0x3B * officer;
            if (l->byte_2B & 0x80)
                leader_bonus = signed_trunc_towards_zero(
                                 (3 * Owned_Officer_Level_(officer) + 4) / 2);
            else if (l->byte_2B & 0x40)
                leader_bonus = Owned_Officer_Level_(officer) + 1;
        }

        int other_a = c->byte_14A ? 4 : 0;
        int other_b = (p->byte_1DA == 3) ? 4 : 0;
        int other_c = c->byte_155 ? 6 : 0;

        int origin_penalty = 0;
        if (p->word_29 == -1 ||
            (_colony + _planet[p->word_29].word_00 * 0x169)->byte_13F == 0) {
            origin_penalty = (int8_t)CODE_table_CD4CC[government_group];
        }

        int tech_or_government_bonus =
            (government_group <= 1 && p->byte_1AA == 3) ? 2 : 0;

        int other_d = 0;
        if (c->byte_14C) {
            other_d = (uint8_t)CODE_table_CD4CF[government];
        } else if (c->byte_138) {
            other_d = (uint8_t)CODE_table_CD4CF[government];
        }

        // Original code adds these to the +0x07 BYTE through AL arithmetic
        // with 8-bit wrapping; order of addition is in the audit.
        c->byte_07 = (uint8_t)(c->byte_07
                       + other_a + other_b + other_c + leader_bonus
                       + mixed + tech_or_government_bonus
                       + origin_penalty + other_d);
    }

    if (optional_display_buffer != NULL) {
        if (government_group == 3) {
            // Original writes _unification_has_no_morale_msg characters.
        } else {
            // Original builds text with a sequence of sprintf_ calls,
            // dependent on the above component contributions.
        }
    }
}
```

The pseudocode intentionally does **not** copy or reconstruct external text strings. In the actual source the result is written to colony BYTE `+0x07` by several separate `ADD BYTE` / `ADD AL` instructions. The conditional `government_group == 3` path jumps directly to the display phase and **skips accumulation of all bonuses and penalties**, although the mixed-race helper is called before the condition.

## Original source evidence for important branches

- CODE `0xCDB2D–0xCDB4C`: owner signed BYTE (colony `+0x00`), player record stride `0xEA9`, government signed BYTE (player `+0x89F`), original signed division by two using `CDQ; SUB; SAR`.
- CODE `0xCDB8A`: `Mixed_Race_Morale_Penalty_` direct call. Its **complete 81-byte original body** checks `BYTE+0x0A >=2` and `BYTE+0x137 ==0`, then traverses packed 4-byte colony entries in reverse and compares their low nibble. Tags at least 8 are ignored. If two considered tags differ, returns `-4`; otherwise 0. The caller holds its result separately.
- CODE `0xCDB92–0xCDBAC`: initial colony `+0x07` assignment from `CODE[0xCD4C4 + signed government byte]`; group 3 skips accumulation and branches straight to `0xCDD33`.
- CODE `0xCDBB4–0xCDBF3`: `Colony_Officer_` direct call. Return `-1` means no leader bonus. Otherwise leader entry stride `0x3B`; bit `0x80` at leader `+0x2B` has priority and computes truncating half of `3*Owned_Officer_Level_+4`. Bit `0x40` without `0x80` uses level +1.
- CODE `0xCDBF6–0xCDC32`: conditional contributions `+4` from colony BYTE `+0x14A`, `+4` from player BYTE `+0x1DA==3`, `+6` from colony BYTE `+0x155`.
- CODE `0xCDC35–0xCDCB2`: government-group check, planet ownership/origin lookup via player WORD `+0x29` and original globals `_planet` and `_colony`. Penalty from original CODE table `0xCD4CC` when the referenced planet is absent or the derived home-colony BYTE `+0x13F` is zero.
- CODE `0xCDCB2–0xCDCC7`: group no greater than 1 and player `+0x1AA==3` contributes 2.
- CODE `0xCDCC7–0xCDD0C`: colony flags `+0x14C` and `+0x138` are **if/else-if** for table at CODE `0xCD4CF`; only one contribution is selected.
- CODE `0xCDD0C–0xCDD30`: five successive `ADD AL` instructions, followed by separate `ADD BYTE [colony+7]` instructions. All direct BYTE arithmetic wraps modulo 256, without observed saturation.
- CODE `0xCDD33–0xCDD50`: when EDI display-output pointer is null, jumps directly to common epilogue CODE `0xCEB17`. Special group-3 path copies the external `_unification_has_no_morale_msg` string and jumps to the same epilogue.
- CODE `0xCDD55–0xCDEF6`: the alternative output path makes **13 direct `sprintf_` calls** (`0x1165F2`) with external string pointers and branch-selected breakdown components. The final JMP to `0xCEB0E` enters a shared last-formatting call and epilogue; that is outside the named 982-byte body.

## Authenticated constant tables in original CODE

| Original CODE slice | Original unsigned bytes | Signed byte interpretation |
|---|---|---|
| `0xCD4C4..0xCD4CB` | 252, 252, 252, 0, 0, 0, 0, 0 | -4, -4, -4, 0, 0, 0, 0, 0 |
| `0xCD4CC..0xCD4CE` | 246, 249, 252 | -10, -7, -4 |
| `0xCD4CF..0xCD4D6` | 4, 4, 4, 4, 0, 0, 0, 0 | +4, +4, +4, +4, 0, 0, 0, 0 |

All table bytes and their SHA-256 digests are verified in the audit against the locally supplied original code image.

## Confidence and limitations

Verified at E1/E2 source and audit level: executable and complete-body bytes, decoded 982-byte instruction coverage, all outgoing direct CALL/JMP/Jcc transfers, named helper targets, CODE versus DATA reference identity, original table values, selected byte-write/conditional paths, and 30 controlled source-derived cases. The original DOS runtime was **not** executed for a differential comparison, and there is no new native gameplay port. The remaining limitations include external formatter-data content, unknown valid ranges for signed government/planet indices, complete leader/player state lifecycles, register aliasing beyond the modeled small fixture domain, and alternate entry points outside the identified caller.
