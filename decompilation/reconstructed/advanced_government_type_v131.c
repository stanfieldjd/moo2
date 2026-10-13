/*
 * Isolated derived Master of Orion II v1.31 routine, NOT original source.
 *
 * Original Watcom CODE symbol Get_Advanced_Government_Type_
 *   original CODE 0x83D0A..0x83D4A, 65 bytes.
 * Data object record pointer comes from original DATA+0x1FF98;
 * player record stride = 0xEA9; signed byte at player +0x89F.
 *
 * Input AX is a signed 16-bit player index.
 * The final original MOVSX AX,BL determines the 16-bit return value.
 * The table at original CODE+0x83CFA has four cases:
 * 0x83D36 -> 1, 0x83D3A -> 3, 0x83D3E -> 5, 0x83D42 -> 7.
 *
 * The signed byte is divided by 2 using CDQ; SUB EAX,EDX; SAR EAX,1,
 * which truncates toward zero even for negative operands.
 * Original unsigned CMP AL,3; JA selects zero for unsigned
 * low-byte quotient >3. Thus -1 maps to 1, not 0.
 *
 * This function only models valid game storage and does not implement
 * save parsing, the game turn loop, or original memory allocation.
 */
#include <stdint.h>

uint16_t moo2_v131_derived_advanced_government_type_from_byte(int8_t raw)
{
    /* C99+ signed division truncates toward zero. */
    int32_t quotient = (int32_t)raw / 2;
    uint8_t index = (uint8_t)quotient;
    if (index > 3u) return 0u;
    return (uint16_t)(2u * (uint16_t)index + 1u);
}

uint16_t moo2_v131_derived_get_advanced_government_type(
    const uint8_t *player_records_base, int16_t player_index)
{
    const uint8_t *player = player_records_base
                          + (int32_t)player_index * 0xEA9;
    const uint8_t encoded = player[0x89F];
    const int8_t raw = (int8_t)((encoded < 128u)
                             ? (int32_t)encoded : ((int32_t)encoded - 256));
    return moo2_v131_derived_advanced_government_type_from_byte(raw);
}
