# Original DOS v1.31 Watcom PD16 video helper reconstruction

The DOS v1.31 Watcom CODE image contains a `__VideoBasePD16` symbol at original CODE 0x15839D. Its 188-byte extent begins with exactly eight zero bytes and continues with **four distinct, coherent 16-bit helper routines** at CODE 0x1583A5, 0x1583D5, 0x1583FC and 0x158420. A fifth one-byte RET helper at CODE 0x158459 is the original helper called by the separately recovered Greenleaf ISR.

This additional source-mode-specific reconstruction verifies **104 original contiguous 16-bit instructions occupying 181 source machine bytes** (four video helper routine bodies and the adjacent one-byte RET helper). It checks the exact SHA-256 of the full original 188-byte symbol (4fc3b2a5781a5ecac7bb49222db60a6217605e951969cacf3ef526ea4ed889d3), full machine-byte hashes for each of five functions, all decoded instruction boundaries, all **five original conditional/unconditional branch displacements**, all **three original near CALL targets**, and 23 source opcode/operand pairs. The 188-byte source symbol itself comprises eight known storage bytes and 180 executable helper bytes, not a single 188-byte executable function.

The authenticated original Watcom video helpers:
- Load the original video base as a far ES:BX pointer at DS:0x26D, calculate offset using 160×caller WORD plus 2×second caller WORD, then write the cursor far pointer at DS:0x271 and DS:0x273.
- Conditionally write a byte to ES:[BX] when saved video segment ES is nonzero; increase cursor BX by 2 and persist it.
- Traverse a NUL-terminated 16-bit addressed character sequence, dispatching each nonzero byte to the original single-character routine at CODE 0x1583D5.
- Convert a supplied WORD's low-byte upper and lower hex nibbles to ASCII with source SHIFT, AND, ADD and compare operations, dispatching exactly two output bytes to the same original character routine.
- Provide an adjacent one-byte RET helper used by the previously authenticated real-mode interrupt handler.

Original whole-file trust: `ORION2.EXE` SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`; original Watcom CODE SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. Original protected binary/asset files are local only.

Reproducer: `tools/audit_video_pd16_v131.py`; machine-readable result: `decompilation/reports/video_pd16_v131_2026-10-16.json`; source-body annotation: `decompilation/annotated/video_pd16_runtime_v131.md`. This is a distinct 16-bit-source audit and does **not** modify the global i386 original CODE CFG baseline (396,305 memberships and 20 apparent unresolved edges); those were intentionally not merged with unrelated 16-bit instruction counts.

The actual video display mode, emulator/hardware behavior, source callers, original DOS dynamic parity, native game browser port, modern graphics and Xbox controller pipeline remain unproven or unfinished. Do not infer complete remaster progress from this runtime-support subsystem audit.
