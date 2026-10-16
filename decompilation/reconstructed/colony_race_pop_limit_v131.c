/*
 * Complete 81-byte original v1.31 Colony_Race_Pop_Limit_ wrapper,
 * original CODE 0xD0C1D..0xD0C6D, Watcom entry
 * EAX=colony*, EDX signed race class, return EAX.
 * SHA256 original body:
 * 97d4044d83c3594792d5d159b6858599d63f153c9532081fa6aae13e70838e58
 * Original executable SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Source uses original colony environmental BYTE+0xE2, planet size
 * BYTE+0x05, race index from EDX. Delegates to original
 * Size_And_Climate_Race_Pop_Limit_ at CODE 0xD0A93,
 * signextends low AX after return; adds 5 if owning player's
 * tech BYTE+0x11A==3 and adds 2 if colony building BYTE+0x145
 * is nonzero. The size/climate helper is not replaced by guesswork.
 */
#include <stddef.h>
#include <stdint.h>
#include "colony_race_pop_limit_v131.h"

static int32_t moo2_v131_racelimit_s16(const uint8_t *p) {
    uint16_t x=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return x<32768u?(int32_t)x:(int32_t)x-65536;
}
Moo2V131RaceLimitStatus moo2_v131_derived_colony_race_pop_limit(
    const Moo2V131RaceLimitContext *ctx,
    const uint8_t *colony,size_t colony_bytes,
    int16_t race_index,int32_t *result)
{
    if(!ctx || !colony || colony_bytes<0x169u || !result ||
       !ctx->planets || !ctx->players || !ctx->size_and_climate_limit)
        return MOO2_V131_RACELIMIT_INVALID;
    int32_t planet_id=moo2_v131_racelimit_s16(colony+2u);
    int32_t owner=(int32_t)(int8_t)colony[0u];
    if(planet_id<0 || (size_t)planet_id>=ctx->planet_count ||
       owner<0 || (size_t)owner>=ctx->player_count)
        return MOO2_V131_RACELIMIT_INVALID;
    const uint8_t *planet=ctx->planets+(size_t)planet_id*0x11u;
    const uint8_t *player=ctx->players+(size_t)owner*0xEA9u;
    int32_t base=0;
    if(!ctx->size_and_climate_limit(ctx->opaque,
              planet[0x05u],colony[0xE2u],race_index,&base))
        return MOO2_V131_RACELIMIT_CALLBACK_FAILED;
    /* Watcom original 0xD0C51 CWDE sign-extends AX. */
    uint16_t low=(uint16_t)base;
    int32_t output=low<32768u?(int32_t)low:(int32_t)low-65536;
    if(player[0x11Au]==3u)output+=5;
    if(colony[0x145u]!=0u)output+=2;
    *result=output;
    return MOO2_V131_RACELIMIT_OK;
}
