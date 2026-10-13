# Master of Orion II v1.31: `Farload_Library_Data_` — recovered complete instruction boundaries

**Status:** every byte in this 760-byte symbol interval is accounted for
as **744 bytes of decoded instructions** and **16 bytes of embedded
dispatch-table data**. Original file-open, header, offset lookup,
allocation, and return branches have been traced. This is not an
equivalent C implementation of the complete loader; the original
error-handler, allocation internals and full ABI remain separate work.

Authenticated source `ORION2.EXE`, SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
Original Watcom CODE offset `0x116F3B..0x117232` inclusive
(760 bytes); relocated analysis-image virtual addresses are original
CODE offsets plus `0x10000`.

Reproducible source-hash-guarded audit:
`tools/audit_farload_library_v131.py`.
Recorded output:
`decompilation/reports/farload_library_audit_2026-10-13.json`.

## Decoding correction: data was being read as code

The previous linear disassembly gave **200 instructions and 24 jumps**.
Those counts were inflated because it decoded **four embedded DWORD
case pointers** at CODE offsets `0x117145..0x117154` as instructions.

Decoding separately before and after this table yields exactly:

| Original source evidence | Verified value |
| --- | ---: |
| Routine size | 760 bytes |
| Embedded jump table | 16 bytes |
| Decoded machine instructions | **194** |
| Direct calls, all mapped to original symbols | **27** |
| Conditional/unconditional jump instructions | **21** |
| Return | `0x117230: RET 0x0C` |

The original source is little-endian. Its table has exact DWORD
targets `0x117197`, `0x1171BA`, `0x1171E0`,
`0x117206`. The indirect jump at `0x117190` indexes
those entries with `EAX = original_ECX * 4`.
The immediately preceding `CMP [EBP-0x38],3; JA 0x11720C`
bounds the valid indexed modes to **0..3**.

**Inventory gap identified:** this exact indirect JMP was not in
the earlier `decompilation/indirect_transfers.csv` /
`switch_tables.csv` inventories. Those earlier global counts,
especially library/runtime switch totals, cannot be considered
exhaustive until decoding of interspersed data regions is repaired.
The new audit verifies this individual original switch table without
silently changing the prior inventories.

## Original loader state and file-open branches

Watcom original DATA object 2 globals and their original offsets:

- `_farload_file_flag`: `0xC576`
- `_secondary_drive_path`: `0xC544`
- `_lbx_header`: `0x43A6C`, a 2,048-byte header buffer
- `_farload_fptr`: `0x4426C`
- `_farload_file_name`: `0x44270`

The routine saves input EAX/EDX/EBX/ECX as stack locals. A negative
signed EDX index takes `Error_Handler_` code **4**.
If an LBX file is open, the routine uses case-insensitive
`_stricmp_` to compare the requested filename to the retained
`_farload_file_name`. An equal name branches directly to header
lookup; a different name leads to `fclose_` then new open.

The new-open path stores the filename with `strcpy_` and
tries `fopen_`. If that fails, it considers
`_secondary_drive_path`, combines a candidate pathname via
`strcpy_`/`strcat_`, and retries `fopen_`.
Original failure paths call `Error_Handler_` with **code 1**.
The file-open mode pointer and exact path construction are observed
in instructions, but are not fully abstracted here into a host
filesystem policy.

## Original file header and entry selection

1. At original CODE `0x117032..0x117047`, call
   `fread_` into `_lbx_header`, passing **size 0x800
   (2048 bytes), count 1**, and the opened file pointer.
2. Original `0x11704C..0x11706B` zero-extends the WORD at
   **header+2** and checks that it equals `0xFEAD`.
   An unexpected value takes `Error_Handler_` **code 7**;
   normal initialization sets `_farload_file_flag=1`.
3. Original `0x117075` loads an unaligned DWORD from
   **header-2** and `SAR 16` yields a signed count based on
   the low 16 bits at **header+0**. That count must be
   **strictly greater** than the requested signed EDX entry
   index. Failure takes error **code 8**.
4. Offsets at original CODE `0x117092..0x1170B6` select
   two **DWORD** entry boundaries from `header+8+4*index`
   and `header+12+4*index` respectively, and compute their
   difference. Original `fseek_` then seeks to the first
   boundary.
5. Original CODE `0x1170C8..0x1170F3` performs two
   `fread_` calls with **size 2, count 1** into
   `[EBP-0x8]` and `[EBP-0x4]`. The low WORDs are
   subsequently used in range/type checks and to determine
   byte offsets and payload length.
6. The two-word data type/format semantics still need confirmation
   from original LBX records and cross-references. Do **not**
   label either WORD as compressed length, frame count, or record
   type merely from guessed structure names.

### Important signed/sentinel behavior

At `0x1170F8..0x117101`, exact instructions are:
`XOR EAX,EAX`, `MOV AX,[EBP+0x14]`,
`CMP EAX,0xFFFFFFFF`, `JNE`.
Because the 16-bit MOV runs after clearing EAX, the compared 32-bit
EAX must lie in **0..65535**, so it can never equal 0xFFFFFFFF.
Consequently, the following branch that attempts to compute an
implicit length is **unreachable under these instructions**.
Do not invent working `-1`/wildcard-length behavior in a native
translation. This does not establish whether the original source
intended something else.

Then original code checks the first low-WORD field against the
requested start parameter (unsigned `JA`, error code **10**)
and compares the second low-WORD field against a caller-supplied
WORD (error **code 9** on mismatch). The full ABI must be
recovered before naming all these caller parameters.

## Four actual allocation modes

| Original ECX mode | CODE destination | Observed behavior |
| ---: | --- | --- |
| 0 | `0x117197` | `Allocate_Space_No_Header_` with computed byte count; allocation failure reports error **3** |
| 1 | `0x1171BA` | `Allocate_First_Block_No_Header_` with caller EBX and byte count; failure reports error **5** |
| 2 | `0x1171E0` | `Allocate_Next_Block_No_Header_` with caller EBX and byte count; failure reports error **5** |
| 3 | `0x117206` | Use the original caller EBX buffer pointer with no allocation |
| greater than 3, unsigned | `0x11720C` directly | Retains the saved original ECX local as destination pointer; exact caller contract pending |

A later `fread_` at `0x11721D` transfers the computed
payload byte count to the selected destination. The routine
returns that destination pointer via EAX and executes `RET 12`,
cleaning twelve bytes of the caller's stack parameters.
Calling conventions therefore cannot be blindly rewritten as
ordinary 32-bit cdecl.

**No decompression call appears anywhere inside this original
760-byte routine.** That negative observation is limited to
this routine; archive entry representation, encoding/compression
and any work by direct callees require separate examination.

## Fatal loader error routes independently decompiled

A second hash-guarded audit traced all **10** direct
`Farload_Library_Data_` calls to `Error_Handler_`
at original CODE `0x1173DC`. That handler is a **439-byte**
function with 106 decoded instructions; it uses
`strcpy_`, `strcat_`, `itoa_`, and case-selected DATA
messages, then converges on `Exit_With_Message_`
at CODE `0x116487`. Its original called helper invokes
Watcom runtime `exit_(1)` at CODE `0x12F2F4`.
These original error paths are **fatal**, not ordinary
negative return values.

| Error condition recognized at the loader call site | Original handler code | CODE call offset |
| --- | ---: | --- |
| Negative entry index | 4 | `0x116F6D` |
| Initial or secondary file open failed | 1 | `0x116FDF`, `0x11702D` |
| LBX header signature mismatch | 7 | `0x117066` |
| Entry index beyond header count | 8 | `0x11708D` |
| Entry WORD/count condition failed | 10 | `0x117122` |
| Entry type/stride WORD differs from caller | 9 | `0x11713B` |
| Ordinary allocation failed (mode 0) | 3 | `0x1171B3` |
| Block allocation failed (modes 1, 2) | 5 | `0x1171D9`, `0x1171FF` |

`Error_Handler_` also contains direct dispatch branches
for codes **2** and **16**, which these 10 loader calls
do not use. Code 6 has no separate selected message in
the observed dispatch. All routes converge on the fatal
helper; callers must not assume a successful return.

Reproducible audit:
`tools/audit_farload_error_handler_v131.py`.
Persisted metadata:
`decompilation/reports/farload_error_handler_audit_2026-10-13.json`.

A modern reimplementation can choose safer exception/error
handling, but that would be a **deliberate compatibility change**,
not the original program's observed failure behavior.

## Next reconstruction boundary

The high-level call chain is now:

`Load_E_Strings_` →
`Farload_Data_Static_` (90-byte wrapper) →
**`Farload_Library_Data_` (original instruction boundaries recovered)** →
`fopen_/fseek_/fread_`, allocation helpers, and `Error_Handler_`.
After a successful load, `Load_E_Strings_` constructs its
812 runtime string pointers and calls the fully reconstructed
`Load_H_And_Pro_File_Strings_` (199 bindings).

Work remaining: recover precise ABI/caller argument ownership, reduce
the 21-branch CFG to validated complete semantic C, map all
`Error_Handler_` codes to fatal/nonfatal behavior, decode original
LBX entry/header semantics using lawful local files, and extend the
global indirect-dispatch inventory to include data-embedded tables.
No original game file or string bytes are committed here.
