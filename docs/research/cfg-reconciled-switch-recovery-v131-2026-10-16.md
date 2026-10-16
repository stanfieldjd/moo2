# Recovering v1.31 switch-dispatch paths across the whole original executable

## Why this matters

The previous whole-executable control-flow repair fixed GNU objdump's split x86 machine-instruction rows and raised **CFG instruction-membership records to 367,349**. However, its traversal still consumed only the legacy `decompilation/switch_targets.csv` index of **135 switch sites / 1,080 case targets**. Independent source audits from October 13 already authenticated **68 more game-module indexed CS dispatches** and **two prescaled CS dispatches** (one game and one support). The verified original targets had not been connected to the full CFG.

This checkpoint integrates **all 205 source-authenticated switch sites and 1,625 entries**, without guessing any target or changing the original game executable.

## Original source validation

The original official DOS `ORION2.EXE` v1.31 SHA-256 is `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Extracted original Watcom LE CODE image SHA-256 is `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`.

`tools/merge_verified_switch_targets_v131.py` reads those original files, every table in the legacy `switch_tables.csv` / `switch_targets.csv`, each of 68 additional reported game CS SIB tables, and both prescaled dispatch tables. For **every one of the 1,625 table entries**, it re-reads the original four CODE bytes, checks the claimed target, refuses out-of-image destinations, detects duplicate sites and case indices, and preserves precise per-site provenance in `decompilation/switch_targets_reconciled.json`. The output `decompilation/switch_targets_reconciled.csv` is the cumulative case-target source for the CFG.

The earlier individual original source reports remain unchanged:
- `decompilation/reports/omitted_game_switches_v131_2026-10-13.json`
- `decompilation/reports/omitted_prescaled_dispatches_v131_2026-10-13.json`
- `decompilation/switch_tables.csv` and `switch_targets.csv`

The existing `tools/recover_function_cfg_extents.py` was updated to prefer the new checked `switch_targets_reconciled.csv`. When working with older workbenches without the combined file, it falls back to the original legacy inventory. This change is strictly in the analysis instrumentation. The original bytes are unchanged and remain on the authorized source machine.

## Measured before/after improvement

The corrected global CFG was regenerated with the exact same 5,635 function entries and full CODE image.

| Metric | Previous corrected CFG | With reconciled switches |
|---|---:|---:|
| Original switch sites included | 135 | **205** |
| Original table case entries | 1,080 | **1,625** |
| CFG instruction membership records | 367,349 | **372,703** |
| Functions whose conservative maximum reached provisional boundary | 4,879 | **4,882** |
| Functions stopping before provisional boundary | 708 | **705** |
| Unresolved CFG edges encountered | 425 | **446** |

**5,354 more CFG membership records** became recoverable (a further **1.46% relative to the prior CFG membership count**, *not* 1.46% of whole game completion). **54 function entries gained** reachable instruction memberships, and **none lost** them. The biggest verified changes include:

| Function | Newly recovered memberships |
|---|---:|
| `Auto_Design_Ship_` | +1,011 |
| `Assign_Empire_Building_` | +699 |
| `Get_Diplomacy_Statement_` | +414 |
| `Setup_Next_Event_` | +371 |
| `Get_Event_Message_` | +262 |
| `Draw_Shield_Arcs_` | +223 |
| `Insert_Item_` | +189 |
| `Diplomacy_Demand_` | +166 |

The increase from 425 to 446 unresolved edges is **not a loss of recovered instructions**. The newly accessible case arms expose additional, previously unseen source branches that require further work. It would be misleading to claim the unresolved-edge count necessarily falls whenever the disassembler becomes more complete.

Under the current conservative CFG, **63 of the 70 additionally verified dispatch instructions are reachable**. The other seven are known and source-authenticated but remain unreachable by this entry/branch traversal. They occur within `Get_Net_Diplomacy_Choices_` (three sites), `Determine_Event_`, `Do_Combat_Turn_`, `Assign_Combat_Grids_`, and `Farload_Library_Data_`.

## Reproducibility, caveats and next actions

`tools/audit_cfg_reconciled_switch_recovery_v131.py` reloads original code and EXE SHA fingerprints, revalidates **every original jump-table entry** from the three source provenances, checks the generated CSV row for row, compares every function to immutable Git baseline `5d6c4d9757bfc97229eb8c4b5ac3395815b64744`, checks the CFG's new manifest, verifies the numeric gains and rejects any negative per-function instruction-membership change. Structured evidence is `decompilation/reports/cfg_reconciled_switch_recovery_v131_2026-10-16.json`. All reports are original-source-derived; no game executable or proprietary assets are included.

The remaining high-leverage work is explaining the seven switch sites still unreachable under conservative control flow, and tracing the 446 newly visible unresolved edges in combat, diplomacy and AI with correct original byte boundaries. Some ambiguous CODE intervals are inline data or shared tails, not executable control flow. **Neither the old 87% estimate nor the later 88% figure was a verified percentage of complete semantic decompilation.** CFG memberships are not unique bytes, original game runtime behavior, or browser-playable native gameplay. This checkpoint does not alter the website, original DOS files, or Xbox-controller code.
