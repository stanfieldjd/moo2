# v1.31 `Farload_Data_Static_`: 90-byte loader wrapper recovered

**Status:** source-instruction-accounted wrapper and its exact callee
have been recovered. This is **not** recovery of the underlying LBX
file loader or a license to distribute original text files.

Source: official `ORION2.EXE`, SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

Original Watcom CODE symbol: `Farload_Data_Static_` at
`0x116C91`, 90 bytes through `0x116CEA`
(relocated analysis-image entry `0x126C91`).

## Complete observed wrapper operations

- Calls Watcom helper `__CHK` (`0x12F1E0` original) with
  immediate 0x34 at function entry, preserves ESI/EDI/EBP, and
  establishes a 24-byte local frame.
- Saves input EAX, EDX, EBX and ECX into stack-frame locals,
  respectively `EBP-0x18`, `EBP-0x14`, `EBP-0x10`,
  `EBP-0x0C`.
- Zero-extends each of two *16-bit* stack arguments
  from `[EBP+0x14]` and `[EBP+0x10]`, pushes the resulting
  DWORDs in that order, then pushes the preserved original ECX.
- Sets `ECX=3`, restores the other original register inputs
  (EBX, EDX, EAX), and directly calls
  `Farload_Library_Data_` at original CODE `0x116F3B`
  (relocated VA `0x126F3B`). This callee is a separate,
  760-byte function now fully segmented into instructions and an embedded
  jump table; its file-I/O and allocation semantics remain incomplete.
- Copies the returned EAX into two successive locals and
  returns it unchanged after restoring the frame and registers.
  Ends with `RET 8`, i.e. the original wrapper cleans up
  **eight bytes** of caller stack arguments.

There are no other direct calls or conditional branches in this
wrapper. This completes its machine-instruction *control-flow
structure* but does not establish the semantic meaning of every
register or parameter, the actual data decoding, file-not-found
behavior, failure protocol or allocation behavior of
`Farload_Library_Data_`.

## Relationship to original EStrings initialization

`Load_E_Strings_` passes one of six original `estr*.lbx`
filenames, static buffer base `DATA+0x29370`, and two
explicit pushed arguments including capacity `0x5208` and
entry number `1` before calling this wrapper. The fixed ECX
value **3** is now independently verified as the 
**caller-supplied-buffer allocation mode**, since the original
four-entry dispatch at CODE `0x117190` reaches `0x117206`, which
returns the original caller EBX buffer without allocation.

The caller's two pushed arguments in the EStrings path are exactly
**count 1** and **expected item stride 0x5208**. Original ECX=0 is
transmitted as start index 0 into `Farload_Library_Data_`.
Thus the observed wrapper issues an original request for one
21,000-byte unit from entry start 0 into the existing
`_string_data` buffer. This is a reconstruction of this
specific caller ABI, not a general proof about every farload caller.

See `decompilation/annotated/farload_library_data_v131.md`
and `decompilation/reconstructed/farload_lbx_entry_layout_v131.c`.
The original lower-level file-I/O, mode-specific allocation
internals and game-resource semantics remain to reconstruct;
private LBX files and original executables remain off the public site.
