/*
 * Original source-derived integration:
 *   Remove_Building_(colony ID,9) -> Assign_New_Home_Planet_(owner,excluded ID).
 * Verifies EDX excluded colony matters and building 9 flag cleared before
 * the home-planet update. Neither routine is executed in original DOS here.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/remove_building9_v131.c"
#include "../decompilation/reconstructed/assign_new_home_planet_v131.c"

typedef struct {
    uint8_t *colonies;
    uint8_t *players;
    uint32_t calls;
    uint16_t home_written;
} Harness;
static void must(int ok){if(!ok){fputs("FAIL Remove_Building_9 -> Assign_New_Home_Planet_\\n",stderr);exit(1);}}
static void write16(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static uint16_t read16(const uint8_t *p){return (uint16_t)(p[0]|((uint16_t)p[1]<<8));}
static void assign(void *opaque,int32_t owner,int32_t excluded_id){
    Harness *h=(Harness *)opaque;
    must(excluded_id>=0 && excluded_id<4 && owner==1);
    must(h->colonies+(size_t)excluded_id*0x169u);
    must(h->colonies[(size_t)excluded_id*0x169u+0x13Fu]==0);
    must(moo2_v131_derived_assign_new_home_planet(
        h->colonies,4u,h->players,2u*0xEA9u,
        owner,excluded_id,&h->home_written)==MOO2_V131_ASSIGN_HOME_OK);
    h->calls++;
}
int main(void) {
    uint8_t colonies[4u*0x169u]={0};
    uint8_t players[2u*0xEA9u]={0};
    for(unsigned i=0;i<4u;i++){
        uint8_t *colony=colonies+(size_t)i*0x169u;
        colony[0]=1u;
        colony[0x0Au]=(uint8_t)(i*30u+10u);
        colony[0x13Fu]=1u;
        write16(colony+2u,(uint16_t)(200+i));
    }
    Harness h={colonies,players,0,0};
    /* Colony #3 is the largest; its home removal must choose #2. */
    must(moo2_v131_derived_remove_building9(
        colonies,4u,3,assign,&h)==MOO2_V131_REMOVE_BUILDING9_OK);
    must(h.calls==1u && h.home_written==202u);
    must(read16(players+0xEA9u+0x29u)==202u);
    must(colonies[3u*0x169u+0x13Fu]==0u);
    /* Colony #2 must be excluded next; #3 remains a population contender
       because removing a building does not itself delete its record. */
    must(moo2_v131_derived_remove_building9(
        colonies,4u,2,assign,&h)==MOO2_V131_REMOVE_BUILDING9_OK);
    must(h.calls==2u && h.home_written==203u);
    /* Assign after excluding sole same-player record: home = FFFF. */
    for(unsigned i=0;i<3;i++)colonies[(size_t)i*0x169u]=0u;
    must(moo2_v131_derived_remove_building9(
        colonies,4u,3,assign,&h)==MOO2_V131_REMOVE_BUILDING9_OK);
    must(h.calls==3u && h.home_written==UINT16_MAX);
    must(read16(players+0xEA9u+0x29u)==UINT16_MAX);
    puts("PASS: source-backed building9 flag clear then home-reassignment owner/exclusion integration");
    return 0;
}
