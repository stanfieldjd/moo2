# v1.31 decompilation checkpoint — colony control flow and remaining gaps (2026-10-13)

## Scope and provenance

This is a **decompilation/reverse-engineering** checkpoint, not a game implementation
or a claim of full source-code recovery. Work on site controls, gameplay tests,
and public engine behavior is paused in favor of reconstructing the original.

- Lawfully supplied local original: `ORION2.EXE`; verified SHA-256
  `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
- Watcom CODE symbols and object offsets: `decompilation/functions.csv` and
  `decompilation/symbols.csv`. For this derived analysis image,
  **Ghidra virtual entry = original LE object offset + 0x10000**.
- Ghidra 12.1.4, via REA, examined the bounded **derived relocated population ELF**,
  `population-window-relocated.elf`,
  SHA-256 `36942cf5838cdb36e0fc50cd153f3d190bacf55181782fe15cb4a3fbed970237`.
  This ELF is an analysis surrogate and is not a running game.
- Evidence returned by direct REA `analyze_function`:
  `Pre_Import_Computing_` 198 bytes; `Colony_Specialty_` 84 bytes;
  `Colony_Production_Calculation_` 18 bytes;
  `Colony_Calculation_` 65 bytes;
  `Star_Colony_Calculation_` 128 bytes;
  `All_Colony_Calculations_` 472 bytes;
  `Do_Player_Colony_Post_Production_` 105 bytes;
  `Apply_Production_` 1,979 bytes. Ghidra pseudocode was cross-checked with
  direct assembly calls, not treated as original C.

## Symbol alias correction

The original Watcom table has **two valid CODE names for the same entry**:
`All_Colony_Calculations_` and `Do_Colony_Calculations_`,
both at LE object offset **863025** (preferred Ghidra `0xE2B31`),
with the same 472-byte provisional extent. This is *not* a contradictory
function name or two distinct implementations. Deduplicate by address while
retaining both source symbol aliases.

## Verified direct-call ordering of the colony preprocessing wrapper

`Pre_Import_Computing_`: original object offset **859481**, Ghidra
`0xE1D59`. This table is the order of decoded **direct CALL
instructions**, not a proof that each callee executes fully on every
runtime branch. The caller passes values in Watcom registers, so Ghidra
`__cdecl` argument guesses are unreliable.

| Order | Direct-call target (Ghidra VA) | Original Watcom name |
|---:|---|---|
| 1 | `0x129C70` | `memset_` |
| 2 | `0xDE03E` | `Colony_Food2_Per_Farmer_` |
| 3 | `0xE1CED` | `Colony_Environmental_Stuff_` |
| 4 | `0xDEC95` | `Colony_Industry_Per_Worker_` |
| 5 | `0xDFDC6` | `Colony_Research_Per_Scientist_` |
| 6 | `0xDDB25` | `Colony_Morale_` |
| 7 | `0xDF546` | `Colony_Industry_Maintenance_` |
| 8 | `0xDEE1B` | `Colony_Industry_Production_` |
| 9 | `0xDE664` | `Colony_Food_Production_` |
| 10 | `0xDEB4B` | `Colony_Food_Maintenance_` |
| 11 | `0xDF66F` | `Colony_Replicators_` |
| 12 | `0xDFF74` | `Colony_Research_Production_` |
| 13 | `0xE08F6` | `Colony_Industry_To_Tax_` |
| 14 | `0xE03F1` | `Colony_BC_Production_` |
| 15 | `0xE094F` | `Colony_BC_Maintenance_` |

There is a **non-call data write between 11 and 12**: observed assembly
stores to colony offset `0xF5` after comparing the signed word at
`0xE9` with the upkeep byte at `0xF0`. Exact clamp/overflow semantics
must be verified in assembly before translating to native rules.

These newly reconciled names matter because Ghidra leaves some real
targets as anonymous `func_0x...`, despite their explicit original
Watcom labels.

## Higher-level colony call structure recovered

- **`Colony_Production_Calculation_`** (offset 859780; `0xE1E84`)
  invokes `Pre_Import_Computing_` and then `Pass_Out_Imports_`
  (`0xDF8F0`, original offset 850160). It is an 18-byte
  wrapper, *not* the entire colony calculation implementation.
- **`Colony_Calculation_`** (offset 862832; `0xE2A70`)
  computes a colony-record address with stride `0x169`, conditionally
  invokes those two stages depending on colony byte `+6`, and invokes
  `Update_Player_Stats_` through a race/player-record stride `0xEA9`.
  Passing conventions remain register-dependent.
- **`Star_Colony_Calculation_`** (offset 862897; `0xE2AB1`)
  scans five two-byte star slot entries (descending slot offsets),
  resolves planet and colony records, checks owner/state conditions,
  performs the pre-import and pass-out pair, then updates player stats.
  These are observed iteration/control-flow properties, not a complete
  validated in-game turn model.
- **`All_Colony_Calculations_` / `Do_Colony_Calculations_`**
  (offset 863025; `0xE2B31`) first loops through qualifying colonies
  with stride `0x169` and pre-import accounting; then loops players
  for pass-out accounting; then scans colonies for
  `Colony_Pop_Grows_` and `Colony_Specialty_`; then updates player
  stats; then resets and accumulates additional player counters
  at original-record offsets `0x5E8`, `0x5EA`, and `0x60C`.
  The meaning of all the latter counters must be determined from
  independent callers/readers, not inferred from offsets alone.
- **`Do_Player_Colony_Post_Production_`** (offset 863497;
  `0xE2D09`) calls `Pass_Out_Imports_` before scanning owner-matching
  colonies for growth/specialty handling. The ending uses a
  cross-boundary jump into the already analyzed `Update_Player_Stats_`
  call site; do not misclassify that edge as an independent function.
- **`Apply_Production_`** (offset 866015; `0xE36DF`) is a
  1,979-byte conditional product-completion routine referencing
  product cost, max population, colonist availability, build
  eligibility, and post-apply calculations. The pseudocode reports
  unreachable-block cleanup and many unresolved external callees.
  **Not reconstructed or safe to port as a complete gameplay function**.

## Colony specialty — isolated behavior to verify fully

`Colony_Specialty_` (offset **859679**, `0xE1E1F`) loops over **three
signed 16-bit source counters** beginning at `colony+0xE7`, accumulating
their sum and tracking the highest entry and its zero-based slot index.
Ghidra's observed result stores that index at `colony+0x0B`
if the maximum is greater than half the combined sum; otherwise it stores
`0xFF`. Because Watcom's signed arithmetic, tie behavior, and overflow
are not yet independently characterized, this is a **decompiler
observation**, not a released native rule.

## New full-function byte-level extraction: `Pass_Out_Imports_`

Original CODE offset **850160**, Ghidra preferred virtual address
`0xDF8F0`, provisional size **1,238 bytes**. Independently restarting
`objdump` at the exact recovered entry in the local relocated LE code
object produced **344 decoded x86 instructions** and **52 conditional or
unconditional jumps** within the bounded symbol interval. This is
*disassembly*, not equivalent-C recovery. Five directly decoded CALLs
were observed, in source-address order:

| Call site (Ghidra VA) | Resolved source symbol |
|---|---|
| `0xDF96A` | `Event_Check_Space_Anomaly_` |
| `0xDFD7F` | `Colony_Pop_Grows_` |
| `0xDFD86` | `Colony_Specialty_` |
| `0xDFDB1` | `Colony_Pop_Grows_` |
| `0xDFDBC` | `Colony_Specialty_` |

The conditional paths reaching the two growth/specialty call pairs
have **not yet been reduced to an equivalent native branching model**.
Do not remove either pair or merge their effects based on function
names. The routine references an explicit anomaly checker; its
outcome-dependent behavior needs independent dataflow reconstruction.

## Indirect-call scope narrowed by original Watcom module identity

Cross-referenced each of the **193 indirect CALL** rows in
`decompilation/indirect_transfers.csv` to the module index of its owning
function in `functions.csv` and `modules.csv`. Exactly **19 CALLs**
belong to the 133 core game-code modules (indices 0–132); **174** belong
to remaining support/runtime/toolkit libraries. Among the 19, two are
indexed dispatches in `COLCALC.C`:

- `Colony_Pop_Prod_Produced_` at object offset `0xCDFF0`
- `Colony_Pop_Base_Prod_Produced_` at object offset `0xCE24E`

Both use the same indexed DWORD table at code/data-relative
`0xB55C`, which earlier table extraction already resolved for valid
slots 0, 1 and 2 respectively to
`Colony_Empire_Base_Food2_Produced_`,
`Colony_Empire_Base_Industry_Produced_`, and
`Colony_Empire_Base_Research_Produced_`.
This is a **confirmed cross-reference of existing recovered targets**,
not 2 newly discovered dynamic callbacks. No dynamic index bounds or
behavior outside the three observed populated entries is presumed.

The 137 indirect JMPs are differently distributed: 118 in the 133
game modules and 19 in runtime/other modules. Switch-table
reconstruction and jump-boundary analysis therefore remain a material
**gameplay-first** task even though most indirect CALLs are support code.

## Remaining decompilation work, in priority order

1. **Finish control-flow boundaries.** Current audit:
   5,635 CFG entries (5,593 Watcom CODE symbols + 42 synthetic entries);
   7 entry decode failures; 311 cross-function conditional branches;
   796 apparent shared tails/epilogues. Confirm source-intended
   branch targets and eliminate embedded-data or alias artifacts.
2. **Resolve indirect transfers.** Static inventory: 193 indirect
   CALL sites; 19 statically resolved absolute slots, 70 zero/BSS
   slots, 4 indexed-call sites, 2 true register-call sites, and
   **96 unclassified sites**. Do not guess dynamic callback targets.
   Break these down by subsystem, starting with game rules and saves.
3. **Reconstruct full colony turn semantics.** Resolve
   `Pass_Out_Imports_`, `Colony_Morale_`,
   `Colony_Replicators_`, `Colony_Job_Production_`,
   `Colony_Pop_Grows_`, all three complete production loops,
   end-of-turn state changes, and register-based Watcom calling
   conventions. Verify explicit record owners and anomaly guards.
4. **Finish the rest of the game**, not just colony routines:
   galaxy generation, diplomacy/AI, research, ships, combat, event
   probabilities, win/loss, save/load, and UI state. Document
   per-routine evidence and equivalence before describing any as
   reconstructed.
5. **Keep proprietary source outside public deployment.**
   Original executable, original artwork and large raw textual
   disassembly are local-only; this committed note contains only
   derived metadata and behavior summaries.

The available REA bounded Ghidra window does not certify entire
1.41 MB gameplay code-object decompilation. A separate attempt to
enumerate the full derived ELF in the current tool session failed
internally; this is a tooling limitation, not proof that the target was
fully analyzed or a reason to invent missing routines. The earlier
rough "87%" is not an audited semantic-completion percentage.

No gameplay-code, controller, website or Qwen changes were made in
this decompilation pass.
