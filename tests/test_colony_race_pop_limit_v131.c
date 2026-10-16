/* Original 81-byte Colony_Race_Pop_Limit_ 0xD0C1D source tests.
 * Size_And_Climate_Race_Pop_Limit_ is external callback, not invented.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/colony_race_pop_limit_v131.c"
static void yes(int ok){
    if(!ok){fputs("FAIL original race-population limit wrapper\n",stderr);exit(1);}
}
typedef struct {
    int32_t base_result;
    uint8_t expected_size,expected_climate;
    int16_t expected_race;
    unsigned calls;
    unsigned fail;
} Fixture;
static int base(void *opaque,uint8_t size,uint8_t climate,
                int16_t race,int32_t *result) {
    Fixture *f=(Fixture*)opaque;
    yes(size==f->expected_size && climate==f->expected_climate);
    yes(race==f->expected_race && result);
    f->calls++;
    if(f->fail)return 0;
    *result=f->base_result;
    return 1;
}
static void word(uint8_t *p,int16_t n) {
    uint16_t v=(uint16_t)n;p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
int main(void) {
    uint8_t colony[0x169u]={0};
    uint8_t planets[2u*0x11u]={0};
    uint8_t players[8u*0xea9u]={0};
    Fixture f={0};
    Moo2V131RaceLimitContext ctx={planets,2,players,8,base,&f};
    unsigned cases=0u;
    for(unsigned owner=0;owner<8u;owner++)
      for(unsigned type=0;type<10u;type++)
      for(unsigned tech=0;tech<4u;tech++)
      for(unsigned building=0;building<2u;building++)
      for(unsigned i=0;i<4u;i++) {
        memset(colony,0,sizeof(colony));
        memset(players,0,sizeof(players));
        colony[0]=(uint8_t)owner;
        word(colony+2u,1);
        planets[0x11u+0x05u]=(uint8_t)(i*2u);
        colony[0xe2u]=(uint8_t)(i+1u);
        colony[0x145u]=(uint8_t)building;
        players[(size_t)owner*0xea9u+0x11au]=(uint8_t)tech;
        f.expected_size=(uint8_t)(i*2u);
        f.expected_climate=(uint8_t)(i+1u);
        f.expected_race=(int16_t)type;
        f.base_result=(int32_t)(i==3u ? 0x12340002 : i*7u);
        f.calls=0u;
        int32_t result=INT32_MIN;
        yes(moo2_v131_derived_colony_race_pop_limit(
           &ctx,colony,sizeof(colony),(int16_t)type,&result)
           ==MOO2_V131_RACELIMIT_OK);
        yes(result==(int32_t)((i==3u?2u:i*7u)+
                 (tech==3u?5u:0u)+(building?2u:0u)));
        yes(f.calls==1u);
        cases++;
      }
    /* Original CWDE after callback discards high16 and sign extends. */
    f.expected_size=6u;f.expected_climate=4u;
    f.expected_race=1;f.base_result=UINT32_C(0x0000FFFE);
    colony[0]=0u;word(colony+2u,1);
    colony[0xe2u]=4u;colony[0x145u]=0;
    players[0x11Au]=0;
    int32_t result=0;
    yes(moo2_v131_derived_colony_race_pop_limit(
       &ctx,colony,sizeof(colony),1,&result)==MOO2_V131_RACELIMIT_OK);
    yes(result==-2);
    f.fail=1u;
    yes(moo2_v131_derived_colony_race_pop_limit(
       &ctx,colony,sizeof(colony),1,&result)
       ==MOO2_V131_RACELIMIT_CALLBACK_FAILED);
    f.fail=0u;
    word(colony+2u,-1);
    yes(moo2_v131_derived_colony_race_pop_limit(
       &ctx,colony,sizeof(colony),1,&result)
       ==MOO2_V131_RACELIMIT_INVALID);
    printf("PASS %u original owner/race/planet/tech/building population-limit cases and CWDE behavior\n",cases);
    return 0;
}
