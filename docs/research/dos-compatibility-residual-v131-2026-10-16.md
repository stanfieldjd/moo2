# MOO2 v1.31: DOS compatibility and mixed-mode code provenance

Canonical original DOS EXE SHA-256: `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Original Watcom CODE SHA-256: `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`.

The original file begins with DOS MZ and contains DOS/4GW and DOS4GW extender signatures. Windows 95 could run DOS programs, but the original protected-mode Watcom CODE should not be misidentified as a native Windows program.

Original source byte checks establish four independent byte-indexed loads from the climate modifier table at CODE 0xCD4BA, three address/size calculations involving Watcom __GETDS (0x1001E4) and ___GETDSEnd_ (0x1001EF), and three address references to the embedded MOO2 signature at 0x128F31. Watcom kind-5 CODE labels, five exact zero-filled runtime storage/marker intervals, and separate complete 16-bit code bodies were also authenticated.

Of 20 apparent unresolved edges in the unchanged i386-only CFG, 19 have source-backed type, storage, mode or boundary explanations. The remaining synthetic address at CODE 0x12F1D8 yields a valid two-instruction SS-selector-store and RET on decoding, but no separately proven Watcom entry/caller. The full i386 CFG still reports 396,305 instruction memberships and 20 raw unresolved edges. No verified whole-game semantic completion percentage is inferred.

Detailed opcode evidence: `decompilation/annotated/dos_compatibility_residual_v131.md`. Exact reproducible original-source auditor: `tools/audit_dos_compatibility_residual_v131.py`. Machine report: `decompilation/reports/dos_compatibility_residual_v131_2026-10-16.json`.

No original proprietary binary/assets, original executable, server or browser deployment were changed. Next focus: authoritative original LE relocation/caller evidence for the synthetic helper, original DOS behavioral parity and native browser gameplay.
