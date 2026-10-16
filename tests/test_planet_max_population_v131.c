/*
 * Tests full source-derived original 206-byte Planet_Max_Population_
 * for player, integrating original 188-byte size-climate formula
 * and original 81-byte Colony_Race_Pop_Limit_ wrapper.
 * Independent expectations derive directly from verified source
 * lookup weights for controlled planet size2 and climate2.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/size_climate_pop_limit_v131.c"
#include "../decompilation/reconstructed/colony_race_pop_limit_v131.c"
#include "../decompilation/reconstructed/planet_max_population_v131.c"
static void need(int ok) {
    if(!ok){fputs("FAIL original 206-byte Planet_Max_Population_For_Player_\n",stderr);exit(1);}
}
static void w16(uint8_t *p,int32_t value){
    uint16_t u=(uint16_t)value;p[0]=(uint8_t)u;p[1]=(uint8_t)(u>>8);
}
static void w32(uint8_t *p,uint32_t v){
    for(unsigned i=0;i<4u;i++)p[i]=(uint8_t)(v>>(8u*i));
}
static int32_t call(const Moo2V131PlanetMaxPopulationContext *ctx,
                    int16_t player) {
    int32_t output=INT32_MIN;
    need(moo2_v131_derived_planet_max_population_for_player(
        ctx,1u,player,&output)==MOO2_V131_PLANET_MAX_OK);
    return output;
}
int main(void) {
    uint8_t planets[2u*0x11u]={0},colonies[2u*0x169u]={0},
            players[8u*0xea9u]={0};
    Moo2V131PlanetMaxPopulationContext ctx={
        planets,2u,colonies,2u,players,8u};
    uint8_t *planet=planets+0x11u,*colony=colonies;
    w16(colony+2u,1);
    planet[5]=2u;planet[8]=2u;
    colony[0]=2u;colony[0xe2u]=2u;
    unsigned cases=0u;
    /* Uncolonized path applies queried player trait to
       verified base capacity4 and then player +0x11a tech+5. */
    for(unsigned player=0;player<8u;player++)
      for(unsigned trait=0;trait<2u;trait++)
      for(unsigned tech=0;tech<2u;tech++) {
        memset(players,0,sizeof(players));
        w16(planet,-1);
        uint8_t *p=players+(size_t)player*0xea9u;
        p[0x8b6u]=(uint8_t)trait;
        p[0x11au]=(uint8_t)(tech?3u:0u);
        /* size2 max15 x climate2 25%, trait adds 25%.
           Integer nearest: 4 with no trait, 8 with trait. */
        need(call(&ctx,(int16_t)player)==
             (int32_t)((trait?8u:4u)+(tech?5u:0u)));
        cases++;
      }
    /* Colony present but flagged +0x06 uses exactly the same
       uncolonized calculation rather than colony population. */
    w16(planet,0);
    colony[6]=1u;
    memset(players,0,sizeof(players));
    players[3u*0xea9u+0x8b6u]=1u;
    players[3u*0xea9u+0x11au]=3u;
    need(call(&ctx,3)==13); /* trait8+ tech5 */

    /* Established colony with no population delegates to colony
       race-pop limit using queried race BUT tech/building effects
       come from COLONY OWNER player2, not queried player. */
    colony[6]=0u;
    colony[0x0au]=0u;
    colony[0x145u]=1u;
    players[2u*0xea9u+0x11au]=3u;
    for(unsigned race=0;race<8u;race++) {
        players[(size_t)race*0xea9u+0x8b6u]=(uint8_t)(race&1u);
        need(call(&ctx,(int16_t)race)==
             (int32_t)((race&1u?8u:4u)+5u+2u));
        cases++;
    }
    /* Colony with represented races: class 8 always +25%; class
       9 neither has bonus nor player lookup. Scan distinct tags
       9 down to 1 and max source signed AX (not a sum). */
    memset(players,0,sizeof(players));
    colony[0x0au]=3u;
    colony[0x145u]=0u;
    w32(colony+0x0cu,1u);
    w32(colony+0x10u,8u);
    w32(colony+0x14u,9u);
    need(call(&ctx,0)==8);
    players[2u*0xea9u+0x11au]=3u;
    need(call(&ctx,0)==13);
    colony[0x145u]=1u;
    need(call(&ctx,0)==15);
    cases+=3u;
    /* Original descending marked scan excludes type0, so when
       all occupied records are class0 the source maximum is 0. */
    colony[0x0au]=2u;
    w32(colony+0x0cu,0u);
    w32(colony+0x10u,UINT32_C(0xFEDC0010));
    need(call(&ctx,1)==0);
    cases++;
    /* Invalid original low-nibble class >=10 is rejected by C
       host rather than writing past its ten-byte stack bitmap. */
    w32(colony+0x10u,15u);
    int32_t unchanged=777;
    need(moo2_v131_derived_planet_max_population_for_player(
        &ctx,1,1,&unchanged)==MOO2_V131_PLANET_MAX_INVALID);
    need(unchanged==777);
    w16(planet,3);
    need(moo2_v131_derived_planet_max_population_for_player(
        &ctx,1,1,&unchanged)==MOO2_V131_PLANET_MAX_INVALID);
    need(unchanged==777);
    printf("PASS %u original planet max cap branches, player tech, owner tech, represented race maximum and class0 quirk\n",cases);
}
