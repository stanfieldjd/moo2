/*
 * Building IDs 15,23,24,28 original code chain:
 * Remove_Building_ -> source product44 queue purge ->
 * Colony_Environmental_Stuff_ -> Colony_Food2_Per_Farmer_
 * -> Enforce_Population_Limits_At_Colony_
 * -> Colony_Race_Pop_Limit_ -> optional food flag rewriting.
 * Fully recovered original Size_And_Climate_Race_Pop_Limit_,
 * Random_ and Shuffle_Int_ run in the same original population
 * limit chain. The downstream Colony_Calculation_ remains an
 * original named callback, not reconstructed in this test.
 * Colony_Calculation_ remains an explicit named callback.
 * No DOS differential execution or guessed gameplay movement.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/remove_building_environment_v131.c"
#include "../decompilation/reconstructed/colony_environmental_stuff_v131.c"
#include "../decompilation/reconstructed/colony_food_per_farmer_v131.c"
#include "../decompilation/reconstructed/colony_race_pop_limit_v131.c"
#include "../decompilation/reconstructed/enforce_population_limits_v131.c"
#include "../decompilation/reconstructed/random_shuffle_population_v131.c"
#include "../decompilation/reconstructed/size_climate_pop_limit_v131.c"

static void check(int good){
    if(!good){fputs("FAIL full environment/population building chain\n",stderr);exit(1);}
}
static void w16(uint8_t *p,int32_t value){
    uint16_t n=(uint16_t)value;p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);
}
static void w32(uint8_t *p,uint32_t value){
    for(unsigned i=0;i<4u;i++)p[i]=(uint8_t)(value>>(8u*i));
}
typedef struct {
    Moo2V131FoodContext food;
    Moo2V131RaceLimitContext race;
    Moo2V131ColonyEnvironmentContext environment;
    Moo2V131PopLimitContext population;
    uint8_t *colony;
    uint8_t colony_index;
    uint8_t original_building;
    Moo2V131SizeClimateContext size_climate;
    uint32_t rng_seed;
    unsigned sequence,env_food_calls,limits_food_calls,shuffle_calls,
             cap_calls;
} Harness;

static int16_t env_food(void *opaque,uint8_t *colony,
                        int32_t owner,int32_t ebx_zero) {
    Harness *h=(Harness*)opaque;
    check(h->sequence==1u && colony==h->colony && owner==3 &&
          ebx_zero==0);
    uint32_t val=UINT32_MAX;
    check(moo2_v131_derived_colony_food_per_farmer(
        &h->food,colony,0x169u,(int16_t)owner,NULL,0,&val)
        ==MOO2_V131_FOOD_OK);
    h->env_food_calls++;
    return (int16_t)(uint16_t)val;
}
static int size_climate(void *opaque,uint8_t size,uint8_t climate,
                        int16_t race,int32_t *base) {
    Harness *h=(Harness*)opaque;
    check(h->sequence==2u && size==2u && race==3 &&
          climate==h->colony[0xe2u]);
    h->cap_calls++;
    return moo2_v131_derived_size_climate_race_pop_limit(
        &h->size_climate,size,climate,race,base)
        ==MOO2_V131_SIZE_CLIMATE_OK;
}
static int population_cap(void *opaque,const uint8_t *colony,
                          uint8_t type,int16_t *cap){
    Harness *h=(Harness*)opaque;
    check(type==3u && colony==h->colony && h->sequence==2u);
    int32_t result=INT32_MIN;
    check(moo2_v131_derived_colony_race_pop_limit(
        &h->race,colony,0x169u,(int16_t)type,&result)
        ==MOO2_V131_RACELIMIT_OK);
    check(result>=0 && result<42);
    *cap=(int16_t)result;
    return 1;
}
static int shuffle(void *opaque,uint8_t *array,size_t count,size_t stride) {
    Harness *h=(Harness*)opaque;
    check(h->sequence==2u && array==h->colony+0x0cu &&
          count==7u && stride==4u);
    h->shuffle_calls++;
    return moo2_v131_derived_shuffle_int(
        &h->rng_seed,array,count,stride)==MOO2_V131_SHUFFLE_OK;
}
static int population_food(void *opaque,uint8_t *colony,
                           int8_t owner,int16_t *result){
    Harness *h=(Harness*)opaque;
    check(h->sequence==2u && colony==h->colony && owner==3);
    uint32_t output=0u;
    check(moo2_v131_derived_colony_food_per_farmer(
        &h->food,colony,0x169u,owner,NULL,0,&output)
        ==MOO2_V131_FOOD_OK);
    *result=(int16_t)(uint16_t)output;
    h->limits_food_calls++;
    return 1;
}
static int environmental(void *opaque,uint8_t *colony) {
    Harness *h=(Harness*)opaque;
    check(h->sequence==0u && colony==h->colony);
    check(colony[0x136u+h->original_building]==0u);
    h->sequence++;
    return moo2_v131_derived_colony_environmental(
        &h->environment,colony,0x169u)==MOO2_V131_COLONY_ENV_OK;
}
static int population(void *opaque,uint8_t *colony) {
    Harness *h=(Harness*)opaque;
    check(h->sequence==1u && colony==h->colony &&
          h->env_food_calls==1u);
    h->sequence++;
    return moo2_v131_derived_enforce_population_limits(
        &h->population,colony,0x169u)==MOO2_V131_POPLIMIT_OK;
}
static int calculation(void *opaque,int16_t index) {
    Harness *h=(Harness*)opaque;
    check(h->sequence==2u && index==h->colony_index);
    check(h->limits_food_calls==1u && h->cap_calls==1u &&
          h->shuffle_calls==1u);
    h->sequence++;
    return 1;
}
int main(void) {
    uint8_t colonies[2u*0x169u]={0},planets[2u*0x11u]={0},
            players[8u*0xea9u]={0};
    Harness h={0};
    h.food=(Moo2V131FoodContext){planets,2,players,8};
    h.size_climate=(Moo2V131SizeClimateContext){players,8};
    h.race=(Moo2V131RaceLimitContext){
        planets,2,players,8,size_climate,&h};
    h.environment=(Moo2V131ColonyEnvironmentContext){
        planets,2,env_food,&h};
    h.population=(Moo2V131PopLimitContext){
        population_cap,shuffle,population_food,&h};
    Moo2V131BuildingEnvironmentContext ctx={
        colonies,2,planets,2,environmental,population,calculation,&h};
    unsigned scenarios=0u;
    for(unsigned id_index=0;id_index<4u;id_index++)
      for(unsigned planet_state=1u;planet_state<=2u;planet_state++)
      for(unsigned planet_food=0u;planet_food<=1u;planet_food++)
      for(unsigned pop_tech=0u;pop_tech<=1u;pop_tech++){
        memset(colonies,0,sizeof(colonies));
        memset(players,0,sizeof(players));
        uint8_t *colony=colonies+0x169u;
        const unsigned building=id_index==0?15u:
                                id_index==1?23u:id_index==2?24u:28u;
        colony[0]=3u;
        w16(colony+2u,1);
        colony[0x0au]=7u;
        for(unsigned i=0;i<7u;i++)
            w32(colony+0x0cu+i*4u,UINT32_C(0xCDEF0003)|
                            (UINT32_C(0x10000)*i));
        colony[0x136u+15u]=1u; /* owner cap +2 before removal */
        colony[0x14du]=1u;colony[0x14eu]=1u;
        colony[0x136u+28u]=1u;
        planets[0x11u+5u]=2u;
        planets[0x11u+8u]=(uint8_t)planet_state;
        planets[0x11u+0x0bu]=(uint8_t)planet_food;
        players[3u*0xea9u+0x11au]=(uint8_t)(pop_tech?3u:0u);
        h.colony=colony;h.colony_index=1u;
        h.original_building=(uint8_t)building;
        h.rng_seed=UINT32_C(0x12345678);
        h.sequence=h.env_food_calls=h.limits_food_calls=
            h.shuffle_calls=h.cap_calls=0u;
        const int32_t queue[7]={44,-10,8,44,-1,-1,-1};
        for(unsigned i=0;i<7u;i++)w16(colony+0x115u+2u*i,queue[i]);
        size_t removed=999u;
        check(moo2_v131_derived_remove_building_environment(
            &ctx,1,(int16_t)building,&removed)
            ==MOO2_V131_BUILDING_ENV_OK);
        check(h.sequence==3u && h.env_food_calls==1u &&
              h.limits_food_calls==1u && h.shuffle_calls==1u);
        check(h.rng_seed!=UINT32_C(0x12345678));
        check(removed==(building!=15u && planet_state<2u?2u:0u));
        const unsigned capacity=4u+(building==15u?0u:2u)+
                             (pop_tech?5u:0u);
        const unsigned expected=capacity<7u?capacity:7u;
        check(colony[0x0au]==expected);
        for(unsigned i=0;i<expected;i++){
            uint32_t record=moo2_v131_pop_load(colony+0x0cu+i*4u);
            check((record&0xfu)==3u);
            check((record&0x180u)==(planet_food?0u:0x80u));
        }
        check(colony[0xe0u]==(planet_food?255u:0u));
        check(colony[0xe2u]==2u); /* original other climate prerequisite remains */
        scenarios++;
    }
    printf("PASS %u source-backed building->queue->environment->food->race-limit->population-limit cases, original seeded RNG/shuffle\n",scenarios);
    return 0;
}
