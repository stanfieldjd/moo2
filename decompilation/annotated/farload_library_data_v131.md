# v1.31 `Farload_Library_Data_`: original loader reconstruction in progress

**Status:** original 760-byte wrapper/core loader disassembled,
direct-call targets resolved against Watcom symbols, several
file-header validation and allocation paths identified. This
is not yet a complete semantically equivalent C translation.

Source original `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

Original Watcom CODE entry `0x116F3B`, 760 bytes through
`0x117232`; relocated analysis entry `0x126F3B`.
The original symbol-bounded i386 decode yields **200 instructions**,
**24 conditional/unconditional jump instructions** and one apparent
RET in this interval. All statements below are bounded to the
original machine instructions; direct CALLs are not treated as fully
reconstructed callees.

## Original named globals and call sequence

The original Watcom DATA symbol table, combined with LE relocation,
confirms the following (DATA object 2 offsets):

- `_farload_file_flag` at `0xC576` (relocated VA `0x17C576`)
- `_farload_fptr` at `0x4426C` (relocated VA `0x1B426C`)
- `_farload_file_name` at `0x44270` (relocated VA `0x1B4270`)

The initial routine saves EAX/EDX/EBX/ECX into a local frame,
checks its signed data-index argument, and invokes
`Error_Handler_` on invalid conditions. It checks the file flag,
uses the original case-insensitive comparison helper
`_stricmp_` against `_farload_file_name` to decide whether
the existing file can be reused, otherwise calls
`fclose_` and copies a new filename with `strcpy_`.

The observed direct-call sequence also includes:

- `fopen_`, `strcat_` and a second `fopen_` path,
  consistent with opening from more than one original directory
- `fseek_` for entry-offset positioning
- repeated `fread_` calls for entry and payload/header reading
- repeated `Error_Handler_` calls at validation failures
- `Allocate_Space_No_Header_`,
  `Allocate_First_Block_No_Header_`, and
  `Allocate_Next_Block_No_Header_` for separate
  allocation paths

Original instruction ranges `0x117075..0x1170B6` select
library-entry offsets from globals based on the signed input
index. `0x1170BB..0x1170F3` seek and read two consecutive
two-byte fields. Branches at `0x1170F8..0x11713B`
perform size/field consistency checks and report via
`Error_Handler_` where necessary.

No specific compression algorithm, memory ownership policy,
LBX entry format, file-sharing behavior, or complete fallback
path is established by this checkpoint. Such semantics must
come from full dataflow recovery and original-file evidence,
rather than an inference from the names of file-I/O functions.

## Next steps

Reconstruct the complete 760-byte conditional CFG and original
Watcom calling convention; identify exact meanings and units of
the two 16-bit fields and the allocation mode, trace the
`fread_` sizes and any decompression callbacks, and align
the result with private lawful `estr*.lbx` inputs without
publishing them. Follow through `Farload_Data_Static_`,
`Load_E_Strings_`, and the now fully mapped
`Load_H_And_Pro_File_Strings_`.

No site gameplay, Xbox controls or Qwen files were changed.
