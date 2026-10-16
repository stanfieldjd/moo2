/*
 * Source-derived tests of complete original 65-byte
 * Colony_Calculation_ call routing. The original 198-byte
 * Pre_Import_Computing_, 1238-byte Pass_Out_Imports_ and 864-byte
 * Update_Player_Stats_ are explicit independent callback boundaries.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/colony_calculation_dispatch_v131.c"
static void require(int yes) {
    if(!yes){fputs("FAIL original colony calculation dispatch\n",stderr);exit(1);}
}
typedef struct {
    uint8_t *colony,*players;
    unsigned stage,pre_calls,pass_calls,stat_calls;
    unsigned fail_step,change_pre_owner,change_pass_owner;
} Fixture;
static int pre(void *opaque,uint8_t *colony) {
    Fixture *h=(Fixture*)opaque;
    require(h->stage==0 && h->colony==colony && colony[6u]==0u);
    h->stage=1;
    h->pre_calls++;
    if(h->change_pre_owner)colony[0u]=(uint8_t)((colony[0u]+1u)%8u);
    return h->fail_step!=1u;
}
static int imports(void *opaque,int8_t owner,uint8_t *colony) {
    Fixture *h=(Fixture*)opaque;
    require(h->stage==1u && h->colony==colony);
    require(owner==(int8_t)colony[0]);
    h->stage=2u;h->pass_calls++;
    if(h->change_pass_owner)colony[0u]=(uint8_t)((colony[0u]+1u)%8u);
    return h->fail_step!=2u;
}
static int stats(void *opaque,uint8_t *player) {
    Fixture *h=(Fixture*)opaque;
    require((h->stage==0u || h->stage==2u) &&
            player==h->players+(size_t)h->colony[0]*0xEA9u);
    h->stage=3u;h->stat_calls++;
    return h->fail_step!=3u;
}
int main(void){
    uint8_t colonies[2u*0x169u]={0},players[8u*0xEA9u]={0};
    Fixture h={0};
    Moo2V131ColonyCalculationContext ctx={
        colonies,2,players,8,pre,imports,stats,&h
    };
    unsigned cases=0;
    for(unsigned owner=0;owner<8u;owner++)
      for(unsigned inactive=0;inactive<=1u;inactive++)
      for(unsigned change_pre=0;change_pre<=1u;change_pre++)
      for(unsigned change_pass=0;change_pass<=1u;change_pass++) {
        memset(colonies,0,sizeof(colonies));
        uint8_t *colony=colonies+0x169u;
        colony[0u]=(uint8_t)owner;
        colony[6u]=(uint8_t)inactive;
        h=(Fixture){0};h.colony=colony;h.players=players;
        h.change_pre_owner=change_pre;
        h.change_pass_owner=change_pass;
        require(moo2_v131_derived_colony_calculation(
            &ctx,1)==MOO2_V131_COLONYCALC_OK);
        require(h.stat_calls==1u && h.stage==3u);
        require(h.pre_calls==(inactive?0u:1u));
        require(h.pass_calls==(inactive?0u:1u));
        if(!inactive)require(colony[0]==
            (uint8_t)((owner+change_pre+change_pass)%8u));
        else require(colony[0]==owner);
        cases++;
      }
    /* Source callback failure boundaries and no fictitious rollback. */
    for(unsigned fail=1u;fail<=3u;fail++){
        memset(colonies,0,sizeof(colonies));
        h=(Fixture){0};h.colony=colonies;h.players=players;
        h.fail_step=fail;colonies[0]=2u;
        require(moo2_v131_derived_colony_calculation(
            &ctx,0)==MOO2_V131_COLONYCALC_CALLEE_FAILED);
        require(h.stage==fail);
    }
    /* Original inactive route does not invoke original production
       callbacks even if those would report failures. */
    memset(colonies,0,sizeof(colonies));
    h=(Fixture){0};h.colony=colonies;h.players=players;
    h.fail_step=1u;colonies[0]=1u;colonies[6]=1u;
    require(moo2_v131_derived_colony_calculation(
        &ctx,0)==MOO2_V131_COLONYCALC_OK);
    require(h.pre_calls==0u && h.pass_calls==0u && h.stat_calls==1u);
    /* Safe host handling: invalid signed index and invalid owner. */
    require(moo2_v131_derived_colony_calculation(
        &ctx,-1)==MOO2_V131_COLONYCALC_INVALID);
    require(moo2_v131_derived_colony_calculation(
        &ctx,2)==MOO2_V131_COLONYCALC_INVALID);
    colonies[0u]=255u;
    require(moo2_v131_derived_colony_calculation(
        &ctx,0)==MOO2_V131_COLONYCALC_INVALID);
    printf("PASS: %u active/inactive owner routing tests, original owner reloads, 3 downstream failure boundaries\n",cases);
}
