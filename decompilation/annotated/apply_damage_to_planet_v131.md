# Master of Orion II v1.31 — planet damage and defense helper reconstruction

**Source:** authenticated original `ORION2.EXE`, SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
Original unpacked LE CODE object 1 is 1,410,709 bytes.

**Status:** complete original source-byte provenance and selective,
instruction-supported C reconstruction of two planet-damage
subexpressions, plus a complete 92-byte source-backed colony-defense
packing helper. **The 775-byte `Apply_Damage_To_Planet_` is NOT yet
fully translated into equivalent C.** Neither the original MicroProse
sources, copyrighted game assets, nor any DOS differential test
run are included or published.

## Original 775-byte `Apply_Damage_To_Planet_`

Original Watcom CODE offset `0x2A3C3`, size **775 bytes**.
Whole original function SHA-256:
`36b773f8747c65d082b0458980138d9df024c44f2fbe5b38e0c133780e262212`.

The independent read-only source audit
`tools/audit_apply_damage_to_planet_v131.py` verifies the
complete function digest and **65 selected instruction locations**,
all seven original named helper targets and nine named DATA symbols.
Report: `decompilation/reports/apply_damage_to_planet_v131_2026-10-13.json`.

At entry, the original caller `Fire_Bomb_` passes
EAX = pointer to a candidate damage value, EBX low16 = a weapon
definition flags/parameter WORD at `+0x12`, and EDX = 0.
The original code saves the pointer in ECX and the low 16-bit
flags in `[EBP-0x4]`.

The routine does not merely multiply damage by armor. Its observed
branch topology includes the following independently decoded paths.

### Biological branch — original flag 0x80

- `0x2A40D TEST BYTE PTR [EBP-0x4],0x80`;
  branch at `0x2A411` chooses conventional path when clear.
- The biological branch sets the original named
  `_bio_weapon_flag` global at DATA `0x218E2` to 1 and
  writes original `_combat_bomb_result` fields. An original
  combat-state byte `ship+0x26 == 0x17` causes an early exit.
- It loads `_combat_defender_player` at DATA `0x2188E`,
  indexes `_player` records with **3,753-byte**
  (`0xEA9`) stride and checks record bytes
  `+0x182` and `+0x1D8`.
- If the first field equals 3, the original modifies the
  candidate signed 16-bit WORD by **division by 2 truncating
  toward zero** (`CWD; SUB AX,DX; SAR AX,1`).
  Otherwise if the second field equals 3, it divides by
  **4 truncating toward zero** (`CWD; SHL DX,2;
  SBB AX,DX; SAR AX,2`). The first field **takes precedence**.
  In other cases the candidate remains unchanged.
- It calls original `Random_(100)` at CODE `0x2A485`;
  the original generator returns **1 through 100** inclusive.
  `CMP EAX,EDX; JG` skips the subsequent biological-hit
  path if roll is greater than the **signed 16-bit** candidate.
- Subsequent original `_combat_bomb_result` mutation and
  `Apply_Bomb_Hits_` at CODE `0xCD2F2` require additional
  reconstruction. No derived code claims to replace these effects.

The threshold arithmetic is isolated at
`decompilation/reconstructed/planet_bio_threshold_v131.c`.
The regression
`tests/test_planet_bio_threshold_v131.c`
compared all **65,536 original bit patterns** across
all four combinations of the two field checks:
**262,144 comparisons** against an independent model
of the Watcom 16-bit x86 arithmetic. It also tested
15,100 source `Random_(100)` comparisons.

`tests/test_planet_bio_random_integration_v131.c`
feeds original `Random_(100)` seeded results into the
threshold test and verifies the seed state. All compiled
under strict C11 and passed ASan and UBSan.

### Conventional branch — original special ID 7

The conventional branch begins at CODE `0x2A4EF).
It calls `Does_Combat_Ship_Have_Special_` with
EAX=0, EDX=7. When AX equals 1, it executes
`CWD; SHL DX,2; SBB AX,DX; SAR AX,2;
MOV WORD [ECX],AX; DEC WORD [ECX]`.
The observed result is:

```
result_word = trunc_toward_zero(signed16(candidate_word) / 4) - 1
// stored with the original 16-bit DEC wraparound semantics
```

If original special query result is not exactly 1,
these specific instructions leave the candidate unchanged.

This bounded subexpression is isolated at
`decompilation/reconstructed/planet_special7_damage_v131.c`.
`tests/test_planet_special7_damage_v131.c`
independently models CWD/SHL/SBB/SAR/DEC and matches the
derived result for **all 65,536 signed WORD patterns**.
It deliberately does not emulate the whole special-bitfield
helper, original global effects or the colony-damage branch.

After this adjustment the original code calls
`Does_Combat_Planet_Have_Defenses_` at `0x2A51A`.
The remaining conventional path reads/writes original
combat ship record fields `+0x29`, `+0x2B`,
`+0xC0`, `+0xAA`, checks original
`_cmbt_colony_id` and `_apply_damage_to_planet`,
and can call `Destroy_Colony_Defense_` and
`Apply_Bomb_Hits_`. Those original side effects
are not replaced by the isolated adjustment function.
At `0x2A6C2` the original writes a **16-bit**
updated value into the input pointer. At `0x2A6BF`
it returns a different local DWORD in EAX, so
do not substitute the return for the in/out damage value.

## Complete 92-byte `Does_Combat_Planet_Have_Defenses_`

Original CODE `0x2A142..0x2A19D` inclusive, **92 bytes**.
Complete function-body SHA-256:
`2e091e1f69040da609a1c6935910251caff5b38a071d45b5a1e7936488ee13c9`.

Original named globals:

- `_cmbt_colony_id` at DATA `0x21878`, signed WORD
- `_colony` at DATA `0x1AB18`, pointer to
  original **361-byte (`0x169`) colony records**

A colony ID of −1 branches to return zero.
Otherwise the code reads four byte fields at
colony record `+0x150`, `+0x151`, `+0x160`,
`+0x165` and computes the lower 16-bit result:

```
packed = field150 | (field151 << 1)
       | (field160 << 2) | (field165 << 3);
```

This is a **bitwise OR**, not addition, and the
fields are *not* assumed to contain only 0 or 1.
Consequently the result is not strictly a boolean.

**Register-width caveat:** original instructions
`MOVZX SI`, `MOVZX CX`, `MOVZX DX`,
and `MOVZX AX` populate only the low 16 bits
of 32-bit registers. This gives an exact lower
16-bit packed output but does not, by itself,
prove that the original upper half of EAX
is zero. The planet-damage caller uses
`TEST AX,AX`, which consumes the documented
lower half. The host C API deliberately returns
a normalized 32-bit packed value and checks
valid array indexes.

- Derived C:
  `decompilation/reconstructed/combat_planet_defenses_v131.c`
- Source audit:
  `tools/audit_combat_planet_defenses_v131.py`
- Evidence:
  `decompilation/reports/combat_planet_defenses_v131_2026-10-13.json`
- Regression:
  `tests/test_combat_planet_defenses_v131.c`

The source audit verified the full original body,
**20 machine-instruction anchors**, the two named
globals, and the signed −1 case. The C tests
verified **66,560 packed-field cases** with strict C11,
AddressSanitizer and UndefinedBehaviorSanitizer.

## Next original-code reconstruction boundary

Recover the full `Destroy_Colony_Defense_` and
the remaining global writes in `Apply_Damage_To_Planet_`,
including colony defense and biological-hit results.
The `Apply_Bomb_Hits_` (95 bytes) loop is already
reconstructed with explicit callbacks; both underlying
hit-resolver original bodies are now byte-hash verified
(641 and 436 bytes) and their target selection and
original RNG draws are reconstructed, while mutation
side effects remain incomplete. See
`decompilation/annotated/colony_hit_resolvers_v131.md`.
Integrate them with `Fire_Bomb_` and the now-verified
original `Random_` state machine. A full game engine
requires combat turn handling, galaxy-generation and
game-state/save logic as well.

**No public Game Lab files, Xbox controller handling,
Qwen services or original copyrighted game assets
were modified in this pass.**
