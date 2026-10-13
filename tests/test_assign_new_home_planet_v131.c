/*
 * Test entire source-derived 146-byte Assign_New_Home_Planet_ state write.
 * Original DOS input fields: signed EAX owner, signed EDX excluded colony;
 * source reads _NUM_COLONIES signed WORD, scans in descending order.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/assign_new_home_planet_v131.c"

static void verify(int ok){if(!ok){fputs("FAIL original Assign_New_Home_Planet_\\n",stderr);exit(1);}}
static void word(uint8_t *p,uint16_t value){
    p[0]=(uint8_t)value;p[1]=(uint8_t)(value>>8);
}
static uint16_t readword(const uint8_t *p){
    return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}
int main(void) {
    uint8_t colonies[5u*0x169u]={0};
    uint8_t players[3u*0xEA9u]={0};
    for(int i=0;i<5;i++){
        uint8_t *record=colonies+(size_t)i*0x169u;
        record[0]=1u;
        record[0x0Au]=(uint8_t)(i+1);
        word(record+2u,(uint16_t)(100+i));
    }
    uint16_t selected=0;
    verify(moo2_v131_derived_assign_new_home_planet(
        colonies,5u,players,sizeof(players),1,4,&selected)==MOO2_V131_ASSIGN_HOME_OK);
    verify(selected==103u);
    verify(readword(players+0xEA9u+0x29u)==103u);
    /* Earlier colony has smaller population, but equal largest eligible
       ties are resolved in favor of the lower index, since traversal
       decrements index and comparison is >=. */
    colonies[1u*0x169u+0x0Au]=4u;
    verify(moo2_v131_derived_assign_new_home_planet(
        colonies,5u,players,sizeof(players),1,4,&selected)==MOO2_V131_ASSIGN_HOME_OK);
    verify(selected==101u);
    /* Even zero population qualifies once no better candidate exists:
       source initial best is zero and comparison uses >=. */
    for(int i=0;i<5;i++)colonies[(size_t)i*0x169u+0x0Au]=0u;
    verify(moo2_v131_derived_assign_new_home_planet(
        colonies,5u,players,sizeof(players),1,-1,&selected)==MOO2_V131_ASSIGN_HOME_OK);
    verify(selected==100u);
    /* With no eligible owner candidate, player home planet ID is -1. */
    verify(moo2_v131_derived_assign_new_home_planet(
        colonies,5u,players,sizeof(players),2,-1,&selected)==MOO2_V131_ASSIGN_HOME_OK);
    verify(selected==UINT16_MAX && readword(players+2u*0xEA9u+0x29u)==UINT16_MAX);
    verify(moo2_v131_derived_assign_new_home_planet(
        NULL,0u,players,sizeof(players),0,-1,&selected)==MOO2_V131_ASSIGN_HOME_OK);
    verify(selected==UINT16_MAX);

    /* The selected colony's planet ID WORD is copied without conversion. */
    const uint8_t *first=colonies;
    (void)first;
    for(uint32_t planet_id=0;planet_id<=UINT16_MAX;planet_id++){
        word(colonies+2u,(uint16_t)planet_id);
        verify(moo2_v131_derived_assign_new_home_planet(
            colonies,1u,players,sizeof(players),1,-1,&selected)==MOO2_V131_ASSIGN_HOME_OK);
        verify(selected==(uint16_t)planet_id);
        verify(readword(players+0xEA9u+0x29u)==(uint16_t)planet_id);
    }
    /* Exhaustive population comparison & excluded-index choices. */
    for(unsigned a=0;a<256u;a++)for(unsigned b=0;b<256u;b++){
        colonies[0x0Au]=(uint8_t)a;
        colonies[0x169u+0x0Au]=(uint8_t)b;
        word(colonies+2u,0x1234u);
        word(colonies+0x169u+2u,0x5678u);
        verify(moo2_v131_derived_assign_new_home_planet(
            colonies,2u,players,sizeof(players),1,-1,&selected)==MOO2_V131_ASSIGN_HOME_OK);
        verify(selected==(a>=b?0x1234u:0x5678u));
        verify(moo2_v131_derived_assign_new_home_planet(
            colonies,2u,players,sizeof(players),1,0,&selected)==MOO2_V131_ASSIGN_HOME_OK);
        verify(selected==0x5678u);
    }
    verify(moo2_v131_derived_assign_new_home_planet(
        colonies,2u,players,sizeof(players),-1,-1,&selected)==MOO2_V131_ASSIGN_HOME_INVALID);
    verify(moo2_v131_derived_assign_new_home_planet(
        colonies,2u,players,3u,1,-1,&selected)==MOO2_V131_ASSIGN_HOME_INVALID);
    verify(moo2_v131_derived_assign_new_home_planet(
        NULL,2u,players,sizeof(players),1,-1,&selected)==MOO2_V131_ASSIGN_HOME_INVALID);
    puts("PASS: 65536 planet ID WORD values, 65536 population pairs with exclusion, tie-breaking, zero candidate and host bounds");
    return 0;
}
