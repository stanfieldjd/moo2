/*
 * Derived Master of Orion II v1.31 research-cost routines.
 *
 * Translated independently from the verified Watcom x86 instructions at
 * CODE offsets 0xFF93B (Get_Tech_Cost_), 0xFF85D (New_Get_Tech_Cost_)
 * and 0xD1E96 (Player_Research_Cost_).
 *
 * This file is not original MicroProse source, not a complete game module,
 * and not yet differentially tested against the original executable.
 * The supplied storage/IDs must already be valid in-game.
 *
 * The "static_data" pointer denotes LE DATA object 2, NOT code object 1;
 * original machine-code pointers require LE relocation.
 */
#include <stdint.h>

static uint16_t moo2_v131_read_le16(const uint8_t *bytes)
{
    return (uint16_t)((uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8));
}

static uint32_t moo2_v131_read_le32(const uint8_t *bytes)
{
    return (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8)
         | ((uint32_t)bytes[2] << 16) | ((uint32_t)bytes[3] << 24);
}

static int32_t moo2_v131_signextend16(uint16_t value)
{
    return value & UINT16_C(0x8000) ? (int32_t)value - 65536 : (int32_t)value;
}

/* Original 0xD1E96 through 0xD1EC5; eax=player, edx=technology. */
uint32_t moo2_v131_derived_player_research_cost(
    const uint8_t *static_data,
    const uint8_t *player_record,
    int32_t technology)
{
    int32_t id = moo2_v131_signextend16((uint16_t)technology);
    if (id <= 0)
        return UINT32_C(0);

    uint32_t cost = moo2_v131_read_le32(static_data + 0x5916
                                       + (uint32_t)id * UINT32_C(23));
    if (id >= 75)
        cost += (uint32_t)player_record[0x1D1 + id] * UINT32_C(10000);
    return cost; /* original 32-bit unsigned addition, with wraparound */
}

/* Original 0xFF93B, reached through 0xFF861/0xFF86C -> 0xD1E96.
 * BX = empire index, AX = initial technology index, DX = mode.
 */
uint32_t moo2_v131_derived_get_tech_cost(
    const uint8_t *static_data,
    const uint8_t *all_player_records,
    int16_t empire_index,
    int16_t technology_arg,
    uint16_t mode)
{
    int32_t technology = technology_arg;

    if (mode == UINT16_C(0x2000)) {
        uint16_t mapped = moo2_v131_read_le16(
            static_data + 0x607F + (int32_t)technology_arg * 13);
        technology = moo2_v131_signextend16(mapped);
    }
    const uint8_t *player_record =
        all_player_records + (int32_t)empire_index * 0xEA9;
    return moo2_v131_derived_player_research_cost(
        static_data, player_record, technology);
}
