# Whole-executable CFG recovery: GNU objdump wrapped-instruction correction

## Scope and original evidence

This checkpoint corrects a **systematic defect in the decompilation pipeline**, rather than reconstructing another isolated colony routine.

The full original MicroProse Master of Orion II DOS v1.31 executable was authenticated by SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. The extracted original Watcom LE CODE image has SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837` and exactly **1,410,709 bytes**. Original executable and CODE image are local-only and not added to the repository.

The previous `tools/recover_function_cfg_extents.py` parser accepted GNU `objdump` lines containing an instruction mnemonic, but **ignored trailing continuation-only lines**. GNU `objdump` often prints a long x86 instruction across two physical text rows, with the remaining instruction bytes on a row that has no mnemonic. Ignoring the second row recorded an incorrectly short machine instruction, so the CFG's fall-through address landed **inside the original machine instruction**. This was incorrectly classified as an unresolvable branch or premature end of the function.

Concrete original source proof: original CODE address `0x32FCE` contains the complete ten-byte instruction `66 C7 04 55 06 12 02 00 00 00` (`MOV WORD PTR [EDX*2+0x21206],0`). GNU `objdump` prints seven bytes on its first line and three bytes on a continuation-only line at `0x32FD5`. The old parser took the instruction length as **7**, erroneously placing the next control-flow step at `0x32FD5`. The corrected parser combines both rows, verifies every byte against the authenticated CODE image, and computes the real next instruction at `0x32FD8`.

## Fully regenerated source inventory, not an invented completion percentage

The corrected parser was run against **all 5,546 original known CODE-entry disassembly intervals**, covering the **5,593 Watcom CODE symbols plus 42 promoted synthetic function entries**, de-duplicated into **5,635 function records**. The regenerated tracked evidence is `decompilation/function_cfg_extents.csv` and `decompilation/function_cfg_extents.json`. The source-byte parser recorded:

| Measured CFG inventory property | Before correction | After correction |
|---|---:|---:|
| Function entries | 5,635 | 5,635 |
| Recovered instruction-membership records | 259,374 | **367,349** |
| Functions whose maximum CFG extent matched provisional boundary | 4,000 | **4,879** |
| Functions with CFG stopping before provisional boundary | 1,599 | **708** |
| Functions extending beyond provisional boundary | 29 | 41 |
| Function-entry decode failures | 7 | 7 |
| Sum of unresolved CFG edges | 2,480 | **425** |

The new source parser reassembled **6,931 wrapped instruction rows totaling 10,646 original machine bytes**, with **zero orphan rows**. It also compares every original instruction and continuation byte to the authenticated CODE image and fails if the CODE SHA-256 differs.

The measured instruction-membership increase is **107,975**, a **41.63% increase in recovered membership records**, affecting **1,595** distinct function records; **zero** function records have a lower reachable-instruction count. These are *CFG membership references*, not unique machine-code bytes, C-level semantics, tested gameplay functions, or a decompilation completion percentage. Shared instruction addresses may belong to multiple function membership records. No new whole-game decompilation percentage is claimed; **the previous 87% was an unmeasured rough estimate**, and the later 88% figure was not independently measured either.

## Large, material function gains

Representative original source-function changes after systematic correction:

| Original game function | Before | After | Gain |
|---|---:|---:|---:|
| `Combat_Draw_View_Ship_` | 35 | 1,800 | +1,765 |
| `Compute_AI_Data_` | 97 | 1,627 | +1,530 |
| `Draw_Field_` | 12 | 1,435 | +1,423 |
| `Build_End_Of_Combat_Message_` | 97 | 1,055 | +958 |
| `Draw_Ship_Status_` | 234 | 1,153 | +919 |
| `Print_Main_Screen_Data_` | 169 | 1,044 | +875 |
| `Strategic_Combat_` | 29 | 694 | +665 |
| `Race_Selection_Screen_` | 17 | 644 | +627 |

This correction directly improves analysis across **combat, AI, rendering, main-screen UI, and race selection**, instead of repeatedly auditing the same economic functions.

## Reproducibility

The original v1.31 binary image is passed to `tools/export_resynchronized_disassembly.py` by a local, ignored `decompilation/code_object_1.bin` reference. The resynchronized original `decompilation/code_object_1_resynced.disasm` and per-instruction `decompilation/function_cfg_membership.csv` are local derived/raw analysis files intentionally excluded from GitHub. The byte-validating whole-executable parser is `tools/recover_function_cfg_extents.py`.

The new cross-version auditor `tools/audit_cfg_continuation_recovery_v131.py` compares the regenerated CSV and manifest against the immutable pre-correction baseline Git commit `5dc3e36806c18123b3afaf80df98aaf438d5ef62`, re-verifies both original EXE and CODE hashes, checks the complete original split instruction, requires all 5,635 records to match by identity, rejects any decrease in per-function reachable instruction counts, and verifies the manifest-level and recomputed membership totals. Its exact reproducible JSON evidence is `decompilation/reports/cfg_continuation_recovery_v131_2026-10-16.json`; top 100 largest function improvements are exported to `decompilation/reports/cfg_continuation_top_gains_v131_2026-10-16.csv`.

## Remaining gaps and next development step

The corrected inventory still has **708** functions whose conservative CFG extent ends before their provisional boundary and **425** unresolved edges. A provisional function boundary is not proof every preceding byte is executable, because the original Watcom CODE object also contains inline dispatch tables, data and shared tails. Prioritize actual control-flow uncertainty and reachable gaming-critical routines rather than equating all these intervals with missing decompilation.

The next systemic pass is to reconcile **indirect dispatch/switch targets** and hard-boundary/shared-tail classification using the newly correct instruction lengths. Specific major functions for attention include `Do_Combat_Turn_` (7,973 source-provisional bytes), `Tactical_Combat_` (5,542 bytes), `Main_Screen_` (5,308 bytes), `Draw_Visible_Fields_Back_` (6,921 bytes), and `Compute_AI_Data_` (6,681 bytes). The explicit priorities are supported by the updated and verified CFG report, not by speculation about exact remaining semantic work.

The native browser gameplay, Xbox controller workflow, dynamic original DOS parity, and complete game-state reconstruction remain unfinished. Original executable, game assets, website and server were not changed in this operation.
