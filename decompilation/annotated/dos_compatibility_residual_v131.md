# MOO2 DOS v1.31: source-verified DOS/4GW compatibility and CODE-vs-data triage

## Machine source identity and platform distinction

Canonical original game ORION2.EXE SHA-256: `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
Watcom LE CODE SHA-256: `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837` (1,410,709 bytes).

The original executable starts with DOS MZ signature and contains literal `DOS/4GW` and `DOS4GW` runtime identifiers. The original Watcom LE CODE objects and separately original-byte-verified 16-bit real-mode interrupt/video routines establish a **DOS extended protected-mode executable with real-mode support**. Windows 95's backward compatibility can host DOS programs, but does **not** imply that the game's Watcom protected-mode CODE is native Windows 95 PE/NE executable code.

This report contains original DOS-source findings; it does not claim a Windows-95 runtime test or infer source code from the Windows file format.

## Source climate calculation reads: a real embedded CODE lookup table

Watcom CODE source label `_climate_maintenance_modifiers` begins at CODE `0xCD4BA`. It has an original provisional 67-byte extent and original source symbol kind **4** (not kind 5). Four **independent, exact machine-byte-verified instructions** use indexed reads of a BYTE array at this source address:

| Original CODE read site | Exact original bytes | Source operation |
|---|---|---|
| `0xC2958` | `0F B6 80 BA D4 0C 00` | MOVZX EAX,BYTE PTR [EAX+0xCD4BA] |
| `0xC2EBC` | `0F B6 80 BA D4 0C 00` | MOVZX EAX,BYTE PTR [EAX+0xCD4BA] |
| `0xD09D7` | `0F B6 89 BA D4 0C 00` | MOVZX ECX,BYTE PTR [ECX+0xCD4BA] |
| `0xD545F` | `66 0F B6 80 BA D4 0C 00` | MOVZX AX,BYTE PTR [EAX+0xCD4BA] |

These establish actual original byte-indexed data access; treating its first bytes as i386 branch opcodes is incorrect. Source code around these sites performs production/maintenance arithmetic on the indexed values. **Legal index bounds and whether every byte of the 67-byte provisional interval is data are not independently proven.** The full interval is not unconditionally excluded from the canonical CFG.

## Genuine Watcom `GETDS` boundary, not one more failed executable routine

The original Watcom code at `0x1001E4` consists of `66 2E 8E 1D ED 01 10 00 C3`: it restores DS from the original CS-addressed selector word and RETs at `0x1001EC`. Two zero bytes at `0x1001ED..0x1001EE` are original selector storage; original `___GETDSEnd_` at CODE `0x1001EF` is a source linker-style end marker with one zero byte.

A separate original routine at `0x143E5C` has these exact original machine instructions:

- `BA EF 01 10 00`: MOV EDX,0x1001EF (address of `___GETDSEnd_`)
- `B8 E4 01 10 00`: MOV EAX,0x1001E4 (address of `__GETDS`)
- `81 EA E4 01 10 00`: SUB EDX,0x1001E4

This computes **11**, the original source span between the helper's entry and its end marker. The end marker is demonstrably used as **an address**, not as an executed function entry. No inferred code has been added at the marker.

## Other original Watcom CODE storage and real-mode boundaries

The full original `_netLobby` symbol at CODE `0x128F31` contains exactly the ten literal source bytes `4D 4F 4F 32 EC 00 00 00 00 00` (the ASCII tag `MOO2` plus six bytes). Exact original source `MOV EDX,0x128F31` appears at `0x128F9C` and `0x128FBD`; `MOV EAX,0x128F31` appears at `0x12950C`. Three original code references independently identify this address as an embedded signature or data pointer, not an i386 conditional branch.

Original CODE-symbol kind **5** marks `_Alphabet`, `_max_planet_flags`, and `_flag_replacement_colors` as non-function data labels inside Watcom CODE. The alphabet has additional independent proof: it is the NUL-terminated radix string `0123456789abcdefghijklmnopqrstuvwxyz`, read via original `CS:[EDX+0x134942]` at CODE `0x13498F`.

The source `__IrqDataArrayRR16` is 620 zero bytes; `__SegmentStartRR16`, `__SegmentEndRR16`, `__SegmentStartPC32`, and `__SegmentEndPC32` are fully source-confirmed zero-filled marker intervals. Their actual relocation/usage semantics are not presumed from zeros alone. `__GreenleafFastRealIsr` and `__RealDispatcherRR16` were previously verified with **81 complete original 16-bit instructions**; the PD16 video support region was independently verified with another **104 original 16-bit instructions**, including its source eight-byte zero storage prefix. The separate mode-specific audits are reused and revalidated.

## Last unproven synthetic function entry

At source CODE `0x12F1D8` the original exact eight machine bytes are `66 8C 15 34 CA 00 00 C3`. Independent 32-bit x86 decoding from this exact address gives two coherent instructions:

```
0x12F1D8: data16 mov WORD PTR ds:0xca34,ss
0x12F1DF: ret
```

It could store the SS selector at source memory `DS:0xCA34`, then return. However, the name `anon_runtime_0012F1D8` is a **synthetic** source-reconstruction entry and no authoritative original Watcom symbol or direct caller has yet established the intended entry boundary. Decodability alone does not prove executable entry or behavior, so it remains *unproven*.

## Conservative accounting and reproducibility

The unchanged global 32-bit-only analyzer reports **396,305 original CFG instruction memberships, 20 apparent unresolved edges across 15 entries**. This audited *overlay* supplies source-grounded data, runtime, or original CPU-mode explanations for **19** of those apparent edges. The last one is the unproven synthetic entry described above. **The baseline is not rewritten to claim only one actual unresolved executable edge.** No verified evidence supports a whole-game semantic decompilation percentage.

Reproducible auditor: `tools/audit_dos_compatibility_residual_v131.py`. Original-code instruction and marker checks, full original file fingerprints, separately validated real-mode bodies, code-vs-data source labels and all 15 original residual names/counts are asserted. Machine report: `decompilation/reports/dos_compatibility_residual_v131_2026-10-16.json`.

Next steps: find authoritative LE relocation/caller provenance of the eight-byte synthetic leaf, audit legal climate table indexing, and progress from byte-correct control flow to tested original DOS behavior and native browser gameplay. No original proprietary DOS binary/art, deployed server or Game Lab page was changed.
