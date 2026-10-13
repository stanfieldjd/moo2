/*
 * Isolated original v1.31 player-stat WRITE from colony bomb/bio hit paths.
 * NOT full original resolvers or game-state equivalent code.
 * Source-anchored CODE 0xCD1D3..0xCD1EF, 0xCD115..0xCD12F:
 *  signed colony[0] * 0xEA9 -> _player base,
 *  signed event[0] * 2 + 0x6FF -> 16-bit per-opponent stat,
 *  INC WORD (1) with modulo 65536 semantics.
 * Source CODE 0xCCFBE..0xCCFDB and 0xCD2AA..0xCD2C6 perform
 *  ADD WORD 0x0A to the same stat under their source conditions.
 * This function performs ONLY the selected +1 or +10 increment.
 * Original DOS code does not bounds-check; host validation is deliberate.
 */
#include "colony_hit_player_stats_v131.h"
Moo2V131OwnerStatStatus moo2_v131_derived_colony_hit_owner_stat(
    uint8_t *players,size_t player_buffer_bytes,
    const uint8_t *colony,size_t colony_buffer_bytes,
    const uint8_t *event,size_t event_buffer_bytes,
    Moo2V131OwnerStatDelta original_branch_increment)
{
    if(!players || !colony || !event || colony_buffer_bytes<1 ||
       event_buffer_bytes<1 ||
       (original_branch_increment!=MOO2_V131_OWNER_STAT_INCREMENT_ONE &&
        original_branch_increment!=MOO2_V131_OWNER_STAT_INCREMENT_TEN))
        return MOO2_V131_OWNER_STAT_INVALID;
    /* Original MOVSX BYTE, sign extended to 32 bits for both players. */
    int32_t owner=colony[0]<128u ? colony[0] : (int32_t)colony[0]-256;
    int32_t opponent=event[0]<128u ? event[0] : (int32_t)event[0]-256;
    if(owner<0 || opponent<0) return MOO2_V131_OWNER_STAT_INVALID;
    const size_t offset=(size_t)owner*0xEA9u+0x6FFu+2u*(size_t)opponent;
    if(player_buffer_bytes<2u || offset>player_buffer_bytes-2u)
        return MOO2_V131_OWNER_STAT_INVALID;
    uint8_t *word=players+offset;
    uint16_t prior=(uint16_t)(word[0]|((uint16_t)word[1]<<8));
    uint16_t next=(uint16_t)(prior+(uint16_t)original_branch_increment);
    word[0]=(uint8_t)next;
    word[1]=(uint8_t)(next>>8);
    return MOO2_V131_OWNER_STAT_OK;
}
