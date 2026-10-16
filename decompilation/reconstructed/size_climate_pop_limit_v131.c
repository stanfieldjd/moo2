/*
 * Fully recovered MOO2 v1.31 source:
 *   Size_And_Climate_Max_Population_ CODE 0xD0A18, 49 bytes
 *   Size_And_Climate_Race_Pop_Limit_ CODE 0xD0A93, 188 bytes
 * Original EXE SHA-256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Full original bodies:
 * CODE 0xD0A18 SHA256 405533edb6bdde5d69b314322b9a8a024bacd606529689968521f5c02b54bb14
 * CODE 0xD0A93 SHA256 7c8629ad880163c090835f05037b1bde31bf058a183d30069b2af1b014eb032d
 *
 * In the original code, indexed lookup _planet_max_population is
 * original initialized DATA segment 2 offset 0x5806, five bytes:
 * [5,10,15,20,25]. The climate weighting table is original CODE
 * object 1 offset 0xCD4EB, sixteen bytes:
 * [25,25,25,25,25,25,40,60,80,100,30,60,30,60,60,120].
 *
 * MaxPop ABI EAX=planet size, EDX=climate index, BL=0/1 bonus:
 *   pct = min(100, climate_pct[climate] + 25*bonus);
 *   floor((pct*planet_max_population[size]+50)/100)
 * Original uses signed IDIV, but all bounded valid inputs positive.
 *
 * Race ABI EAX=size, EDX=environment, BX=race 0..9:
 * 0..7: player record at race*0xEA9; +0x8B6 nonzero activates
 * race-specific 25% climate multiplier bonus;
 * race 8 always activates it; race 9 does not.
 * For race <8 whose player record BYTE+0x8AB is nonzero,
 * environment 4,6 -> 8 and environment 5,8 -> 9.
 * This transformation affects the table lookup, not colony+0xE2.
 * Source calls MaxPop after the transformation.
 * For race <8 whose player BYTE+0x8AC is nonzero, adds
 * signed16(2*(planet_size+1)) to the MAX population result.
 * Source race index>=8 (8 or9) does not access player records.
 *
 * Valid in-game sizes 0..4, climates 0..15, races 0..9.
 * Bounds checks and explicit rejection of broken data are host
 * safety behavior, not original DOS memory semantics.
 */
#include <stdint.h>
#include <stddef.h>
#include "size_climate_pop_limit_v131.h"

static const uint8_t moo2_v131_source_size_base[5]={5,10,15,20,25};
static const uint8_t moo2_v131_source_climate_weight[16]={
    25,25,25,25,25,25,40,60,80,100,30,60,30,60,60,120
};
Moo2V131SizeClimateStatus moo2_v131_derived_size_climate_max_population(
    uint8_t planet_size,uint8_t environment,
    uint8_t bonus,int32_t *result)
{
    if(!result || planet_size>=5u || environment>=16u || bonus>1u)
        return MOO2_V131_SIZE_CLIMATE_INVALID;
    uint32_t pct=(uint32_t)moo2_v131_source_climate_weight[environment]+
                 (uint32_t)bonus*25u;
    if(pct>100u)pct=100u;
    const uint32_t numerator=pct*
        (uint32_t)moo2_v131_source_size_base[planet_size]+50u;
    *result=(int32_t)(numerator/100u);
    return MOO2_V131_SIZE_CLIMATE_OK;
}
Moo2V131SizeClimateStatus moo2_v131_derived_size_climate_race_pop_limit(
    const Moo2V131SizeClimateContext *ctx,
    uint8_t planet_size,uint8_t environment,
    int16_t race,int32_t *result)
{
    if(!ctx || !result || planet_size>=5u || environment>=16u ||
       race<0 || race>9)
        return MOO2_V131_SIZE_CLIMATE_INVALID;
    uint8_t bonus=(uint8_t)(race==8);
    const uint8_t *player=NULL;
    if(race<8) {
        if(!ctx->players || (size_t)race>=ctx->player_count)
            return MOO2_V131_SIZE_CLIMATE_INVALID;
        player=ctx->players+(size_t)race*0xEA9u;
        bonus=(uint8_t)(player[0x8B6u]!=0u);
        if(player[0x8ABu]!=0u) {
            if(environment==4u || environment==6u)
                environment=8u;
            else if(environment==5u || environment==8u)
                environment=9u;
        }
    }
    int32_t base=0;
    Moo2V131SizeClimateStatus rc=
        moo2_v131_derived_size_climate_max_population(
            planet_size,environment,bonus,&base);
    if(rc!=MOO2_V131_SIZE_CLIMATE_OK)return rc;
    if(player && player[0x8ACu]!=0u)
        base+=(int32_t)(2u*((uint32_t)planet_size+1u));
    *result=base;
    return MOO2_V131_SIZE_CLIMATE_OK;
}
