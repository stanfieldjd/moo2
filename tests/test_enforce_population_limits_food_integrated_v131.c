/*
 * Source-derived original 489-byte population-limit routine
 * integrated with authentic 136-byte Colony_Food2_Per_Farmer_.
 * Race pop limits and Shuffle_ remain explicit deterministic
 * fixtures, rather than guessed capacity or randomness.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/colony_food_per_farmer_v131.c"
#include "../decompilation/reconstructed/enforce_population_limits_v131.c"
static void verify(int ok) {
    if(!ok){fputs("FAIL original population limit + food integration\n",stderr);exit(1);}
}
static void w16(uint8_t *p,int32_t n) {
    uint16_t k=(uint16_t)n;p[0]=(uint8_t)k;p[1]=(uint8_t)(k>>8);
}
static void w32(uint8_t *p,uint32_t n) {
    for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8u*i));
}
typedef struct {
    Moo2V131FoodContext food_source;
    unsigned limits_called,shuffles_called,food_called;
    int16_t cap;
} Fixture;
static int limit(void *opaque,const uint8_t *colony,
                 uint8_t type,int16_t *max_pop) {
    Fixture *f=(Fixture*)opaque;
    verify(colony[0]==3 && type<10u);
    f->limits_called++;
    *max_pop=f->cap;
    return 1;
}
static int shuffle(void *opaque,uint8_t *p,size_t count,size_t stride) {
    Fixture *f=(Fixture*)opaque;
    verify(p && count<=42 && stride==4u);
    f->shuffles_called++;
    return 1; /* controlled identity permutation fixture */
}
static int food(void *opaque,uint8_t *colony,
                int8_t owner,int16_t *result) {
    Fixture *f=(Fixture*)opaque;
    verify(owner==3);
    f->food_called++;
    uint32_t value=UINT32_MAX;
    verify(moo2_v131_derived_colony_food_per_farmer(
        &f->food_source,colony,0x169u,owner,NULL,0,&value)
        ==MOO2_V131_FOOD_OK);
    *result=(int16_t)(uint16_t)value;
    return 1;
}
int main(void) {
    uint8_t colony[0x169u]={0};
    uint8_t planets[0x11u]={0};
    uint8_t players[8u*0xea9u]={0};
    Fixture fixture={{planets,1,players,8},0,0,0,41};
    Moo2V131PopLimitContext pop={limit,shuffle,food,&fixture};
    unsigned cases=0u;
    for(unsigned base=0;base<4u;base++)
      for(unsigned tech=0;tech<2u;tech++)
      for(unsigned bonuses=0;bonuses<4u;bonuses++)
      for(unsigned n=1;n<=10u;n++) {
        memset(colony,0,sizeof(colony));
        memset(players,0,sizeof(players));
        colony[0]=3u;
        w16(colony+2u,0);
        colony[0x0au]=(uint8_t)n;
        colony[0x164u]=(uint8_t)(bonuses&1u);
        colony[0x13au]=(uint8_t)(bonuses&2u);
        planets[0x0bu]=(uint8_t)base;
        players[3u*0xea9u+0x134u]=(uint8_t)(tech?3u:0u);
        fixture.cap=41;
        fixture.limits_called=fixture.shuffles_called=fixture.food_called=0u;
        for(unsigned i=0;i<n;i++) {
            uint32_t v=UINT32_C(0xBCDA0000)|((i%3u)==0u?8u:3u);
            w32(colony+0x0cu+4u*i,v);
        }
        verify(moo2_v131_derived_enforce_population_limits(
            &pop,colony,sizeof(colony))==MOO2_V131_POPLIMIT_OK);
        verify(colony[0x0au]==n);
        verify(fixture.shuffles_called==1 && fixture.food_called==1);
        verify(fixture.limits_called==2);
        int no_food=base==0u && tech==0u;
        for(unsigned i=0;i<n;i++) {
            uint32_t v=moo2_v131_pop_load(colony+0x0cu+4u*i);
            unsigned type=(i%3u)==0u?8u:3u;
            uint32_t expected=UINT32_C(0xBCDA0000)|type;
            if(no_food && type!=8u)expected|=0x80u;
            verify(v==expected);
        }
        cases++;
    }
    /* Fixed capacity 2, four type3 entries: source must cap to2
       before executing original full food and postfood flag sweep. */
    memset(colony,0,sizeof(colony));memset(players,0,sizeof(players));
    colony[0]=3u;w16(colony+2u,0);
    colony[0x0au]=4u;fixture.cap=2;
    planets[0x0bu]=0u;
    for(unsigned i=0;i<4;i++)
        w32(colony+0x0cu+i*4u,UINT32_C(0x01000003)+i*UINT32_C(0x10000));
    verify(moo2_v131_derived_enforce_population_limits(
        &pop,colony,sizeof(colony))==MOO2_V131_POPLIMIT_OK);
    verify(colony[0x0au]==2u);
    for(unsigned i=0;i<2;i++)
        verify((moo2_v131_pop_load(colony+0x0cu+i*4u)&UINT32_C(0x180))==0x80u);
    printf("PASS %u integrated original food+population states with exact zero-food flags and removal ordering\n",cases);
    return 0;
}
