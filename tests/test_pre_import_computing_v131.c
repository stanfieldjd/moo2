/*
 * Regression of original 198-byte Pre_Import_Computing_ with fully
 * recovered food/environment/worker/research numeric subroutines.
 * Original remaining ten production-related named callees are
 * explicit ordered callbacks; no fake economic effects are claimed.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/colony_food_per_farmer_v131.c"
#include "../decompilation/reconstructed/colony_environmental_stuff_v131.c"
#include "../decompilation/reconstructed/colony_worker_scientist_v131.c"
#include "../decompilation/reconstructed/pre_import_computing_v131.c"
#define must(x) do { if(!(x)) {fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);exit(1);} }while(0)
static void put16(uint8_t *p,int n){
    uint16_t v=(uint16_t)n;p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
static int read16(const uint8_t *p){
    uint16_t v=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return v<32768u?v:(int)v-65536;
}
typedef struct {
    uint8_t *colony;
    unsigned next,steps_called,fail_at,replicator_f0;
    int replicator_e9;
    int expected_food,expected_worker,expected_scientist;
    int expected_environment;
} Harness;
static int stage_callback(void *opaque,
    Moo2V131PreImportStage stage,uint8_t *colony)
{
    Harness *h=(Harness*)opaque;
    must(colony==h->colony && (unsigned)stage==h->next);
    must(colony[0xDDu]==h->expected_food);
    must(colony[0xDEu]==h->expected_worker);
    must(colony[0xDFu]==h->expected_scientist);
    must(colony[0xE2u]==h->expected_environment);
    must(colony[0xE0u]==(h->expected_food?255:0));
    if(stage==MOO2_V131_PRE_MORALE)
        for(unsigned i=0;i<4;i++)must(colony[0xEFu+i]==0u);
    if(stage==MOO2_V131_PRE_REPLICATORS) {
       colony[0xF0u]=(uint8_t)h->replicator_f0;
       put16(colony+0xE9u,h->replicator_e9);
    }
    if(stage>=MOO2_V131_PRE_RESEARCH_PRODUCTION) {
        int cmp=(int)h->replicator_f0<h->replicator_e9?
             (int)h->replicator_f0:h->replicator_e9;
        must(read16(colony+0xF5u)==cmp);
    }
    h->next++;h->steps_called++;
    return h->fail_at!=(unsigned)(stage+1);
}
int main(void){
    uint8_t colony[0x169u]={0};
    uint8_t planets[2u*0x11u]={0};
    uint8_t players[8u*0xEA9u]={0};
    Harness h={0};
    Moo2V131PreImportContext ctx={
        planets,2,players,8,stage_callback,&h
    };
    unsigned cases=0;
    const uint8_t mine_lookup[]={1,2,3,5,8};
    for(unsigned food=0;food<3;food++)
    for(unsigned mineral=0;mineral<5;mineral++)
    for(unsigned flags=0;flags<8;flags++)
    for(unsigned planet_special=0;planet_special<3;planet_special++)
    for(unsigned capcase=0;capcase<4;capcase++) {
        memset(colony,0,sizeof(colony));
        memset(players,0,sizeof(players));
        memset(planets,0,sizeof(planets));
        colony[0]=3u;
        put16(colony+2u,1);
        planets[0x11u+0x08u]=1u;
        planets[0x11u+0x0Bu]=(uint8_t)food;
        planets[0x11u+0x0Au]=(uint8_t)mineral;
        planets[0x11u+0x0Fu]=(uint8_t)(planet_special==1?10:
                                    planet_special==2?11:0);
        colony[0x14Du]=1u;
        colony[0x13Au]=(uint8_t)(flags&1u);
        colony[0x13Du]=(uint8_t)(flags&2u);
        colony[0x154u]=(uint8_t)(flags&4u);
        colony[0xEFu]=0xCCu;colony[0xF0u]=0xDDu;
        colony[0xF1u]=0xEEu;colony[0xF2u]=0xFFu;
        h=(Harness){0};
        h.colony=colony;
        h.expected_food=(int)(food==0u?0u:
            food*2u+((flags&1u)?2u:0u));
        h.expected_worker=(int)mine_lookup[mineral]+
             ((flags&1u)?1:0)+((flags&2u)?1:0);
        h.expected_scientist=3+((flags&1u)?1:0)+
             ((flags&4u)?2:0)+(planet_special==1?2:
                               planet_special==2?5:0);
        h.expected_environment=2;
        h.replicator_f0=capcase==0?0u:capcase==1?7u:
                         capcase==2?255u:11u;
        h.replicator_e9=capcase==0?0:capcase==1?3:
                         capcase==2?-1:32000;
        must(moo2_v131_derived_pre_import_computing(
             &ctx,colony,sizeof(colony))==MOO2_V131_PREIMPORT_OK);
        must(h.steps_called==10 && h.next==10);
        must(colony[0xDDu]==h.expected_food &&
             colony[0xDEu]==h.expected_worker &&
             colony[0xDFu]==h.expected_scientist);
        const int expected=(int)h.replicator_f0<h.replicator_e9?
              (int)h.replicator_f0:h.replicator_e9;
        must(read16(colony+0xF5u)==expected);
        cases++;
    }
    /* All ten callback failures must surface after the corresponding
       partial source writes, not fake completion/rollback. */
    for(unsigned fail=1;fail<=10;fail++) {
        memset(colony,0,sizeof(colony));
        memset(players,0,sizeof(players));
        colony[0]=3u;put16(colony+2u,1);
        colony[0x14Du]=1u;
        planets[0x11u+0x0Au]=0u;
        planets[0x11u+0x0Bu]=1u;
        planets[0x11u+0x08u]=1u;
        planets[0x11u+0x0Fu]=0;
        h=(Harness){0};h.colony=colony;h.fail_at=fail;
        h.expected_food=2;h.expected_worker=1;
        h.expected_scientist=3;h.expected_environment=2;
        h.replicator_f0=7;h.replicator_e9=5;
        must(moo2_v131_derived_pre_import_computing(
             &ctx,colony,sizeof(colony))
             ==MOO2_V131_PREIMPORT_PENDING_CALLEE_FAILED);
        must(h.steps_called==fail);
    }
    printf("PASS %u original pre-import numeric/callback sequences plus ten explicit callee failure cases\n",cases);
}
