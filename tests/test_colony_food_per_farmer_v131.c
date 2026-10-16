/*
 * v1.31 complete 136-byte Colony_Food2_Per_Farmer_ host C tests.
 * Verify all BYTE values of base food, bonuses and optional stats,
 * player-tech fallback, and original MOVZX DX preserving EDX high16.
 */
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../decompilation/reconstructed/colony_food_per_farmer_v131.c"
static void yes(int v) {
    if(!v){fputs("FAIL original Colony_Food2_Per_Farmer_\n",stderr);exit(1);}
}
static void w16(uint8_t *p,int32_t n) {
    uint16_t v=(uint16_t)n;p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
static uint32_t r32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void test_one(Moo2V131FoodContext *ctx,uint8_t *colony,
                     uint8_t *planets,uint8_t *players,
                     unsigned base,unsigned bit_flags,unsigned owner)
{
    memset(colony,0,0x169u);
    w16(colony+2u,1);
    const unsigned technology=(bit_flags&1u)!=0;
    const unsigned extra4=(bit_flags&2u)!=0;
    const unsigned extra2=(bit_flags&4u)!=0;
    const unsigned extra_other=(bit_flags&8u)!=0;
    colony[0x164u]=(uint8_t)(extra4?1u:0u);
    colony[0x13au]=(uint8_t)(extra2?1u:0u);
    colony[0x14eu]=(uint8_t)extra_other;
    planets[0x11u+0x0bu]=(uint8_t)base;
    players[(size_t)owner*0xea9u+0x134u]=(uint8_t)(technology?3u:2u);
    uint8_t stats[0x21eu];memset(stats,0xA5,sizeof(stats));
    uint32_t returned=UINT32_MAX;
    yes(moo2_v131_derived_colony_food_per_farmer(
        ctx,colony,sizeof(uint8_t)*0x169u,
        (int16_t)owner,stats,sizeof(stats),&returned)
        ==MOO2_V131_FOOD_OK);
    unsigned first=base*2u;
    unsigned fallback=(base==0u && technology)?2u:0u;
    unsigned result=first+fallback;
    unsigned has_food=(result!=0u);
    if(has_food) {
        if(extra4)result+=4u;
        if(extra2)result+=2u;
    }
    yes(returned==result);
    yes(r32(stats)==first);
    /* Verify untouched breakdown bytes were not spuriously zeroed. */
    uint8_t expected[sizeof(stats)];memset(expected,0xA5,sizeof(expected));
    for(unsigned i=0;i<4u;i++)
        expected[i]=(uint8_t)(first>>(8u*i));
    if(fallback)w16(expected+0x52u,2);
    if(has_food && extra4)w16(expected+0x21cu,4);
    if(has_food && extra2)w16(expected+0x1c8u,2);
    yes(!memcmp(stats,expected,sizeof(stats)));
    uint32_t no_stats=0;
    yes(moo2_v131_derived_colony_food_per_farmer(
        ctx,colony,0x169u,(int16_t)owner,NULL,0,&no_stats)
        ==MOO2_V131_FOOD_OK);
    yes(no_stats==result);
}
int main(void) {
    uint8_t colony[0x169u]={0};
    uint8_t planets[2u*0x11u]={0};
    uint8_t players[8u*0xea9u]={0};
    Moo2V131FoodContext ctx={planets,2u,players,8u};
    for(unsigned owner=0;owner<8u;owner++)
      for(unsigned base=0;base<256u;base++)
        for(unsigned flags=0;flags<16u;flags++)
            test_one(&ctx,colony,planets,players,base,flags,owner);

    /* Unmodified high16 from original EDX planet-record product. */
    uint8_t big_planets[4001u*0x11u]={0};
    ctx.planets=big_planets;
    ctx.planet_count=4001u;
    w16(colony+2u,4000);
    big_planets[4000u*0x11u+0x0bu]=1u;
    colony[0x164u]=colony[0x13au]=0u;
    uint32_t outcome=0u;
    yes(moo2_v131_derived_colony_food_per_farmer(
        &ctx,colony,0x169u,1,NULL,0,&outcome)
        ==MOO2_V131_FOOD_OK);
    yes(outcome==UINT32_C(0x20002));

    /* Host validation is pre-write; wrong player or insufficient
       stats buffer does not mutate original-format game state. */
    uint8_t tiny[4]={1,2,3,4};
    yes(moo2_v131_derived_colony_food_per_farmer(
        &ctx,colony,0x169u,-1,tiny,sizeof(tiny),&outcome)
        ==MOO2_V131_FOOD_INVALID);
    yes(moo2_v131_derived_colony_food_per_farmer(
        &ctx,colony,0x169u,0,tiny,sizeof(tiny),&outcome)
        ==MOO2_V131_FOOD_INVALID);
    yes(tiny[0]==1u && tiny[1]==2u && tiny[2]==3u && tiny[3]==4u);
    puts("PASS original full colony food: 32768 base/owner/bonus variants, full optional breakdown, 32-bit high-word case");
    return 0;
}
