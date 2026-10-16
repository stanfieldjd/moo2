/* Original source-derived Remove_Building_ ID15/24/28 integrated
 * with actual Colony_Environmental_Stuff_ (108 bytes).
 * Real Enforce_Population_Limits_At_Colony_ and Colony_Calculation_
 * stay explicit order-checking callbacks until their effects are rebuilt.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/colony_environmental_stuff_v131.c"
#include "../decompilation/reconstructed/remove_building_environment_v131.c"
static void require(int yes){
    if(!yes){fputs("FAIL building environmental integration\n",stderr);exit(1);}
}
static void put16(uint8_t *p,int32_t n){
    uint16_t v=(uint16_t)n;p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
static int32_t get16(const uint8_t *p){
    uint16_t v=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return v<32768u?(int32_t)v:(int32_t)v-65536;
}
typedef struct {
    Moo2V131ColonyEnvironmentContext env;
    uint8_t *colony;
    int building_id;
    int colony_id;
    int32_t food_result;
    int32_t environmental_result;
    unsigned stage;
    unsigned food_calls;
} Harness;
static int16_t food(void *opaque,uint8_t *colony,int32_t owner,int32_t zero){
    Harness *h=(Harness*)opaque;
    require(h->stage==1u && colony==h->colony);
    require(owner==2 && zero==0);
    require(colony[0xe2u]==h->environmental_result);
    h->food_calls++;
    return (int16_t)h->food_result;
}
static int environment(void *opaque,uint8_t *colony){
    Harness *h=(Harness*)opaque;
    require(h->stage==0u && colony==h->colony);
    require(colony[0x136u+(unsigned)h->building_id]==0);
    h->stage++;
    return moo2_v131_derived_colony_environmental(
        &h->env,colony,0x169u)==MOO2_V131_COLONY_ENV_OK;
}
static int limits(void *opaque,uint8_t *colony){
    Harness *h=(Harness*)opaque;
    require(h->stage==1u && colony==h->colony);
    require(h->food_calls==1u);
    require(colony[0xe2u]==h->environmental_result);
    require(colony[0xe0u]==(h->food_result==0?0u:255u));
    h->stage++;
    return 1;
}
static int calculation(void *opaque,int16_t colony_id){
    Harness *h=(Harness*)opaque;
    require(h->stage==2u);
    require(colony_id==h->colony_id);
    h->stage++;
    return 1;
}
int main(void){
    uint8_t colonies[2u*0x169u]={0};
    uint8_t planets[2u*0x11u]={0};
    Harness h={0};
    h.env=(Moo2V131ColonyEnvironmentContext){planets,2u,food,&h};
    Moo2V131BuildingEnvironmentContext ctx={
        colonies,2u,planets,2u,environment,limits,calculation,&h
    };
    unsigned cases=0;
    for(unsigned id_index=0;id_index<3u;id_index++)
      for(unsigned planet_status=0;planet_status<4u;planet_status++)
      for(unsigned flags=0;flags<4u;flags++)
      for(unsigned f=0;f<2u;f++) {
        memset(colonies,0,sizeof(colonies));
        uint8_t *colony=colonies+0x169u;
        int16_t building=(int16_t)(id_index==0?15:id_index==1?24:28);
        h.colony=colony;
        h.building_id=building;
        h.colony_id=1;
        h.stage=h.food_calls=0u;
        h.food_result=f?2:0;
        colony[0]=2u;
        colony[0x14du]=(uint8_t)(flags&1u);
        colony[0x14eu]=(uint8_t)(flags&2u);
        colony[0x136u+(unsigned)building]=1u;
        put16(colony+2u,1);
        planets[0x11u+0x08u]=(uint8_t)planet_status;
        h.environmental_result=(int32_t)(planet_status==1u&&flags?2u:planet_status);
        const int32_t q[7]={44,-10,3,44,-1,-1,-1};
        for(unsigned slot=0;slot<7u;slot++)
            put16(colony+0x115u+2u*slot,q[slot]);
        size_t gone=999u;
        require(moo2_v131_derived_remove_building_environment(
            &ctx,1,building,&gone)==MOO2_V131_BUILDING_ENV_OK);
        unsigned purge=building!=15 && planet_status<2u;
        require(gone==(purge?2u:0u));
        require(h.stage==3u && h.food_calls==1u);
        require(colony[0xe2u]==h.environmental_result);
        require(colony[0xe0u]==(f?255u:0u));
        require(get16(colony+0x115u)==(purge?3:44));
        require(colony[0x136u+(unsigned)building]==0);
        cases++;
      }
    printf("PASS %u integrated original building15/24/28 -> production44 purge -> real 108-byte colony environment -> pop/calc boundaries\n",cases);
    return 0;
}
