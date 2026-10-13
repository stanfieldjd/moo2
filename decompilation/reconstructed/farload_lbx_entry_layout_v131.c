/*
 * Master of Orion II v1.31 — DERIVED, ISOLATED original LBX layout logic.
 *
 * This is NOT original MicroProse C, a complete resource loader, or a
 * usable LBX parser. Source evidence from authenticated v1.31 original
 * Watcom instructions Farload_Library_Data_ (LE CODE 0x116F3B..0x117232).
 *
 * This isolates the verified header magic, entry-offset-table lookup,
 * embedded entry's two 16-bit fields and their offset/length arithmetic.
 * The original file-open, I/O, error-handler and allocation routines are
 * NOT reproduced here.
 *
 * Deliberate safety differences from original DOS:
 *  - explicit input length bounds checks and offset-pair validation
 *  - status values returned instead of original fatal Error_Handler_ -> exit
 * Original low-32-bit IMUL result is preserved by unsigned arithmetic.
 * Original absent / unreachable 0xFFFFFFFF wildcard count is not added.
 */
#include <stddef.h>
#include <stdint.h>

enum {
    MOO2_V131_LBX_HEADER_SIZE = 0x800,
    MOO2_V131_LBX_MAGIC = 0xFEAD
};

typedef enum {
    MOO2_V131_ENTRY_OK = 0,
    MOO2_V131_ENTRY_SOURCE_ERROR_4 = 4,
    MOO2_V131_ENTRY_SOURCE_ERROR_7 = 7,
    MOO2_V131_ENTRY_SOURCE_ERROR_8 = 8,
    MOO2_V131_ENTRY_SOURCE_ERROR_9 = 9,
    MOO2_V131_ENTRY_SOURCE_ERROR_10 = 10,
    /* Modern safety failure, not an original Watcom error code. */
    MOO2_V131_ENTRY_INVALID_BUFFER = 100
} Moo2V131DerivedEntryStatus;

typedef struct {
    uint32_t original_entry_begin;
    uint32_t original_entry_end;
    uint32_t original_entry_byte_span;
} Moo2V131DerivedEntryOffset;

typedef struct {
    uint16_t original_item_count;
    uint16_t original_item_stride_bytes;
    uint32_t seek_delta_after_two_entry_words;
    uint32_t requested_payload_bytes;
} Moo2V131DerivedPayloadSpan;

static uint16_t moo2_v131_lbx_u16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static uint32_t moo2_v131_lbx_u32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8)
         | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static int32_t moo2_v131_lbx_signed16(uint16_t x)
{
    return (x & UINT16_C(0x8000)) ? (int32_t)x - 65536 : (int32_t)x;
}

/* Derived from 0x11704C..0x1170C3. Original compares magic, header count,
 * reads DWORD start and next from header+8+4*index, and computes difference.
 * A modern safety check restricts index*4 to the supplied 2048-byte buffer.
 */
Moo2V131DerivedEntryStatus moo2_v131_derived_select_lbx_entry(
    const uint8_t *header, size_t header_size, int32_t entry_index,
    Moo2V131DerivedEntryOffset *out)
{
    if (!header || !out || header_size < MOO2_V131_LBX_HEADER_SIZE)
        return MOO2_V131_ENTRY_INVALID_BUFFER;
    if (entry_index < 0)
        return MOO2_V131_ENTRY_SOURCE_ERROR_4;
    if (moo2_v131_lbx_u16(header + 2) != MOO2_V131_LBX_MAGIC)
        return MOO2_V131_ENTRY_SOURCE_ERROR_7;

    /* Original unaligned DWORD at HEADER-2, arithmetic shift right 16,
       gives a sign-extended low WORD from HEADER+0. */
    const int32_t original_count =
        moo2_v131_lbx_signed16(moo2_v131_lbx_u16(header));
    if (original_count <= entry_index)
        return MOO2_V131_ENTRY_SOURCE_ERROR_8;

    /* The original does not bounds-check the table against 2048 bytes. */
    if ((uint32_t)entry_index > (MOO2_V131_LBX_HEADER_SIZE - 12u)/4u)
        return MOO2_V131_ENTRY_INVALID_BUFFER;
    size_t at = 8u + 4u * (uint32_t)entry_index;
    const uint32_t start = moo2_v131_lbx_u32(header + at);
    const uint32_t end   = moo2_v131_lbx_u32(header + at + 4u);

    /* Preserve the original unsigned 32-bit subtraction. */
    out->original_entry_begin = start;
    out->original_entry_end = end;
    out->original_entry_byte_span = end - start;
    return MOO2_V131_ENTRY_OK;
}

/* Derived from the two original size-2 fread calls followed by
 * 0x11710C..0x11717D. 'first_two_words' are bytes read at the selected
 * LBX entry start; original uses their low 16 bits.
 *
 * original start index = caller stack arg at EBP+0x10
 * original count       = caller stack arg at EBP+0x14
 * expected byte stride = caller stack arg at EBP+0x18
 *
 * A mode-3 EStrings caller uses start=0, count=1, expected=0x5208,
 * and points to _string_data rather than allocating a new buffer.
 */
Moo2V131DerivedEntryStatus moo2_v131_derived_item_span(
    const uint8_t *first_two_words, size_t size,
    uint32_t start_index, uint32_t requested_count,
    uint16_t expected_stride, Moo2V131DerivedPayloadSpan *out)
{
    if (!first_two_words || size < 4u || !out)
        return MOO2_V131_ENTRY_INVALID_BUFFER;
    const uint16_t count = moo2_v131_lbx_u16(first_two_words);
    const uint16_t stride = moo2_v131_lbx_u16(first_two_words + 2);

    /* Original CMP zero-extended COUNT, START; JA success. */
    if ((uint32_t)count <= start_index)
        return MOO2_V131_ENTRY_SOURCE_ERROR_10;
    if (stride != expected_stride)
        return MOO2_V131_ENTRY_SOURCE_ERROR_9;

    out->original_item_count = count;
    out->original_item_stride_bytes = stride;
    out->seek_delta_after_two_entry_words =
        (uint32_t)stride * start_index;
    out->requested_payload_bytes =
        (uint32_t)stride * requested_count;
    return MOO2_V131_ENTRY_OK;
}
