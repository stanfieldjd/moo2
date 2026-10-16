/*
 * Complete source-derived Watcom MOO2 v1.31 Colony_Food2_Per_Farmer_
 * (136 bytes, original CODE 0xCE03E..0xCE0C5).
 * Authenticated ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Original full 136-byte body SHA256:
 * 6aef5f245db959b949a22eb0cfccd03b65db2c103a18c4dc47f5bbabcf9a04e4.
 *
 * Source takes EAX=colony pointer, EDX=owner (low signed WORD),
 * EBX=NULL or optional breakdown buffer. Original DATA _planet at
 * 0x1b0d4: signed WORD colony+2 -> planet record stride0x11,
 * unsigned BYTE planet+0x0b. Source MOVZX DX, BYTE retains high16
 * of preceding EDX planet_offset and ADD EDX,EDX doubles full
 * register; preserving this value matters to an exact EAX result.
 *
 * If original food low WORD zero, source checks player BYTE+0x134
 * ==3 (player stride 0xEA9), then sets EDX=2.
 * When signed food low WORD is positive:
 *   colony BYTE+0x164 !=0 => add 4 to EDX;
 *   colony BYTE+0x13A !=0 => add 2 to EDX.
 * Optional breakdown buffer receives:
 *   DWORD+0 = signed original initial doubled food WORD;
 *   WORD+0x52=2 for player-tech fallback;
 *   WORD+0x21c=4 for 0x164 bonus;
 *   WORD+0x1c8=2 for 0x13a bonus.
 * Do NOT zero untouched breakdown cells.
 *
 * Host arrays validated before any writes; original DOS code has
 * no comparable bounds protection on malformed colony records.
 */
#include <stddef.h>
#include <stdint.h>
#include "colony_food_per_farmer_v131.h"

static int32_t moo2_v131_food_s16(uint16_t b) {
    return b<32768u?(int32_t)b:(int32_t)b-65536;
}
static void moo2_v131_food_word(uint8_t *p,uint16_t n) {
    p[0]=(uint8_t)n;
    p[1]=(uint8_t)(n>>8);
}
static void moo2_v131_food_dword(uint8_t *p,uint32_t n) {
    for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8u*i));
}
Moo2V131FoodResult moo2_v131_derived_colony_food_per_farmer(
    const Moo2V131FoodContext *ctx,
    const uint8_t *colony,size_t colony_bytes,
    int16_t owner,
    uint8_t *stats,size_t stats_bytes,
    uint32_t *source_eax_result)
{
    if(!ctx || !ctx->planets || !ctx->players || !colony ||
       colony_bytes<0x169u || !source_eax_result ||
       owner<0 || (size_t)owner>=ctx->player_count ||
       (stats && stats_bytes<0x21eu))
        return MOO2_V131_FOOD_INVALID;

    uint16_t bits=(uint16_t)(colony[2]|((uint16_t)colony[3]<<8));
    int32_t planet_id=moo2_v131_food_s16(bits);
    if(planet_id<0 || (size_t)planet_id>=ctx->planet_count)
        return MOO2_V131_FOOD_INVALID;
    const uint8_t *planet=ctx->planets+(size_t)planet_id*0x11u;
    const uint8_t *player=ctx->players+(size_t)owner*0xEA9u;

    uint32_t edx=(uint32_t)((uint32_t)planet_id*17u);
    edx=(edx & UINT32_C(0xFFFF0000))|
        (uint32_t)planet[0x0bu];  /* original MOVZX DX,BYTE */
    edx=edx+edx;                /* original ADD EDX,EDX */
    if(stats) {
        const int32_t base=moo2_v131_food_s16((uint16_t)edx);
        moo2_v131_food_dword(stats,(uint32_t)base);
    }
    if((uint16_t)edx==0u && player[0x134u]==3u) {
        edx=2u;
        if(stats)moo2_v131_food_word(stats+0x52u,2u);
    }
    if(moo2_v131_food_s16((uint16_t)edx)>0) {
        if(colony[0x164u]!=0u) {
            edx+=4u;
            if(stats)moo2_v131_food_word(stats+0x21cu,4u);
        }
        if(colony[0x13au]!=0u) {
            edx+=2u;
            if(stats)moo2_v131_food_word(stats+0x1c8u,2u);
        }
    }
    *source_eax_result=edx;
    return MOO2_V131_FOOD_OK;
}
