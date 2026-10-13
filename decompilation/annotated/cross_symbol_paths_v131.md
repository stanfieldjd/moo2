# Original v1.31: eleven structurally traced cross-symbol control paths

**Scope:** bounded control-flow and small-function decompilation from
the verified official v1.31 `ORION2.EXE`, SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

**Method:** The source branch instruction is proven reachable from
its original Watcom CODE symbol entry by
`tools/audit_entry_reachability.py`. The destination was independently
re-decoded at its exact address from original LE CODE bytes, and direct
call/jump targets cross-referenced with Watcom CODE names. For data
addressing, the original raw instruction operand is **LE relocated**
before interpreting which DATA object contains referenced values.
Branch-path reconstruction does **not** imply the entire source
function has been reproduced, that all stack frames are compatible,
or that the paths have been executed in the original DOS game.

These eleven cases belong to the earlier 11
`reachable_nontrivial_cfg_target` class. Seven have short bounded operation sequences; the remaining four
now have explicitly verified return-route graphs but require further
source-level semantic and calling-convention reconstruction.

## 1. `Ship_Strength_Vs_Shield_`: capped return

- Source conditional branch: `0x4F22B` (`JNE 0x4EE13`),
  after comparing relocated data byte `0x21CB4` to zero.
- Target: `0x4EE13` within the provisional
  `Satelite_Strength_Vs_Ships_` symbol interval.
- On the taken branch, the target compares **unsigned**
  `ESI` with `0xFA00` (64,000), clamps if greater, moves
  the result to `EAX`, restores the frame and returns.
- Bounded C-like observation: `return ESI > 64000U ? 64000U : ESI;`.
  This is the specific branch's result, not the complete
  ship-strength algorithm.

## 2. `Remap_Draw_Ship_Seg_N_Centered_`: shared draw-and-return

- Source `0xAABC3`: `JE 0xAAB8C` after signed-size
  `CMP BX, [DATA+0xAC1D]`. When this comparison matches,
  the target loads `EDX = sign_extend_i16([EBP-0x2C])`,
  `EAX = sign_extend_i16([EBP-0x28])`, and
  `EBX = [DATA+0x277C0]).
- Calls named `Draw_Centered_` at `0xB5CFF` then
  executes `LEAVE; POP EDI; POP ESI; POP ECX; RET`.
- Untaken path continues further rendering and object handling;
  it is not covered by this case.

## 3. `Pop_State_String_`: original control collapsed to two cases

- Original function starts at `0xAB147`. Inputs include
  `AX` (unsigned comparison to 2).
- If **AX is exactly zero**, code at `0xAB160` loads
  `EAX=0x11E` and tail-jumps to `E_Strings_` at `0xBDF5C`.
- For **all nonzero 16-bit AX inputs**, the branch chain
  reaches `0xAB12F`, loads `EAX=0x0C`, and tail-jumps
  to the same `E_Strings_`.
- `E_Strings_` sign-extends AX, indexes a DWORD
  pointer table with scale 4 and returns the selected pointer
  in EAX. Its relocated DATA object pointer must be resolved
  separately before dereferencing.
- C-like control selection only:
  `uint16_t string_index = (ax == 0) ? 0x11E : 0x0C;`.
  The meanings of the referenced strings remain to be checked
  against original labels/assets.

## 4. `Draw_Colony_Info_Production_For_`: shared production drawer

- Source `0xACE84`: `JNE 0xACE2D` after `CMP EAX,3`.
  The routine had already pushed EBX, ECX, EDX.
- If `EAX != 3`, target `0xACE2D` sets
  `ECX=-1`, `EDX=EAX*30`, and falls through to
  the common drawing call at `0xACE37`.
- If `EAX == 3`, branch is not taken; source sets
  `EDX=-1`, `ECX=-3` then jumps directly to the
  same common setup at `0xACE34`.
- Both paths reach `PUSH 20`, `PUSH 301`,
  `EBX=128`, `CALL Draw_Colony_Prod_` (`0xA55A3`),
  restore EBX/ECX/EDX, and `RET` at `0xACE5D`.
- The computed coordinate passed in `ECX` is signed
  low-16-bit `30*EAX+64` for EAX != 3, or **61** for EAX == 3.
  The original Watcom register/stack call protocol and screen
  coordinate interpretation require separate verification.
  This is not a reconstruction of complete colony production.

## 5. `Do_Net_Combat_Update_`: early shared return

- Source at `0xDAAAA` first calls `Mox_Update_`.
- Next at `0xDAAAF` compares a relocated global byte
  `[DATA+0xB579]` to zero. If **nonzero**, branch at
  `0xDAAB6` jumps to `0xDA8BE` in the earlier provisional
  `Client_Combat_Loop_` symbol interval.
- Target `0xDA8BE` calls `Mox_Update_` **again**, then
  executes `LEAVE; POP EDI; POP ESI; POP EDX; POP ECX;
  POP EBX; RET`.
- Thus the early return path makes two total `Mox_Update_`
  calls before returning. The zero branch instead proceeds
  through the full network combat update, which remains
  unreconstructed.

## 6. `Get_Tech_Cost_`: complete small dispatcher and cost core

A separate machine-instruction-aligned function-level
translation has now been committed as:

- `decompilation/annotated/research_cost_v131.md`
- `decompilation/reconstructed/research_cost_v131.c`

`Get_Tech_Cost_` at `0xFF93B` checks whether input
`DX==0x2000`. It either maps `AX` through a 13-byte-stride
lookup in original LE DATA object 2, or directly uses AX as
technology ID, then computes the player record address with
`0xEA9` stride and tail-jumps into `Player_Research_Cost_`
(`0xD1E96`). The latter reads a **23-byte-stride**
technology table in original DATA object 2; on positive IDs it
loads the base 32-bit cost, and when ID >= 75 adds
`10000 * player_record[0x1D1+ID]`. Negative/nonpositive IDs
return zero.

**Critical correction:** relocating CODE pointers identifies
DATA offset `0x5916` (relocated address `0x175916`) for
the cost table and DATA offset `0x607F` (relocated address
`0x17607F`) for special mapping. Interpreting those offsets as
CODE bytes produces erroneous prices and is not valid source
recovery. Exact values and remaining uncertainty are recorded
in the research-cost dossier.

## 7. `Draw_Relocation_Links_`: restore-and-return

- Source branch at `0x7535D`: original `JE 0x73CF6`
  following `CMP BYTE PTR [DATA+0x21BE4],0`.
- The taken path jumps into the shared cleanup area of the
  `Draw_Black_Holes_` provisional symbol interval.
- Verified instructions at `0x73CF6` sign-extend
  `WORD PTR [EBP-0x8]` into EAX and call
  `Restore_Window_Status_` at `0x7FD56`.
- The following instructions execute
  `LEAVE; POP EDI; POP ESI; POP EDX; POP ECX; POP EBX; RET`.
- This establishes the exact taken-branch call sequence,
  not the full rendering or caller-specific stack-frame
  compatibility.

## 8–11. Remaining branch target subgraphs: original return routes established

The SHA-guarded `tools/audit_four_shared_target_paths.py`
re-disassembled the exact source branch and independently traversed each
observed destination inside tightly bounded named CODE-symbol intervals,
with explicit only-when-needed shared tail allowances. It checked all
branch targets and return instructions against original LE bytes.
Direct CALLs were modeled as fall-through; **callee effects and
stack-frame correctness are not yet verified**. The machine-readable
record is
`decompilation/reports/four_target_paths_2026-10-13.json`.

| Source branch | Target instructions reached | Return path |
| --- | ---: | --- |
| `Draw_Special_Systems_Replacement_Box_` `0x558FB → 0x5583A` | 13 | Calls `Play_Streaming_Music_` at `0x14677`, jumps to `0x56268` (`LEAVE`) and then `0x58D37` (`POP*; RET` at `0x58D3C`) |
| `Fleet_Box_Data_` `0x61A57 → 0x610CA` | 43 | Contains 5 direct CALLs (not followed); returns at `0x61197` |
| `Ship_Owner_` `0x68003 → 0x6892D` | 48 | Two return instructions: `0x68982` valid owner and `0x689C6` post-error fallback |
| `Officer_Cost_` `0x87A56 → 0x84807` | 40 | Two direct CALLs (not followed), then shared `0x841B5` epilogue and RET at `0x841BA` |

The **`Ship_Owner_`** subgraph now has a separate detailed
function-level C-like reconstruction at
`decompilation/annotated/ship_owner_v131.md`. It validates signed
indices 0–499 and owner-byte values 0–15, returning the valid owner.
Invalid cases take the original `sprintf_` +
`Exit_With_Message_` path that invokes `exit_(1)`; treating
that as a normal return of zero would misrepresent the original.

The other three bounded graphs still require deeper reconstruction
of their invoked UI, fleet and officer calculations. It would be
incorrect to count them as functionally equivalent C implementations.

## Continuing decompilation scope

All eleven previously nontrivial *reachable branch targets* now have
verified structural return paths, but **complete game behavior is not
reconstructed**. Next work is extracting and validating the remaining
full function bodies, especially officer costs, fleet UI, colony turn,
combat, AI, and game-state persistence. Call-site register/stack state
and unestablished branch-source reachability must also be revisited.

The earlier **29** branch sources not established by bounded
symbol-entry traversal remain independently unresolved; their
mere presence in a linear disassembly is not evidence that
they can actually execute.

No original copyrighted machine-code files, executable, graphics
or binary tables are committed here. No Game Lab website, Xbox
controller or Qwen changes were made.
