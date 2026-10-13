# v1.31 `Load_E_Strings_` and `E_Strings_`: original text bootstrap

**Status:** recovered original LE relocation, six file selectors, static
buffer/pointer layout, 812-entry runtime pointer-building loop,
overflow path and next initialization call. This is original
instruction-supported C-like reconstruction, **not** the original
MicroProse source and not a parser for LBX files.

Original executable identity: SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

## Watcom symbol/control-flow anchors

- `E_Strings_`: CODE `0xBDF5C`, 9 bytes, through `0xBDF64`.
- `Load_E_Strings_`: CODE `0xBDF65`, 384 bytes, through
  `0xBE0E4`.
- `Load_H_And_Pro_File_Strings_`: CODE `0xBE0E5` (a separate
  follow-on initializer now reconstructed from all 600 instructions).
- Original Watcom DATA symbol `_strings`: DATA offset
  `0x2E578`, relocated virtual address `0x19E578`.
- Original fixed string-byte buffer starts at DATA offset
  `0x29370` (relocated `0x199370`). Its end is exactly
  `0x2E578`, leaving **`0x5208` = 21,000 bytes**.
- LE CODE relocations in the derived analysis image convert
  `MOV EAX,[EAX*4+0x2E578]` into
  `MOV EAX,[EAX*4+0x19E578]`.

The original initialized DATA object has zero pointer values at both
`_strings[0x0C]` and `_strings[0x11E]`; they are populated
**at runtime**. It would be erroneous to infer missing translations
from those static zeros.

## Six file selectors, copied directly from original DATA text

The language-selection byte at original DATA offset `0x1CAE` selects:

| Selector byte | EStrings file loaded | Follow-on `main*.lbx` filename |
| ---: | --- | --- |
| 0 | `estrings.lbx` | `maintext.lbx` |
| 1 | `estrGERM.lbx` | `maingerm.lbx` |
| 2 | `estrFREN.lbx` | `mainfren.lbx` |
| 3 | `estrSPAN.lbx` | `mainspan.lbx` |
| 4 | `estrITAL.lbx` | `mainital.lbx` |
| 5 | `estrPOLI.lbx` | `mainpoli.lbx` |

The first column's EStrings file names come from original DATA offsets
`0x1E8C,0x1E99,0x1EA6,0x1EB3,0x1EC0,0x1ECD`.
The follow-on filenames come from DATA offsets
`0x1EFF,0x1EF2,0x1F0C,0x1F19,0x1F26,0x1F33`, respectively.
Their assignments are verified independently from the branch chain at
`0xBE056` through `0xBE0DE`. Do not infer exact locale
semantics beyond the explicit file selectors; the original game's
language setting and LBX contents should be cross-checked separately.

## Confirmed load sequence

1. Based on selector 0–5, `Load_E_Strings_` prepares the original
   EStrings filename address in EAX, buffer pointer `0x199370` in EBX,
   byte capacity `0x5208` as a pushed stack argument, and the
   original call register/stack parameters for
   `Farload_Data_Static_` (CODE `0x116C91`, relocated VA
   `0x126C91`). This call returns a pointer copied to EBX.
   The loader is not yet reconstructed, so file read/failure
   semantics remain pending.
2. Set 16-bit loop index EDX=0. For indices **0 through 811**
   (`CMP EAX,0x32C; JB`), write the current EBX pointer to
   `_strings[index]`.
3. Using `REPNZ SCASB` with AL=0, locate the terminating zero
   of the current string, then advance EBX by the number of scanned
   bytes **including** the terminating zero. This is an ordered
   NUL-terminated string table, not a fixed-width array.
4. After exactly 812 pointers have been written, compare final EBX
   against `0x19E578` **unsigned**. If the text cursor is above
   the buffer end, call original `Exit_With_Message_` with the
   diagnostic `you blew the array eric` at DATA offset `0x1EDA`.
   The error routine calls the runtime `exit_(1)`.
   The exact memory-safety policy for a modern port must separately
   check all intermediate pointers, not only the original final
   postcondition.
5. Call `Load_H_And_Pro_File_Strings_` at original
   CODE `0xBE0E5`. Its first instructions look up EStrings
   indexes `0x268,0x269,0x26A,...` and store the resulting
   pointers into individual globals. The complete 2,996-byte
   subsequent function still needs decoding.
6. The later part of `Load_E_Strings_` selects a
   `main*.lbx` filename and copies **13 bytes** via three
   `MOVSD` and one `MOVSB` into a destination obtained
   from a global pointer. This prepares another resource name;
   additional use sites must be traced.

## Isolated C-like semantic structure

```c
// Derived algorithm only. It deliberately does not provide file loading,
// initialization ordering, memory allocation, text resources, or original
// Watcom ABI. Original LBX assets are NOT stored with this reconstruction.

static const char *estring_files[6] = {
    "estrings.lbx", "estrGERM.lbx", "estrFREN.lbx",
    "estrSPAN.lbx", "estrITAL.lbx", "estrPOLI.lbx"
};

static const char *main_files[6] = {
    "maintext.lbx", "maingerm.lbx", "mainfren.lbx",
    "mainspan.lbx", "mainital.lbx", "mainpoli.lbx"
};

void derived_Load_E_Strings(uint8_t mode) {
    // Original expects a valid language mode 0..5.
    char *cursor = Farload_Data_Static(estring_files[mode],
                                      /* capacity */ 0x5208);
    for (unsigned i = 0; i < 0x32C; i++) {
        strings[i] = cursor;
        cursor += strlen(cursor) + 1;
    }
    if (cursor > string_buffer_end)
        Exit_With_Message("you blew the array eric");

    Load_H_And_Pro_File_Strings();
    prepare_main_filename(main_files[mode]);  // 13-byte copy
}

char *derived_E_Strings(int16_t index) {
    return strings[index];  // original direct signed-index table read
}
```

Modern code must provide checked bounds on every string scan and index;
the original routine relies on valid data and uses a post-scan
overflow check. The translation above is **not yet complete or safe
to run** with arbitrary inputs.

## Integration relevance

This resolves why `Pop_State_String_`, whose two original
indexes are `0x11E` (AX zero) and `0x0C` (AX nonzero), has
no meaningful static text pointer until the runtime text
initialization occurs. A future browser implementation may need
licensed private source text assets, but those original LBX files
must not be committed to GitHub or deployed publicly without
the appropriate rights.

The follow-on initializer is now fully decoded structurally:
**199 string-ID lookups and global assignments**, covering
**188 distinct string IDs**, plus a final pointer copy and RET.
Original named destinations include the personality, objective, and
treaty label pointer arrays. The recovered assignment mapping is in
`decompilation/reports/h_pro_string_bindings_2026-10-13.json` and the
standalone derived C implementation is in
`decompilation/reconstructed/h_and_pro_file_strings_v131.c`.
All 199 generated assignments match the original instruction mapping,
and the derived C passed a strict syntax check.

Further work: reconstruct `Farload_Data_Static_`, LBX entry semantics
and string decoding; trace all `Load_E_Strings_` callers and the
language-selection byte initialization; recover runtime text
allocation, lifetime and error behavior. The complete game
is not yet decompiled.
