/*
 * Full original-derived MOO2 v1.31 Planet_Max_Population_For_Player_
 * at CODE offset 0xD0B4F (206 bytes, shared Watcom exit 0xCEB17).
 * ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Complete named CODE source body SHA256:
 * 00adaceecdeea9bb7cd18420bf11803ee6d784361fb2282b2581b4122f72b886
 *
 * Original inputs EAX=planet pointer, EDX=player index (low WORD).
 * EAX return is the maximum population cap for that planet.
 *
 * When original planet signed colony ID WORD +0 ==-1, OR when
 * referenced colony BYTE+0x06 is nonzero, source uses:
 *   Size_And_Climate_Race_Pop_Limit_(planet BYTE+5, planet BYTE+8,
 *                                   requested player race),
 *   sign extend source low AX,
 *   +5 if player BYTE+0x11A == 3.
 * When colony exists, BYTE+0x06 ==0, and population BYTE+0x0A
 * ==0: call Colony_Race_Pop_Limit_(colony, requested race).
 * When colony exists and popcount>0: clear 10 class marks,
 * mark each original population low-nibble class from records
 * at colony+0x0C, then iterate classes 9..1 in DESCENDING order.
 * For each represented class, query Colony_Race_Pop_Limit_ and
 * return the maximum signed low16 capacity, starting at zero.
 * Class0 is not visited by the original class loop; this is
 * verified original behavior, not a modern correction.
 *
 * Source uses previously reconstructed complete original:
 *   Size_And_Climate_Max_Population_ CODE 0xD0A18,
 *   Size_And_Climate_Race_Pop_Limit_ CODE 0xD0A93,
 *   Colony_Race_Pop_Limit_ CODE 0xD0C1D.
 * No synthetic arithmetic callbacks.
 * Host bounds checks and invalid-state rejection are
 * safety adaptations, not original DOS undefined behavior.
 */
#include <stdint.h>
#include <stddef.h>
#include "planet_max_population_v131.h"
#include "size_climate_pop_limit_v131.h"
#include "colony_race_pop_limit_v131.h"

static int32_t moo2_v131_planet_max_s16(const uint8_t *p) {
    uint16_t w=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return w<32768u?(int32_t)w:(int32_t)w-65536;
}
static int moo2_v131_planet_max_size_climate_cb(
    void *opaque,uint8_t size,uint8_t climate,
    int16_t race,int32_t *out)
{
    const Moo2V131SizeClimateContext *source=
        (const Moo2V131SizeClimateContext *)opaque;
    return moo2_v131_derived_size_climate_race_pop_limit(
        source,size,climate,race,out)==MOO2_V131_SIZE_CLIMATE_OK;
}
Moo2V131PlanetMaxPopulationStatus
moo2_v131_derived_planet_max_population_for_player(
    const Moo2V131PlanetMaxPopulationContext *ctx,
    size_t planet_id,int16_t player_id,int32_t *result)
{
    if(!ctx || !ctx->planets || !ctx->colonies || !ctx->players ||
       !result || planet_id>=ctx->planet_count ||
       player_id<0 || player_id>=8 ||
       (size_t)player_id>=ctx->player_count)
        return MOO2_V131_PLANET_MAX_INVALID;
    const uint8_t *planet=ctx->planets+planet_id*0x11u;
    const int32_t colony_id=moo2_v131_planet_max_s16(planet);
    Moo2V131SizeClimateContext sc={ctx->players,ctx->player_count};
    Moo2V131RaceLimitContext rc={
        ctx->planets,ctx->planet_count,ctx->players,
        ctx->player_count,moo2_v131_planet_max_size_climate_cb,&sc
    };
    if(colony_id == -1) {
        int32_t cap=0;
        if(moo2_v131_derived_size_climate_race_pop_limit(
             &sc,planet[5],planet[8],player_id,&cap)
             !=MOO2_V131_SIZE_CLIMATE_OK)
            return MOO2_V131_PLANET_MAX_INVALID;
        int32_t signed_ax=(int32_t)(uint16_t)cap;
        if(signed_ax>=32768)signed_ax-=65536;
        const uint8_t *player=ctx->players+(size_t)player_id*0xEA9u;
        if(player[0x11Au]==3u)signed_ax+=5;
        *result=signed_ax;
        return MOO2_V131_PLANET_MAX_OK;
    }
    if(colony_id<0 || (size_t)colony_id>=ctx->colony_count)
        return MOO2_V131_PLANET_MAX_INVALID;
    const uint8_t *colony=ctx->colonies+(size_t)colony_id*0x169u;
    if(colony[6]!=0u) {
        int32_t cap=0;
        if(moo2_v131_derived_size_climate_race_pop_limit(
             &sc,planet[5],planet[8],player_id,&cap)
             !=MOO2_V131_SIZE_CLIMATE_OK)
            return MOO2_V131_PLANET_MAX_INVALID;
        int32_t signed_ax=(int32_t)(uint16_t)cap;
        if(signed_ax>=32768)signed_ax-=65536;
        const uint8_t *player=ctx->players+(size_t)player_id*0xEA9u;
        if(player[0x11Au]==3u)signed_ax+=5;
        *result=signed_ax;
        return MOO2_V131_PLANET_MAX_OK;
    }
    const size_t count=colony[0x0Au];
    if(count>42u)return MOO2_V131_PLANET_MAX_INVALID;
    if(count==0u) {
        int32_t cap=0;
        if(moo2_v131_derived_colony_race_pop_limit(
            &rc,colony,0x169u,player_id,&cap)
            !=MOO2_V131_RACELIMIT_OK)
            return MOO2_V131_PLANET_MAX_INVALID;
        int32_t signed_ax=(int32_t)(uint16_t)cap;
        *result=signed_ax>=32768?signed_ax-65536:signed_ax;
        return MOO2_V131_PLANET_MAX_OK;
    }
    uint8_t seen[10]={0};
    for(size_t i=count;i>0u;i--) {
        const uint8_t tag=(uint8_t)(colony[0x0Cu+(i-1u)*4u]&0x0Fu);
        if(tag>=10u)return MOO2_V131_PLANET_MAX_INVALID;
        seen[tag]=1u;
    }
    int32_t maximum=0;
    for(int type=9;type>=1;type--) {
        if(seen[type]==0u)continue;
        int32_t cap=0;
        if(moo2_v131_derived_colony_race_pop_limit(
            &rc,colony,0x169u,(int16_t)type,&cap)
            !=MOO2_V131_RACELIMIT_OK)
            return MOO2_V131_PLANET_MAX_INVALID;
        int32_t signed_ax=(int32_t)(uint16_t)cap;
        if(signed_ax>=32768)signed_ax-=65536;
        if(maximum<signed_ax)maximum=signed_ax;
    }
    *result=maximum;
    return MOO2_V131_PLANET_MAX_OK;
}
