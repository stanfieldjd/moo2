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
