# Decompilation checkpoint: game indirect calls and mixed-mode code
**Date:** 2026-10-13  
**Scope:** Master of Orion II v1.31 control-flow/source reconstruction, **not** gameplay testing

## Source and safeguards

Authenticated original `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
Code: original LE object 1 (1,410,709 bytes) analyzed through its
relocated local representation, based at preferred VA `0x10000`.
Data: locally reconstructed LE object 2, relocated for analysis.
Original executables, media, relocatable object images, and raw machine
code remain **local** and are never deployed to the public Game Lab site.

Two reproducible read-only audits have now run successfully on the verified
original and its relocated objects:

```bash
python3 tools/audit_game_indirect_calls.py \
  --exe "$MOO2_V131_EXE" \
  --code "$RELOCATED_CODE_OBJECT" \
  --data "$RELOCATED_DATA_OBJECT"

python3 tools/audit_decode_exceptions.py \
  --exe "$MOO2_V131_EXE" \
  --code "$RELOCATED_CODE_OBJECT"
```

The generated metadata, without the game image, is committed as:

- `decompilation/reports/game_indirect_call_audit_2026-10-13.json`
- `decompilation/reports/decode_exception_audit_2026-10-13.json`

## Game-code indirect calls: 19/19 provenance categories recorded

`indirect_transfers.csv` has **193** indirect CALL sites overall.
Cross-referencing their owning Watcom module shows **19** in the 133
core game-code modules and **174** in support/runtime/library modules.
This split is by *originating module*, not dynamic reachability.
No remaining target is guessed.

| Orig. CODE call offsets | Procedure | Observed target provenance |
| --- | --- | --- |
| `0xCDFF0`, `0xCE24E` | `Colony_Pop_Prod_Produced_`, `Colony_Pop_Base_Prod_Produced_` | Shared indexed 7-DWORD table at LE data offset `0xB55C`, with only slots 0–2 populated |
| `0xC7EBC`, `0xC7FDB` | `Ship_Rough_Strength_At_Star_`, `Ship_Min_Strength_Versus_Players_At_Star_` | Conditional stack-local function pointer; original instructions store one of two exact CODE entries |
| `0xF3031`, `0xF3049`, `0xF3077`, `0xF309B` | `_Squeeze_Print_Paragraph_` | Four calls through the same stack-local pointer, selected from two constant CODE entries |
| Other 11 sites | See audit JSON | Caller-provided, object-field, or runtime-assignable callback; cannot be treated as a resolved target |

### Recovered static target sets

**Colony dispatch** (data table offsets `0xB55C..0xB578`):
the *original* initialized DWORD values are
`0xCE0C6`, `0xCED47`, `0xCFE77`, then **four zeros**.
After LE relocation they are `0xDE0C6`, `0xDED47`, `0xDFE77`, then
four zeros. Exact Watcom CODE-entry symbols:

- index 0: `Colony_Empire_Base_Food2_Produced_`
- index 1: `Colony_Empire_Base_Industry_Produced_`
- index 2: `Colony_Empire_Base_Research_Produced_`

**Ship dispatch**: conditional instructions store relocated code pointers
`0x5EF09` and `0x5EF17` before indirect calls. They map to original CODE
entries `Ship_Strength_Vs_Ships_In_Nebula_` and
`Ship_Strength_Vs_Ships_`. Both call sites were confirmed separately.
The choosing condition is visible in disassembly; broader strength-rule
equivalence and compiler calling conventions are still pending.

**Paragraph dispatch**: two literal relocated code pointers
`0x103CAF` and `0x103952`, corresponding to original CODE entries
`Get_Formatted_Paragraph_Max_Height_` and
`_Get_Paragraph_Max_Height_`. They feed the same stack local used by
four calls. Their status is **statically bounded**, not proof that either
target has been ported.

**Remaining 11** are not unknown table entries. They are:
`Execute_Auto_Function_`, `Fade_Into_Screen_`,
`Draw_Generic_Score_`, `Draw_Generic_Vertical_Scroll_Bar_`,
`Find_Planet_At_Star_Satisfying_`, `Kill_Buildings_`,
`Update_List_Window_Data_`, `FN_User_Call_`,
`Display_Selected_List_Text_`,
`Display_Selected_List_Text_For_Tech_List_`,
and `Draw_Icon_Group_`.
Their pointer origins are classified and recorded per site.
Specifically the data callback slot for `FN_User_Call_` is
initialized to **zero** in the original data object. A runtime assignment
must be independently traced before assigning it a target.

**Important accounting:** eight sites have bounded, named static target
sets; **eleven** remain runtime-dependent. This is a target-provenance
classification, *not* 8 completed C functions or a proof that all
game indirect control flow is known.

## Original game switch-table coverage — expanded and corrected

**The prior 118-game-switch inventory was incomplete.** Its independent
source-byte audit was correct *for those 118 exported sites*, but linear
disassembly missed additional indexed jumps, including original
machine instructions after embedded dispatch-table data. It must not
be interpreted as exhaustive original game-code coverage.

The original bounded-export baseline was 135 switch tables across all
modules (118 game, 17 support) with 1,080 original case entries.
The prior game subset contained 943 case entries and 800 distinct
case destinations. The audit remains at
`tools/audit_game_switch_coverage.py` and
`decompilation/reports/game_switch_coverage_2026-10-13.json`.

The expanded original-byte audits subsequently added:

- **68 game-code CS-indexed SIB switches** omitted from that export,
  with **537** bounded table entries. 67 have nearby CMP/JA
  upper-bound evidence; one has a source `REPNE SCASW` scan
  with original count 14
- **1 further game-code prescaled switch**, in
  `Do_Colony_Info_Military_Stuff_For_` at CODE `0xACF3E`
- **1 support-code prescaled switch**, in
  `Farload_Library_Data_` at CODE `0x117190`, which selects
  the original four allocation modes

A separate source-hash-guarded reconciliation independently
rechecked the original DWORD values and ensured the old and new
site inventories did not overlap:

| Verified static inventory | Distinct switch sites | Case entries |
| --- | ---: | ---: |
| Game modules | **187** | **1,484** |
| Support/runtime modules | **18** | **141** |
| **All currently recovered** | **205** | **1,625** |

- `tools/audit_omitted_game_switches_v131.py`
- `tools/audit_omitted_prescaled_dispatches_v131.py`
- `tools/reconcile_v131_switch_inventories.py`
- `decompilation/reports/reconciled_switch_inventory_v131_2026-10-13.json`

This **remains a lower bound**. These audits are scoped to source-export
tables and two observed original x86 indexed-jump instruction families.
Other indirect-transfer encodings or missed symbol entries might still
be absent. Static DWORD branch-target provenance is not proof of
runtime reachability, full case semantics, or equivalent C recovery.
The separate 311 cross-function conditional-branch inventory
still requires calling-convention and entry-alignment review.

## Cross-function conditional branches: target-byte audit

The 311 previously flagged cross-function conditional branches break down
by source module into **250 from game-code modules** and **61 from
support/runtime modules**. An independently reproducible byte-level
review against the exact original LE object found that:

| Scope | Targets beginning with a Watcom-compatible return epilogue | Others requiring CFG review |
| --- | ---: | ---: |
| Game modules | **158** | **92** |
| Support/runtime modules | **1** | **60** |

The epilogue classifier requires exact target bytes matching an
optional `LEAVE`, zero or more register `POP` instructions, followed
by `RET` or `RET imm16`; it does not guess from neighboring
symbol names. For example, game branches aimed at original code
offset `0xD1F97` land on `LEAVE; POP EDI; POP ESI; POP EDX; POP ECX;
POP EBX; RET`, while branches to `0xCEB17` land on a separate
verified shared exit sequence.

This supports treating many of the 311 anomalies as **shared
epilogue candidates rather than missing code**, but byte-pattern
membership alone does not validate caller-specific stack layout,
reachability, or semantic equivalence. The remaining **92 game-origin
targets** require address-by-address CFG review. All 311 classifications
are reproducible with `tools/audit_conditional_epilogues.py`; original
machine-code bytes stay local.

## Second-pass audit of the 92 non-simple-epilogue game branches

**The older `function_boundary_audit.csv` uses independently decoded
symbol intervals, then records only the first outward direct jump; it
does not prove that instruction is reachable from the routine's entry.**
Accordingly, the original 311-branch report is an anomaly inventory,
not a list of 311 proven broken control-flow edges.

An additional source-hash-guarded tool,
`tools/audit_entry_reachability.py`, starts at each original function
entry, walks decoded direct fall-through and branch paths inside that
symbol's provisional interval, incorporates previously verified switch
cases, and checks whether the recorded branch source was traversed.

**Results for the 92 non-simple-epilogue game-origin candidates:**

- **63** branch instructions were reachable from the original symbol
  entry under this *bounded direct-CFG* method.
- **29** were **not established** as reachable by that method.
  These are *not proven dead code*: indirect control transfers,
  cross-symbol tails, embedded data and decoding alignment can defeat
  the bounded analysis.

The second source-hash-guarded audit,
`tools/audit_extended_return_targets.py`, decodes independently
from the **exact target** of the 63 reachable branches, checking
limited straight-line return preparation, exact RET epilogues,
one-hop unconditional jumps to return epilogues, and named
function-entry destinations.

| Observed target shape | Branch sites |
| --- | ---: |
| Straight-line setup and return (includes AL-zeroing stubs) | **34** |
| One unconditional jump into a verified shared return epilogue | **10** |
| Branch destination exactly equals another original named function entry | **8** |
| Other entry-reachable code needing complete target CFG analysis | **11** |
| Source branch not established reachable by the bounded walk | **29** |
| **Total** | **92** |

This brings the number of game-origin branches with **recognizable
entry/return target structure** to 158 + 34 + 10 + 8 = **210 out of
250**. This **is not 210 proven equivalent functions**; in particular
the original Watcom stack/register state must still be verified when
sharing exits between routines.

**Reproducible metadata:**

- `decompilation/reports/entry_reachability_2026-10-13.json`
- `decompilation/reports/extended_return_targets_2026-10-13.json`

The 11 entry-reachable nontrivial targets are:
`Ship_Strength_Vs_Shield_`,
`Draw_Special_Systems_Replacement_Box_`,
`Fleet_Box_Data_`, `Ship_Owner_`, `Draw_Relocation_Links_`,
`Officer_Cost_`, `Remap_Draw_Ship_Seg_N_Centered_`,
`Pop_State_String_`, `Draw_Colony_Info_Production_For_`,
`Do_Net_Combat_Update_`, and `Get_Tech_Cost_`.

The 29 not established by the bounded walk must be re-entered from
source and caller references before treating them as real branch
sites. This matters especially for entries that linear `objdump`
misreads as conditional opcodes in interleaved code/data.

### Exact branch and target reconstruction: ship/shield exit cap

In `Ship_Strength_Vs_Shield_` the original code-object branch at
`0x4F22B` tests byte flag `[0x21CB4]`, then conditionally jumps
to `0x4EE13` (inside an earlier provisional symbol interval).
The target instructions show:

- `CMP ESI,0xFA00`, followed by unsigned `JBE`;
- when ESI exceeds `0xFA00`, `MOV ESI,0xFA00`;
- `MOV EAX,ESI; LEAVE; POP EDI; POP ESI; POP ECX; RET`.

Therefore **on this particular taken-branch path**, the result
returned in EAX is the unsigned 32-bit minimum of the incoming ESI
and 64,000. The byte flag's gameplay meaning, the calculation
which supplied ESI, and the correctness of source/target stack
compatibility are **not yet proved**. This is a bounded
instruction-level reconstruction, not a whole-routine port.

## Seven prior entry-decoder failures triaged

Earlier `function_cfg_extents.csv` reported seven
`no_entry_decode` entries because its resynchronized
32-bit instruction export cannot decode all mixed regions or every
synthetic entry. A SHA-guarded local read of the object bytes established:

| Entry | Classification |
| --- | --- |
| `___GETDSEnd_` | 1-byte zero marker |
| `__SegmentStartRR16` | 1-byte zero marker |
| `__IrqDataArrayRR16` | 620-byte zero-filled data array |
| `__SegmentStartPC32` | 1-byte zero marker |
| `__SegmentEndPC32` | 1-byte zero marker |
| `anon_runtime_0012F1D8` | Genuine 8-byte initializer routine, referenced by `__InitRtns` entry at original offset `0x12FF2` and omitted by earlier exporter |
| `__VideoBasePD16` | Eight zero data bytes followed by a **16-bit instruction island** wrongly treated as a single 32-bit entry |

The anonymous runtime routine (original object offset
`0x12F1D8`) contains a WORD store of SS to an absolute data address
followed by RET. This is real code; the original initialization-table
reference gives a concrete control-flow edge.

### Four i8086 subroutines in the mixed video region

Starting at original object offset `0x1583A5` after the eight-byte
data prefix, decoding as `i8086` rather than 32-bit x86 yields four
consecutive procedures with verified `PUSH BP; MOV BP,SP` entry
prologues and exact RET instruction boundaries:

| Entry | RET instruction | Preliminary function meaning |
| --- | --- | --- |
| `0x1583A5` | `0x1583D4` | Position a far video-buffer cursor, computing a 160-byte row stride and 2-byte character-cell column offset |
| `0x1583D5` | `0x1583FB` | Store one character through the far buffer and advance by two bytes |
| `0x1583FC` | `0x15841F` | Iterate NUL-terminated text, calling the character writer |
| `0x158420` | `0x158458` | Format a byte as two hexadecimal ASCII characters using the writer |

The low-level roles follow directly from the decoded instruction
operations and internal calls, but names and calling conventions are
provisional; those routines are not native game-rule equivalents.
A 32-bit decoder must not be used to interpret this 16-bit island.

## Remaining work

This pass **did not finish full-game source recovery**. Next actions:
rebuild the resynchronized control-flow corpus with synthetic function
entries included, separately handle mixed 16/32-bit code, investigate the **11 entry-reachable nontrivial game CFG destinations** and **29 game branch sites not established reachable** (without treating the latter as dead code), verify
shared-tail stack discipline and 61 support-module cases, preserve and expand the
**187 currently verified game switch tables** to full case semantics, and continue reconstructing the real
colony turn, diplomacy, AI, combat, map generation, save/load, and
rendering behavior. The 11 runtime-dependent CALLs require individual
caller/object-initialization provenance; a zero-initialized callback
must not be assigned a fabricated callee.

This checkpoint makes no edits to website gameplay, native game
execution, Xbox controller behavior, or Qwen, and does not distribute
original game binaries or artwork.


## Follow-on recovered combat subsystem: ammunition eligibility

The source-verified original `Is_Ship_Out_Of_Ammo_` (241 bytes)
and `Check_For_Launched_Fighters_` (95 bytes) now have isolated
derived C. Original `Does_Combat_Ship_Have_Special_` (75 bytes)
and the pure return calculation from `Test_Bit_Field_`
(34 bytes) are included rather than replaced by guesses or stubs.

The six-case original weapon-category switch, signed ammunition
field, eight weapon slots, 300 missile records, dual special
bitfields, and 51 opcode/producer checkpoints are individually
cross-referenced with the authenticated original. Four original
combat initialization functions explicitly assign the 16-bit
global at DATA offset `0x218AC` from the signed owner byte of
a selected original `_ship` record.

- `decompilation/reconstructed/combat_ammo_v131.c`
- `decompilation/annotated/combat_ammo_v131.md`
- `tests/test_combat_ammo_v131.c`
- `tools/audit_combat_ammo_v131.py`
- `decompilation/reports/combat_ammo_audit_v131_2026-10-13.json`

The derived regression suite passes strict C11 and both
AddressSanitizer/UndefinedBehaviorSanitizer. This remains
**source-anchored functional reconstruction, not dynamic
differential validation inside the original DOS executable**;
the original bitfield helper's scratch CODE-object write is
intentionally omitted from pure C, and invalid host indices
are explicitly rejected for safety. No website, Xbox controls,
Qwen, or original game assets were modified by this work.


## Follow-on weapon-state and actual firing-ammunition mutation recovery

A subsequent original-v1.31 source-anchored pass isolated the **entire
124 bytes** of three game-code helper functions:

- `Weapons_Left_` (60 bytes, original CODE `0x26C60`).
  Signed 16-bit numerator/denominator `IDIV` and a
  specific positive-numerator remainder adjustment
- `Weapon_Is_On_` (32 bytes, `0x3584C`);
  compares weapon slot `+0x5A` flag against 1 and sets **AL**
- `Weapon_Is_Off_` (32 bytes, `0x3586C`);
  the complementary `SETNE AL` condition

All three full original function-byte hashes and 26 machine-code
instruction sites are independently verified. The derived C
passed strict C11, ASan and UBSan, including every original
weapon-bank slot and 4,096 status-byte combinations.

The original firing routine `Fire_Ship_` is **2,216 bytes** and
not fully reconstructed. Nevertheless, its **actual post-fire
ammunition state mutations** have now been traced and verified
from original instructions:

- `0x28FB5`: after `Fire_Missile_`, if a local mode WORD
  equals **2**, store the zero-extended byte at
  `_weapons + 28*weapon_id + 13` into the selected
  weapon-slot WORD `+0x58`
- `0x28FC3`: after `Fire_Missile_` in other modes,
  decrement that slot's WORD
- `0x2910C`: after `Fire_Bomb_`,
  decrement that slot's WORD

The two original 16-bit DEC operations have modulo-65536
behavior. Their *normal-game reachability on zero* remains
to be verified. A separate derived C helper reproduces only
these three bounded state writes (not missile/bomb effects),
and its tests passed the full 65,536-value decrement domain,
eight slots and all 256 reload-byte values under ASan/UBSan.

Source and evidence:

- `decompilation/reconstructed/combat_weapon_status_v131.c`
- `decompilation/reconstructed/fire_ship_ammo_mutations_v131.c`
- `decompilation/annotated/combat_weapon_status_v131.md`
- `decompilation/annotated/fire_ship_ammo_mutations_v131.md`
- `tools/audit_combat_weapon_status_v131.py`
- `tools/audit_fire_ship_ammo_mutations_v131.py`
- `decompilation/reports/combat_weapon_status_v131_2026-10-13.json`
- `decompilation/reports/fire_ship_ammo_mutations_v131_2026-10-13.json`

**Next priority:** source-trace `Fire_Ship_` local mode at
`[EBP-0x14]` and the surrounding jump-table cases, then
reconstruct `Fire_Missile_`, `Fire_Bomb_` and their original
calling conventions and side effects. The game is not yet
fully decompiled and no original-game differential execution
has been performed. Original assets remain private; there
are no website, Xbox controller or Qwen changes.


## Fire_Ship category dispatch, bomb calculation, RNG and seed lifecycle

A newer authenticated original-code pass resolved the `Fire_Ship_`
local at `[EBP-0x14]` to the original selected weapon's
**definition category byte at `_weapons+0x0C`**:
`0x28CA4` reads the signed weapon ID, `0x28CA7`
multiplies by the original 28-byte weapon-definition stride,
`0x28CAA` reads the category, and `0x28CB2`
stores it in that local. The original six-case dispatch at
CODE `0x28F62` uses a table at `0x28B46`:

| Category | Original CODE branch | Firing helper |
| ---: | --- | --- |
| 0 | `0x28FD1` | `Fire_Beam_Weapon_` |
| 1 | `0x28F6A` | `Fire_Missile_` |
| 2 | `0x28F6A` | `Fire_Missile_`; subsequent slot `+0x58` counter overwrite |
| 3 | `0x290E2` | `Fire_Bomb_` |
| 4 | `0x28F6A` | `Fire_Missile_` |
| 5 | `0x29113` | `Fire_Special_Weapon_` |

This resolves the previously unknown "mode 2": it is
weapon definition **category 2**, not an independent
mode or an inferred special gameplay term. The
reconstructed router and post-fire mutations passed
2,048 category/slot cases and 6,144 integrated
missile-counter writes under strict C11/ASan/UBSan.

The **entire original 224-byte** `Fire_Bomb_` function
has now been source-body hash verified, with **44 original
instruction anchors**. Its signed damage range calculations,
`_ordnance_bonus` scaling, 0..255 firing-count loop and
32-bit accumulator are translated into standalone C.
Its direct `Apply_Damage_To_Planet_` (775-byte)
callee remains an **explicit external callback**,
not a simulated planet damage engine.

The **entire original 128-byte** Watcom `Random_`
has likewise been source-body hash verified with
**20 machine-instruction anchors**. The original
DWORD global `_random_seed` at DATA offset
`0x41E34` uses the exact update
`seed = seed * 0x41C64E6D + 0x3039` modulo
2^32, rejection sampling with threshold
`(UINT32_MAX / n)*n`, and a return in
**1..n inclusive**. `Random_(0)` raises an
original x86 divide error before its apparent
zero-argument recovery branch could run.
The derived C reports a safe zero-divisor status
instead. It reproduces independently calculated
seed/output fixtures, including a rejection retry.

A further **five full original seed-related functions
totaling 200 bytes** were verified by full-body digests
and **14 original instruction anchors**:

- `Set_Game_Random_Seed_` (28 bytes; checks original
  `_cmd_line_seed`, calls `Check_Release_Version_`
  first, then selects time or explicit command-line seed)
- `Random_With_Restore_` (33 bytes; saves seed,
  draws, restores seed, returns signed low 16 bits)
- `Set_Random_Seed_` (44 bytes)
- `Get_Random_Seed_` (44 bytes)
- `Randomize_` (51 bytes; invokes original
  `time_(NULL)`, then installs its returned seed)

This pass therefore added **552 source-authenticated
complete original function-body bytes** to the
record, alongside the bounded six-category
`Fire_Ship_` branch table (the remaining 2,216-byte
firing routine is **not** fully decompiled).

Original seed-driven `Random_(100)` now feeds
the derived `Fire_Bomb_` loop; integrated tests
reproduce both expected damage under a test-only
planet-effect callback and exact final seed state.
RNG seed initialization and restore behavior have
separate strict-C11/ASan/UBSan regression tests.
These are original-instruction-supported C functions
and host tests, **not** dynamic differential validation
against the DOS executable or a playable full engine.

Source and research artifacts:

- `tools/audit_fire_ship_category_dispatch_v131.py`
- `decompilation/reconstructed/fire_ship_category_dispatch_v131.c`
- `decompilation/annotated/fire_ship_ammo_mutations_v131.md`
- `decompilation/reports/fire_ship_category_dispatch_v131_2026-10-13.json`
- `decompilation/reconstructed/fire_bomb_v131.c`
- `decompilation/annotated/fire_bomb_v131.md`
- `tools/audit_fire_bomb_v131.py`
- `decompilation/reports/fire_bomb_v131_2026-10-13.json`
- `decompilation/reconstructed/random_v131.c` and `.h`
- `decompilation/annotated/random_v131.md`
- `tools/audit_random_v131.py`
- `decompilation/reports/random_v131_2026-10-13.json`
- `decompilation/reconstructed/random_seed_lifecycle_v131.c`
- `decompilation/annotated/random_seed_lifecycle_v131.md`
- `tools/audit_random_seed_lifecycle_v131.py`
- `decompilation/reports/random_seed_lifecycle_v131_2026-10-13.json`

The outstanding combat bottleneck is the full
`Apply_Damage_To_Planet_` routine, followed by
`Fire_Missile_`, `Fire_Beam_Weapon_`,
`Fire_Special_Weapon_`, remaining `Fire_Ship_`
control flow, and original game save/turn systems.
No Game Lab public website, Xbox controls or
Qwen configuration was modified.


## Further original planetary combat recovery: damage, defenses and hit loop

The source-authenticated original MOO2 v1.31 executable provided
three additional planet-combat targets:

1. **`Apply_Damage_To_Planet_` (775 bytes, CODE `0x2A3C3`)**:
   complete original function byte digest verified and **65**
   original instruction checkpoints audited. The biological
   `flags & 0x80` and conventional branches, seven original
   helper calls, and original named combat-state writes are mapped.
   The body as a whole is **not fully reconstructed in C**.
   Two bounded source-equivalent arithmetic expressions now are:
   original special-ID-7 conventional damage
   `trunc_toward_zero(signed16(damage)/4)-1` using
   WORD wraparound, and biological probability reductions
   selected by original defender-player bytes
   `+0x182` and `+0x1D8` (half or quarter,
   first taking precedence). They passed exhaustive
   original WORD-input tests, and the biological
   predicate was integrated with the recovered source
   `Random_(100)` seed sequence.
2. **`Does_Combat_Planet_Have_Defenses_`
   (92 bytes, CODE `0x2A142`)**: entire original
   body digest verified and 20 opcode anchors audited.
   With signed combat colony ID −1 it returns zero;
   otherwise it reads four original `_colony`
   bytes `+0x150`, `+0x151`, `+0x160`,
   `+0x165` from a 361-byte record and
   OR-packs them shifted by 0,1,2,3 bits.
   The lower AX word is established; the original
   code does not necessarily zero the upper half
   of EAX because it updates SI/CX/DX/AX halves.
   The derived C normalizes the high word for safe
   host callers, while the original planet-damage
   caller tests AX. It passed 66,560 packed-value tests.
3. **`Apply_Bomb_Hits_` (95 bytes, CODE `0xCD2F2`)**:
   complete original body verified with 40 instruction
   checks and a separate checksum on its actual
   7-byte shared epilogue at CODE `0xCCDA5`.
   The exit is a valid cross-function jump inside the
   `Handle_Leader_At_Lost_Colony_` symbol interval,
   which explains why the legacy 95-byte linear CFG
   appeared to lack a RET. Its ordinary and biological
   hit-processing loop is now standalone derived C
   with explicit `Resolve_Bomb_Hit_` and
   `Resolve_Biological_Hit_` callbacks. Regression
   covers original callback order, hit counters,
   32-bit accumulated hit value, zero-progress and
   shared-return cases.

The current source/authenticated artifacts are:

- `tools/audit_apply_damage_to_planet_v131.py`
- `decompilation/reports/apply_damage_to_planet_v131_2026-10-13.json`
- `decompilation/annotated/apply_damage_to_planet_v131.md`
- `decompilation/reconstructed/planet_special7_damage_v131.c`
- `decompilation/reconstructed/planet_bio_threshold_v131.c`
- `tests/test_planet_special7_damage_v131.c`
- `tests/test_planet_bio_threshold_v131.c`
- `tests/test_planet_bio_random_integration_v131.c`
- `tools/audit_combat_planet_defenses_v131.py`
- `decompilation/reports/combat_planet_defenses_v131_2026-10-13.json`
- `decompilation/reconstructed/combat_planet_defenses_v131.c`
- `tests/test_combat_planet_defenses_v131.c`
- `tools/audit_apply_bomb_hits_v131.py`
- `decompilation/reports/apply_bomb_hits_v131_2026-10-13.json`
- `decompilation/reconstructed/apply_bomb_hits_v131.c`
- `tests/test_apply_bomb_hits_v131.c`
- `decompilation/annotated/apply_bomb_hits_v131.md`

Next source reconstruction boundary is original
`Resolve_Bomb_Hit_` (641 bytes),
`Resolve_Biological_Hit_` (436 bytes),
and `Destroy_Colony_Defense_` (549 bytes).
The original planet-damage, bomb effects and
combat subsystem remain incompletely decompiled;
the reconstructed C has not been differentially
run against the original DOS game. Safe host
input checks and iteration caps are deliberate
non-DOS differences. Original proprietary assets
stay private, and the public Game Lab/Xbox/Qwen
deployments were not modified.


## Hit-resolver original-code coverage and weighted targeting

The next original-source pass authenticated **both complete named
hit-resolver function bodies** in the original v1.31 executable:

| Original CODE body | Original offset | Bytes | Status |
| --- | --- | ---: | --- |
| `Resolve_Bomb_Hit_` | `0xCCEBD` | 641 | Entire original source-byte hash verified; target selection reconstructed |
| `Resolve_Biological_Hit_` | `0xCD13E` | 436 | Entire original source-byte hash verified; reverse reservoir selection reconstructed |
| **Combined source-verified bytes** | | **1,077** | **Not yet full side-effect-equivalent C** |

`tools/audit_colony_hit_resolvers_v131.py`
confirmed both original CODE-body SHA-256 digests and
**68 original opcode/call/branch sites**. An absent-target
biological resolver branch at CODE `0xCD185`
jumps to a six-byte external Watcom epilogue at
`0xCCEB7`, within the original `Destroy_Colony_`
named symbol interval. The source prologue and
external epilogue agree on preserved-register order.
This is another genuine original cross-function CFG
edge, not a function-boundary disassembly error.

The isolated derived source
`decompilation/reconstructed/colony_hit_target_selection_v131.c`
reconstructs two major original selection subgraphs:

- Biological resolver scans original colony entries
  at `+0x0C+4*i` in reverse order,
  excluding source DWORD low-nibble value **8**.
  For each eligible entry it increments a running
  count and chooses the index if the actual original
  `Random_(eligible_count)` return equals 1.
  This is reverse-order **reservoir sampling**
  with original-state LCG/rejection sampling.
- Ordinary bomb resolver scans colony byte fields
  `+0x136+i` for i=48..0, collecting positions
  whose byte is nonzero and whose index is not
  in the original hard-coded exclusion set
  **{8, 9, 26, 27, 40, 41, 42, 47}**.
  It then builds original target-group weights from
  eligible positions, signed colony WORDs `+0x130`
  and `+0x132`, a nonzero WORD `+0x125`
  treated as one slot, and colony byte `+0x0A`
  **unless that byte equals exactly 1**.
  The weighted selector uses the original
  `Random_(total_weight)-1` zero-based draw,
  splitting five source target groups. When
  colony byte `+0x0A==1` and other weights total
  zero, a special single-entry path bypasses RNG.

Separate derived tests cover **1,280 seeded biological
reservoir fixtures**, the complete 49-slot
ordinary target filter, and **4,096 seeded
weighted-selection cases**. Both passed strict
C11, AddressSanitizer and UndefinedBehaviorSanitizer.
Their independent expected RNG states and output
categories were compared to the reconstructed
original RNG state.

New authoritative artifacts:

- `tools/audit_colony_hit_resolvers_v131.py`
- `decompilation/reports/colony_hit_resolvers_v131_2026-10-13.json`
- `decompilation/reconstructed/colony_hit_target_selection_v131.c`
- `tests/test_colony_hit_target_selection_v131.c`
- `tests/test_bomb_weighted_target_v131.c`
- `decompilation/annotated/colony_hit_resolvers_v131.md`

The ordinary and biological resolvers' **game-state
effects remain incomplete**: population removal,
player statistics and traits, special defense
status, colony building destruction, and result-event
updates. The host selection helpers intentionally
do not mutate the underlying colony or result-event
structures, except that the supplied original RNG
seed is advanced. Their input guards and explicit
no-target result are safety-focused differences
from the DOS executable. The next decompilation
pass must trace and reimplement those original
mutations, then remove the `Apply_Bomb_Hits_`
resolver callbacks only after end-to-end validation.

Original game binary/media remains private.
No Game Lab public web, Xbox controller, or
Qwen configuration was changed.


## Follow-on: bounded bomb/biological population, event and owner-stat writes

Original source verification for `Resolve_Bomb_Hit_` (641 bytes)
and `Resolve_Biological_Hit_` (436 bytes) now includes **96**
independent original opcode sites, including 28 additional
population-removal and player-stat mutation instructions,
alongside the authenticated entire-function hashes and
shared Watcom return bytes.

Branch-selected original writes recovered in isolated C:

- Colony population WORD +0x130 or +0x132 decremented,
  corresponding event WORD +0x08 or +0x0A incremented,
  and event BYTE +0x41 marked when the original branch
  requires it
- Original colony WORD +0x125 transferred to event
  WORD +0x43 before being zeroed
- Biological population death increments event WORDs
  +0x0C and +0x3F, decrements colony entry-count BYTE
  +0x0A, then replaces the chosen DWORD entry with
  the last population-entry DWORD
- Original signed defense WORD >100 at
  colony +0xB4+2*index is decremented by 100
- Original player-stat counters at
  `player_base + sign_extend(colony[0])*0xEA9 +
  0x6FF + 2*sign_extend(event[0])` are changed by
  original WORD increment 1 or add 10 depending on
  the selected source branch

The implementation is deliberately limited to **already-selected
source mutation paths**. It does not itself implement branch
selection, all missing colony/building/population/player effects,
or original DOS dynamic execution. Bounds guards and statuses
are modern host safety changes; DWORD/WORD update semantics
preserve the observed original integer widths.

New committed files:

- `decompilation/reconstructed/colony_hit_mutations_v131.c`
- `decompilation/reconstructed/colony_hit_player_stats_v131.c`
- `tests/test_colony_hit_mutations_v131.c`
- `tests/test_colony_hit_player_stats_v131.c`
- `tests/test_apply_bomb_hits_colony_mutation_integration_v131.c`
- Updated `tools/audit_colony_hit_resolvers_v131.py`
- Updated `decompilation/reports/colony_hit_resolvers_v131_2026-10-13.json`
- Updated `decompilation/annotated/colony_hit_resolvers_v131.md`

All three test programs were downloaded at their committed
GitHub revision and executed successfully on the original-source
decompilation computer under strict C11, AddressSanitizer and
UndefinedBehaviorSanitizer. The expanded original-body audit
also passed all **96** opcode checkpoints.

**Remaining:** connect original resolver branch predicates with
the reconstructed source effects, reconstruct building destruction,
defense-clearing, and all player/global mutations. Full-game
decompilation remains incomplete. No Game Lab, Xbox, Qwen,
or original game media changes were made.
