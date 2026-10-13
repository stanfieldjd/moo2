/*
 * DERIVED original MOO2 v1.31 biological planet damage chance adjustment.
 * Isolated arithmetic, NOT the complete 775-byte planet-damage function.
 *
 * Original CODE path 0x2A43A..0x2A48F:
 *   owner selected by original _combat_defender_player (DATA+0x2188E)
 *   and original player record at _player + owner*0xEA9
 *   if player+0x182 == 3, CWD SUB AX,DX SAR AX,1, write WORD [damage]
 *   else if player+0x1D8 == 3, CWD SHL DX,2 SBB AX,DX SAR AX,2,
 *                              write WORD [damage]
 *   Random_(100), then CMP full EAX result with sign-extended WORD [damage].
 *   JG 0x2A6BD skips the downstream biological bomb result path.
 *
 * The low 16-bit signed fraction truncates toward zero in the original.
 * Original first condition takes precedence over second when both are 3.
 * Caller must check original +0x26 ship state and +0x80 flag before using
 * this sub-expression. Here we do not alter the game globals or invoke
 * the Random_ runtime; the rolled result is supplied separately.
 */
#include <stdint.h>

typedef enum {
    MOO2_V131_BIO_THRESHOLD_OK=0,
    MOO2_V131_BIO_THRESHOLD_INVALID_POINTER=1
} Moo2V131BioThresholdStatus;

static int32_t moo2_v131_bio_original_s16(uint16_t word) {
    return word < UINT16_C(0x8000)
         ? (int32_t)word : ((int32_t)word-65536);
}

Moo2V131BioThresholdStatus moo2_v131_derived_bio_threshold_adjust(
    uint16_t *candidate_word,uint8_t player_record_byte_182,
    uint8_t player_record_byte_1d8)
{
    if (!candidate_word)
        return MOO2_V131_BIO_THRESHOLD_INVALID_POINTER;
    int32_t value=moo2_v131_bio_original_s16(*candidate_word);
    if(player_record_byte_182==3u)
        value/=2;
    else if(player_record_byte_1d8==3u)
        value/=4;
    *candidate_word=(uint16_t)((uint32_t)value & UINT32_C(0xFFFF));
    return MOO2_V131_BIO_THRESHOLD_OK;
}

/* Original 0x2A48D CMP EAX,EDX; 0x2A48F JG skip,
 * therefore the continued biological result path requires draw <=
 * the SIGN-EXTENDED threshold. This is a pure branch check.
 * Original Random_(100) only returns 1..100; this helper can check
 * caller-supplied values without generating or advancing the seed.
 */
int moo2_v131_derived_bio_roll_passes(
    uint16_t adjusted_candidate,uint32_t original_random100_result)
{
    const int32_t candidate=moo2_v131_bio_original_s16(adjusted_candidate);
    return ((int64_t)original_random100_result <= (int64_t)candidate);
}
