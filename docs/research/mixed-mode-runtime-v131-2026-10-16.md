# Recovery of original MOO2 v1.31 16-bit runtime interrupt code

The prior Watcom CODE CFG audit left 21 unresolved edges. A full original-source review identifies a distinct CPU-mode issue: real-mode Greenleaf interrupt code was being interpreted by a single global **32-bit** disassembler despite containing actual **16-bit** instructions, far-pointer loads, hardware I/O, RETF and IRET.

Original v1.31 source body verification now passes for:
- __GreenleafFastRealIsr at CODE 0x15845A: 104 bytes, 45 fully contiguous decoded 16-bit instructions, 6 exact direct-branch targets and four original near calls to source RET helper 0x158459. The handler reads I/O status/data through IN/OUT, updates a 10-bit masked circular read/write index, supports a far-linked state list, and ends in RETF.
- __RealDispatcherRR16 at CODE 0x1584FE: 61 bytes, 36 fully contiguous original 16-bit instructions, two exact conditional branch targets, a genuine far indirect callback through [SI+0x10], conditional end-of-interrupt port writes, and final IRET.

A third false CFG entry is original CODE symbol _Alphabet at 0x134942: exact 37-byte radix lookup string 0123456789abcdefghijklmnopqrstuvwxyz followed by NUL. Original source byte-load instruction at 0x13498F references that address directly. Four of the old analyzer's unresolved apparent branches are actually ASCII lookup-table bytes misread as branch opcodes; four others are an artifact of decoding the two real-mode routines as 32-bit.

The reproducible audit is tools/audit_mixed_mode_runtime_v131.py, the full original-instruction annotation is decompilation/annotated/mixed_mode_runtime_v131.md, and the machine report is decompilation/reports/mixed_mode_runtime_v131_2026-10-16.json. Canonical original DOS EXE SHA-256: 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f. Canonical original Watcom CODE SHA-256: f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837.

All **81** complete 16-bit original machine instructions are decoded and byte-verified; eight source branch destinations, four original near helper CALL destinations, and twenty named original opcode checks are authenticated. The 16-bit auditor preserves the global 32-bit source CFG baseline of 396,138 instruction memberships and 21 reported unresolved edges rather than forcing code/data out of its scope to make the numeric metric look better.

Next: reconcile source CODE-object data labels and runtime marker ranges using type- and mode-aware function-entry treatment, and ultimately compare native reconstruction against original DOS behavior. Source audit does not imply restored original hardware IRQ operation, completed Xbox browser game, or any remeasured whole-executable semantic percent. Proprietary original game files and the website are untouched.
