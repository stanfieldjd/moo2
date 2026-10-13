/* Exhaustive original-code-derived player statistic write regression. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/colony_hit_player_stats_v131.c"
static void must(int v){if(!v){fputs("FAIL hit owner statistics\n",stderr);exit(1);}}
static uint16_t rd(const uint8_t *p){return (uint16_t)(p[0]|((uint16_t)p[1]<<8));}
static void wr(uint8_t *p,uint16_t n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
int main(void){
    uint8_t players[3u*0xEA9u]={0};
    uint8_t colony[0x169]={0},event[0x49]={0};
    for(unsigned owner=0;owner<3;owner++)for(unsigned opponent=0;opponent<16;opponent++){
        colony[0]=(uint8_t)owner;event[0]=(uint8_t)opponent;
        uint8_t *stat=players+(size_t)owner*0xEA9u+0x6ffu+2u*opponent;
        for(uint32_t v=0;v<=0xffffu;v++){
            wr(stat,(uint16_t)v);
            must(!moo2_v131_derived_colony_hit_owner_stat(
                players,sizeof(players),colony,sizeof(colony),event,sizeof(event),
                MOO2_V131_OWNER_STAT_INCREMENT_ONE));
            must(rd(stat)==(uint16_t)(v+1u));
            wr(stat,(uint16_t)v);
            must(!moo2_v131_derived_colony_hit_owner_stat(
                players,sizeof(players),colony,sizeof(colony),event,sizeof(event),
                MOO2_V131_OWNER_STAT_INCREMENT_TEN));
            must(rd(stat)==(uint16_t)(v+10u));
        }
    }
    colony[0]=255u;event[0]=0u;
    must(moo2_v131_derived_colony_hit_owner_stat(
        players,sizeof(players),colony,sizeof(colony),event,sizeof(event),
        MOO2_V131_OWNER_STAT_INCREMENT_ONE)==MOO2_V131_OWNER_STAT_INVALID);
    colony[0]=0u;event[0]=255u;
    must(moo2_v131_derived_colony_hit_owner_stat(
        players,sizeof(players),colony,sizeof(colony),event,sizeof(event),
        MOO2_V131_OWNER_STAT_INCREMENT_ONE)==MOO2_V131_OWNER_STAT_INVALID);
    colony[0]=10u;event[0]=0u;
    must(moo2_v131_derived_colony_hit_owner_stat(
        players,sizeof(players),colony,sizeof(colony),event,sizeof(event),
        MOO2_V131_OWNER_STAT_INCREMENT_TEN)==MOO2_V131_OWNER_STAT_INVALID);
    puts("PASS 3 owners x16 opponents x65536 WORDs, +1 and +10 original hit-stat writes");
    return 0;
}
