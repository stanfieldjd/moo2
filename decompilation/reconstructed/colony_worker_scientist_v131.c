/*
 * Original MOO2 1.31 source-derived small productivity functions:
 * Colony_Industry_Per_Worker_ CODE 0xCEC95 (178 bytes)
 * full body SHA256 1e58a5b42e7d04cbc1d412b55ba007dbee502d5f0c257a96890c93d5689d8aa9
 * Colony_Research_Per_Scientist_ CODE 0xCFDC6 (177 bytes)
 * full body SHA256 7d9e54a024e600115cf99d1d299806ceaf74f93c1aa95638a135b97e2efadd14
 * Original EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Source Worker uses mineral table embedded CODE0xCD4B5 [1,2,3,5,8],
 * colony building flags +0x13A(+1),+0x13D(+1),+0x15A(+2),
 * +0x142(+3); player tech BYTE+0x183==3 adds 1.
 * Optional breakdown buffer writes only triggered source offsets.
 * Keep upper 16 bits of EDx after original MOVZX DX,[mineral table].
 *
 * Scientist starts at 3, adds building bonuses colony
 * +0x13A(+1),+0x154(+2),+0x149(+3),+0x159(+1);
 * planet special BYTE+0x0F ==10 (+2), 11 (+5).
 * If optional breakdown present, stat DWORD+0 begins 3,
 * triggered WORD+0x1C8,1FC,1E6,206 and DWORD+0x226
 * additions are exact original instructions.
 *
 * These are source arithmetic reconstructions, not DOS runtime
 * differential tests; invalid host indexes are safely rejected.
 */
#include <stddef.h>
#include <stdint.h>
#include "colony_worker_scientist_v131.h"
static const uint8_t moo2_v131_original_mineral_per_worker[5]={1,2,3,5,8};
static int32_t moo2_v131_ws_s16(const uint8_t *p){
    uint16_t b=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return b<32768u?(int32_t)b:(int32_t)b-65536;
}
static void moo2_v131_ws_w16(uint8_t *p,uint16_t n){
    p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);
}
static void moo2_v131_ws_w32(uint8_t *p,uint32_t n){
    for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8u*i));
}
static uint32_t moo2_v131_ws_r32(const uint8_t *p){
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
          ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
Moo2V131WorkerScientistStatus
moo2_v131_derived_industry_per_worker(
    const Moo2V131WorkerScientistContext *ctx,
    const uint8_t *colony,size_t colony_bytes,int16_t owner,
    uint8_t *stats,size_t stat_bytes,uint32_t *result)
{
    if(!ctx || !ctx->planets || !ctx->players || !colony ||
       colony_bytes<0x169u || !result || owner<0 ||
       (size_t)owner>=ctx->player_count ||
       (stats && stat_bytes<0x20Au))
        return MOO2_V131_WORKER_SCIENTIST_INVALID;
    int32_t planet_id=moo2_v131_ws_s16(colony+2u);
    if(planet_id<0 || (size_t)planet_id>=ctx->planet_count)
        return MOO2_V131_WORKER_SCIENTIST_INVALID;
    const uint8_t *planet=ctx->planets+(size_t)planet_id*0x11u;
    const uint8_t mineral=planet[0x0Au];
    if(mineral>=5u)return MOO2_V131_WORKER_SCIENTIST_INVALID;
    const uint8_t *player=ctx->players+(size_t)owner*0xEA9u;
    uint32_t edx=(uint32_t)((uint32_t)planet_id*17u);
    edx=(edx&UINT32_C(0xFFFF0000))|
        (uint32_t)moo2_v131_original_mineral_per_worker[mineral];
    if(stats) {
        int32_t sign_ext=(int32_t)(int16_t)(uint16_t)edx;
        moo2_v131_ws_w32(stats,(uint32_t)sign_ext);
    }
    if(colony[0x13Au]){edx++;if(stats)moo2_v131_ws_w16(stats+0x1C8u,1);}
    if(colony[0x13Du]){edx++;if(stats)moo2_v131_ws_w16(stats+0x1CEu,1);}
    if(colony[0x15Au]){edx+=2u;if(stats)moo2_v131_ws_w16(stats+0x208u,2);}
    if(colony[0x142u]){edx+=3u;if(stats)moo2_v131_ws_w16(stats+0x1D8u,3);}
    if(player[0x183u]==3u){edx++;if(stats)moo2_v131_ws_w16(stats+0xF0u,1);}
    *result=edx;
    return MOO2_V131_WORKER_SCIENTIST_OK;
}
Moo2V131WorkerScientistStatus
moo2_v131_derived_research_per_scientist(
    const Moo2V131WorkerScientistContext *ctx,
    const uint8_t *colony,size_t colony_bytes,
    uint8_t *stats,size_t stat_bytes,uint32_t *result)
{
    if(!ctx || !ctx->planets || !colony ||
       colony_bytes<0x169u || !result ||
       (stats && stat_bytes<0x22Au))
        return MOO2_V131_WORKER_SCIENTIST_INVALID;
    int32_t planet_id=moo2_v131_ws_s16(colony+2u);
    if(planet_id<0 || (size_t)planet_id>=ctx->planet_count)
        return MOO2_V131_WORKER_SCIENTIST_INVALID;
    const uint8_t *planet=ctx->planets+(size_t)planet_id*0x11u;
    uint32_t total=3u;
    if(stats)moo2_v131_ws_w32(stats,3u);
    if(colony[0x13Au]){total++;if(stats)moo2_v131_ws_w16(stats+0x1C8u,1);}
    if(colony[0x154u]){total+=2u;if(stats)moo2_v131_ws_w16(stats+0x1FCu,2);}
    if(colony[0x149u]){total+=3u;if(stats)moo2_v131_ws_w16(stats+0x1E6u,3);}
    if(colony[0x159u]){total++;if(stats)moo2_v131_ws_w16(stats+0x206u,1);}
    if(planet[0x0Fu]==10u){
        total+=2u;
        if(stats)moo2_v131_ws_w32(stats+0x226u,
                     moo2_v131_ws_r32(stats+0x226u)+2u);
    }else if(planet[0x0Fu]==11u){
        total+=5u;
        if(stats)moo2_v131_ws_w32(stats+0x226u,
                     moo2_v131_ws_r32(stats+0x226u)+5u);
    }
    *result=total;
    return MOO2_V131_WORKER_SCIENTIST_OK;
}
