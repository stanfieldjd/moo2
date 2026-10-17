# Whole-executable v1.31 control-flow recovery: byte-only objdump rows

## Material parser failure and original source proof

The original Master of Orion II DOS **v1.31** Watcom CODE analyzer had a second systemic parsing defect. An earlier correction recombined GNU `objdump` machine-byte continuation rows, but the parser matched a *mnemonic-containing* row pattern **before** testing whether a row contained **only hex byte tokens**. Rows such as `76247: ff ff` matched as a new instruction with a fabricated mnemonic `ff`; the tool then traversed into a missing address and stopped the source function. The instruction at CODE `0x76240` is actually the original complete **nine-byte** instruction `66 c7 05 ca 19 02 00 ff ff`, whose final two bytes are displayed on the continuation-only line `0x76247`. The proper following executable instruction is at CODE `0x76249`.

The original canonical `ORION2.EXE` SHA-256 is `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`; the extracted Watcom LE CODE image is 1,410,709 bytes with SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. The entire source-byte decoder continues to match each parsed machine byte against that exact original CODE image.

Additional original source examples verified byte-for-byte:

| Original CODE instruction start | True source machine bytes | Byte-only continuation address | False prior mnemonic |
|---|---|---|---|
| `0x76240` | `66 c7 05 ca 19 02 00 ff ff` | `0x76247` | `ff` |
| `0x379A9` | `66 c7 05 f4 18 02 00 fe ff` | `0x379B0` | `ff` |
| `0x3317B` | `66 c7 04 45 6c a9 01 00 f6 ff` | `0x33182` | `ff` |
| `0xDFB9` | `66 c7 05 96 21 02 00 ff ff` | `0xDFC0` | `ff` |
| `0xE045` | `66 c7 05 96 21 02 00 ff ff` | `0xE04C` | `ff` |
| `0x36CE3` | `66 c7 84 4e a8 49 01 00 ff ff` | `0x36CEA` | `ff` |
| `0xC4817` | `66 c7 85 64 ff ff ff ff ff` | `0xC481E` | `ff` |

The fix in `tools/recover_function_cfg_extents.py` gives the **entire-byte-row anchored pattern** priority over the mnemonic pattern. This prevents byte fragments from being misread as new instructions and permits the original whole-function CFG traversal to continue from authentic source instruction endings. This is a parser correction, not a change to the source executable or any gameplay algorithm.

## Measured before / after on the full original CODE inventory

The source-audited full CFG was regenerated for all **5,635** original Watcom/synthetic function records, retaining the **205 original-byte-verified indirect switch sites and 1,625 table cases** from the previous GitHub checkpoint `8998afc20a4d3bae68cd81f26cf03f6a61209445`.

| Measured original-source CFG property | Baseline | Corrected |
|---|---:|---:|
| Recombined byte-only continuation rows | 6,931 | **7,722** |
| Recombined continuation machine bytes | 10,646 | **12,398** |
| Phantom/disassembled instruction-entry records | 408,409 | **407,618** |
| CFG instruction-membership records | 372,703 | **395,671** |
| Functions reaching their provisional next-entry boundary | 4,882 | **5,033** |
| Functions stopping before provisional next-entry boundary | 705 | **553** |
| Unresolved CFG edges observed | 446 | **45** |
| Unmatched source continuation rows | 0 | **0** |

Exactly **791 more byte-only continuation rows** were properly merged, and **791 corresponding false instruction-start records were removed**. New recovered CFG instruction memberships: **+23,039**, while **71 obsolete old memberships** were dropped, for a **net increase of 22,968**. Across the same unchanged 5,635 entries, 226 function records increased; 49 decreased slightly (by an aggregate of 71), consistent with removal of incorrect byte-fragment instructions. Reporting those reductions is essential; the new parser changes the definition of a valid decoded source instruction, not simply the quantity.

Major actual source-function recovered memberships:

| Original v1.31 function | Additional CFG instruction memberships | Reached provisional end? |
|---|---:|---|
| `Do_Combat_Turn_` | +1,649 | Yes |
| `Interpret_Mouse_Input_` | +1,534 | Yes |
| `Tactical_Combat_` | +1,200 | Yes |
| `Main_Screen_` | +1,112 | Yes |
| `Beam_SFX_` | +878 | Yes |
| `Get_Net_Diplomacy_Choices_` | +644 | Yes |
| `Fleet_Screen_` | +617 | Yes |
| `Officers_Screen_` | +611 | Yes |

The parser also reaches **six of the previous seven original-byte-verified indexed switch dispatch sites** that were inaccessible in the conservative CFG: `0xE198`, `0xE3C1`, `0xEBB7`, `0x12836`, `0x3352D`, and `0x36D9F`. The seventh (`0x117190` inside `Farload_Library_Data_`) remains unreachable because a source CODE inline switch table at `0x117145` disturbs the disassembly alignment after the table. Its direct original branch target `0x117155` is a legitimate instruction boundary but is not a recognized original resynchronized-disassembly entry in the current pipeline. **Do not invent a case target or mark the underlying function fully recovered** until a separately authenticated resynchronization pass resolves it.

## Reproducibility and next work

The audit `tools/audit_byte_only_continuations_v131.py` checks both canonical original binary hashes, seven precisely enumerated original machine instruction-and-continuation examples in the original text export, all function identifier pairs against immutable source Git commit `8998afc20a4d3bae68cd81f26cf03f6a61209445`, both complete CFG manifests, exact membership sums, gains and losses, additional six source-verified dispatch site reachability, and 45 remaining CFG unresolved edges. Structured evidence: `decompilation/reports/byte_only_continuation_recovery_v131_2026-10-16.json`. Regenerated `decompilation/function_cfg_extents.csv` and `decompilation/function_cfg_extents.json` contain the authoritative new code-boundary counts.

**Measurement warning:** these are per-function original x86 CFG instruction memberships. They are not unique machine-code bytes, proved gameplay semantics, compilable reconstructed C/C++, dynamic original DOS parity, or percentage completion of browser-playable Game Lab. The previous 87% / 88% informal completion claims remain unsupported; this work does not replace them with a guessed number.

The next program-wide priorities are the **45 remaining unresolved control-flow edges**, the explicitly source-proved inline switch-table resynchronization at `0x117155` and dispatch `0x117190`, and rebuilding actual executable gameplay functionality for the browser and Xbox-controller targets. Original game binary, art, server, and live website were unchanged by this work.
