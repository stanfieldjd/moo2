/*
 * Original-source composed environmental calculation:
 * Remove_Building_(15/23/24/28) -> product44 queue deletion ->
 * Colony_Environmental_Stuff_ -> Colony_Food2_Per_Farmer_
 * Full recovered Watcom function arithmetic, no fake food result.
 * Population limit and colony calculation remain named callbacks.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/remove_building_environment_v131.c"
#include "../decompilation/reconstructed/colony_environmental_stuff_v131.c"
#include "../decompilation/reconstructed/colony_food_per_farmer_v131.c"
static void must(int good) {
    if(!good){fputs("FAIL v1.31 real food and building environment integration\n",stderr);exit(1);}
}
static void put16(uint8_t *p,int32_t v){
    uint16_t x=(uint16_t)v;p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8);
}
static int32_t read16(const uint8_t *p){
    uint16_t b=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return b<32768u?(int32_t)b:(int32_t)b-65536;
}
typedef struct {
    Moo2V131FoodContext food;
    Moo2V131ColonyEnvironmentContext env;
    uint8_t *colony;
    int16_t id;
    int16_t building;
    unsigned stage;
    unsigned food_calls;
    uint8_t expected_environment;
    uint8_t expected_farm_food;
} Fixture;
static int16_t real_food(void *opaque,uint8_t *colony,
                         int32_t signed_owner,int32_t zero) {
    Fixture *f=(Fixture*)opaque;
    must(f->stage==1u && signed_owner>=0 && zero==0);
    must(colony==f->colony);
    must(colony[0xe2u]==f->expected_environment);
    uint32_t eax_result=0u;
    must(moo2_v131_derived_colony_food_per_farmer(
        &f->food,colony,0x169u,(int16_t)signed_owner,
        NULL,0,&eax_result)==MOO2_V131_FOOD_OK);
    must((uint8_t)eax_result==f->expected_farm_food);
    f->food_calls++;
    return (int16_t)(uint16_t)eax_result;
}
static int environmental(void *opaque,uint8_t *colony) {
    Fixture *f=(Fixture*)opaque;
    must(f->stage==0u && colony==f->colony);
    must(colony[0x136u+(unsigned)f->building]==0u);
    f->stage++;
    return moo2_v131_derived_colony_environmental(
        &f->env,colony,0x169u)==MOO2_V131_COLONY_ENV_OK;
}
static int population(void *opaque,uint8_t *colony){
    Fixture *f=(Fixture*)opaque;
    must(f->stage==1u && f->food_calls==1u && colony==f->colony);
    must(colony[0xe2u]==f->expected_environment);
    must(colony[0xe0u]==(f->expected_farm_food?255u:0u));
    f->stage++;
    return 1;
}
static int calculation(void *opaque,int16_t id) {
    Fixture *f=(Fixture*)opaque;
    must(f->stage==2u && id==f->id);
    f->stage++;
    return 1;
}
int main(void) {
    uint8_t colonies[2u*0x169u]={0};
    uint8_t planets[2u*0x11u]={0};
    uint8_t players[8u*0xEA9u]={0};
    Fixture f={0};
    f.food=(Moo2V131FoodContext){planets,2u,players,8u};
    f.env=(Moo2V131ColonyEnvironmentContext){planets,2u,real_food,&f};
    Moo2V131BuildingEnvironmentContext ctx={
        colonies,2u,planets,2u,environmental,population,calculation,&f
    };
    unsigned tests=0;
    for(unsigned owner=0;owner<8;owner++)
      for(unsigned variant=0;variant<4;variant++)
      for(unsigned planet_type=0;planet_type<3;planet_type++)
      for(unsigned planet_food=0;planet_food<2;planet_food++)
      for(unsigned player_tech=0;player_tech<2;player_tech++)
      for(unsigned bits=0;bits<4;bits++)
      for(unsigned prerequisites=0;prerequisites<4;prerequisites++) {
        memset(colonies,0,sizeof(colonies));
        memset(players,0,sizeof(players));
        uint8_t *colony=colonies+0x169u;
        int16_t building=(int16_t)(variant==0?15:
                         variant==1?23:variant==2?24:28);
        f.colony=colony;
        f.building=building;
        f.id=1;
        f.stage=f.food_calls=0u;
        colony[0]=(uint8_t)owner;
        put16(colony+2u,1);
        colony[0x136u+(unsigned)building]=1u;
        colony[0x14du]=(uint8_t)(prerequisites&1u);
        colony[0x14eu]=(uint8_t)((prerequisites&2u)?1u:0u);
        colony[0x164u]=(uint8_t)(bits&1u);
        colony[0x13au]=(uint8_t)(bits&2u);
        planets[0x11u+8u]=(uint8_t)planet_type;
        planets[0x11u+0x0bu]=(uint8_t)planet_food;
        players[(size_t)owner*0xEA9u+0x134u]=(uint8_t)(player_tech?3u:0u);
        unsigned remaining=(unsigned)(
            ((prerequisites&1u)!=0u && building!=23) ||
            ((prerequisites&2u)!=0u && building!=24));
        f.expected_environment=(uint8_t)(planet_type==1u &&
                          remaining?2u:planet_type);
        uint32_t food_value=planet_food*2u;
        if(food_value==0u && player_tech)food_value=2u;
        if(food_value!=0u) {
            if(bits&1u)food_value+=4u;
            if(bits&2u)food_value+=2u;
        }
        f.expected_farm_food=(uint8_t)food_value;
        const int q[7]={44,44,-10,8,-1,-1,-1};
        for(unsigned i=0;i<7u;i++)
            put16(colony+0x115u+2u*i,q[i]);
        size_t count=0;
        must(moo2_v131_derived_remove_building_environment(
            &ctx,1,building,&count)==MOO2_V131_BUILDING_ENV_OK);
        must(count==(building!=15&&planet_type<2u?2u:0u));
        must(read16(colony+0x115u)==
             (building!=15&&planet_type<2u?8:44));
        must(f.stage==3u && f.food_calls==1u);
        must(colony[0xe2u]==f.expected_environment);
        must(colony[0xe0u]==(food_value!=0u?255u:0u));
        tests++;
      }
    printf("PASS %u original building15/23/24/28 -> queue -> environmental -> full original food calculations\n",tests);
    return 0;
}
