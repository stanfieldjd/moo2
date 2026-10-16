/* Regression based on authenticated original max-population arrays
 * (DATA +0x5806 and CODE +0xCD4EB) and v1.31 race traits.
 * Reference computes independent explicit table values with signed
 * arithmetic, not the function under test's control flow.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/size_climate_pop_limit_v131.c"
static void must(int yes) {
    if(!yes){fputs("FAIL original Size_And_Climate_Race_Pop_Limit_\n",stderr);exit(1);}
}
static const uint8_t climate_ref[16]={
    25,25,25,25,25,25,40,60,80,100,30,60,30,60,60,120
};
static int32_t expected_base(unsigned size,unsigned climate,unsigned bonus) {
    int32_t p=(int32_t)climate_ref[climate]+(bonus?25:0);
    if(p>100)p=100;
    return (int32_t)(((int32_t)(size+1u)*5*p+50)/100);
}
static int32_t expected_race(unsigned size,unsigned climate,
                             unsigned race,unsigned traits) {
    unsigned bonus=race==8u;
    if(race<8u) {
        bonus=(traits&1u)!=0;
        if(traits&2u) {
            if(climate==4u || climate==6u) climate=8u;
            else if(climate==5u || climate==8u) climate=9u;
        }
    }
    int32_t val=expected_base(size,climate,bonus);
    if(race<8u && (traits&4u))val+=(int32_t)(2u*(size+1u));
    return val;
}
int main(void) {
    uint8_t players[8u*0xEA9u]={0};
    Moo2V131SizeClimateContext ctx={players,8};
    unsigned max_tests=0u,race_tests=0u;
    for(unsigned size=0;size<5u;size++)
      for(unsigned climate=0;climate<16u;climate++)
      for(unsigned bonus=0;bonus<=1u;bonus++) {
        int32_t result=INT32_MIN;
        must(moo2_v131_derived_size_climate_max_population(
            (uint8_t)size,(uint8_t)climate,
            (uint8_t)bonus,&result)==MOO2_V131_SIZE_CLIMATE_OK);
        must(result==expected_base(size,climate,bonus));
        max_tests++;
      }

    for(unsigned size=0;size<5u;size++)
      for(unsigned climate=0;climate<16u;climate++)
      for(unsigned race=0;race<10u;race++)
      for(unsigned traits=0;traits<8u;traits++) {
        memset(players,0,sizeof(players));
        if(race<8u) {
            uint8_t *player=players+(size_t)race*0xEA9u;
            player[0x8B6u]=(uint8_t)(traits&1u);
            player[0x8ABu]=(uint8_t)(traits&2u);
            player[0x8ACu]=(uint8_t)(traits&4u);
        }
        int32_t result=INT32_MIN;
        must(moo2_v131_derived_size_climate_race_pop_limit(
            &ctx,(uint8_t)size,(uint8_t)climate,
            (int16_t)race,&result)==MOO2_V131_SIZE_CLIMATE_OK);
        must(result==expected_race(size,climate,race,traits));
        race_tests++;
      }
    /* MaxPop saturation for climate table entry 120, race 8
       receives a full 25% bonus; both clamp to 100. */
    int32_t result=0;
    must(moo2_v131_derived_size_climate_max_population(
        4u,15u,1u,&result)==MOO2_V131_SIZE_CLIMATE_OK);
    must(result==25);
    must(moo2_v131_derived_size_climate_race_pop_limit(
        &ctx,4u,15u,8,&result)==MOO2_V131_SIZE_CLIMATE_OK);
    must(result==25);
    must(moo2_v131_derived_size_climate_race_pop_limit(
        &ctx,4u,15u,9,&result)==MOO2_V131_SIZE_CLIMATE_OK);
    must(result==25);
    /* Bounds rejection and no fabricated output on failure. */
    result=0x12345678;
    must(moo2_v131_derived_size_climate_race_pop_limit(
        &ctx,5u,2u,0,&result)==MOO2_V131_SIZE_CLIMATE_INVALID);
    must(moo2_v131_derived_size_climate_race_pop_limit(
        &ctx,2u,16u,0,&result)==MOO2_V131_SIZE_CLIMATE_INVALID);
    must(moo2_v131_derived_size_climate_race_pop_limit(
        &ctx,2u,2u,-1,&result)==MOO2_V131_SIZE_CLIMATE_INVALID);
    must(moo2_v131_derived_size_climate_race_pop_limit(
        &ctx,2u,2u,10,&result)==MOO2_V131_SIZE_CLIMATE_INVALID);
    must(result==0x12345678);
    printf("PASS original size/climate: %u base lookups, %u player-race-trait combinations, source clamps and invalid bounds\n",
        max_tests,race_tests);
}
