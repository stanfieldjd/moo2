/*
 * Source v1.31 Remove_Building_ IDs15,23,24,28 and product44 queue
 * deletion tests. Downstream environmental/pop/colony subsystems
 * are distinct original named functions, represented by verifying
 * call-order callbacks; no gameplay behavior invented.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/remove_building_environment_v131.c"
static void check(int v) {
    if(!v){fputs("FAIL original building15/24/28 environment\n",stderr);exit(1);}
}
static void word(uint8_t *p,int32_t n) {
    uint16_t v=(uint16_t)n;p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
typedef struct {
    uint8_t *colony;
    int16_t colony_id;
    int16_t building_id;
    unsigned step;
    unsigned fail_at;
} Harness;
static void verify_call(Harness *h,uint8_t *colony,unsigned step) {
    check(colony==h->colony);
    check(h->step==step);
    check(colony[0x136u+(unsigned)h->building_id]==0u);
    h->step++;
}
static int environment(void *opaque,uint8_t *colony) {
    Harness *h=(Harness *)opaque;verify_call(h,colony,0);
    return h->fail_at!=1u;
}
static int limits(void *opaque,uint8_t *colony) {
    Harness *h=(Harness *)opaque;verify_call(h,colony,1);
    return h->fail_at!=2u;
}
static int calculate(void *opaque,int16_t colony_id) {
    Harness *h=(Harness *)opaque;
    check(colony_id==h->colony_id);
    verify_call(h,h->colony,2);
    return h->fail_at!=3u;
}
static void input_queue(uint8_t *p,const int32_t values[7]) {
    for(unsigned i=0;i<7u;i++)
        word(p+0x115u+2u*i,values[i]);
}
static void expected_queue(const uint8_t *p,
                           const int32_t values[7],int purge)
{
    int32_t expected[7];
    unsigned next=0;
    for(unsigned i=0;i<7;i++){
        /* The original repeated first-match deletion only removes
           -10 placeholders if they shift to a 44-deleted slot. This
           fixture places placeholder runs directly after the 44s. */
        if(purge && (values[i]==44 || values[i]==-10))
            continue;
        expected[next++]=values[i];
    }
    for(;next<7;next++)expected[next]=-1;
    for(unsigned i=0;i<7;i++) {
        check(moo2_v131_environment_s16(p+0x115u+2u*i)==expected[i]);
    }
}
int main(void) {
    uint8_t colonies[3u*0x169u]={0};
    uint8_t planets[2u*0x11u]={0};
    const int32_t original[7]={44,-10,44,-100,12,44,-10};
    Harness h={0};
    Moo2V131BuildingEnvironmentContext ctx={
        colonies,3u,planets,2u,environment,limits,calculate,&h
    };
    /* Every original branch and planet byte state. Product44
       removal affects only 24/28 when planet BYTE+8 is 0 or 1. */
    for(unsigned planet_state=0;planet_state<=255u;planet_state++)
      for(unsigned variant=0;variant<4u;variant++)
      for(unsigned colony_id=0;colony_id<3u;colony_id++) {
        int16_t building=(int16_t)(variant==0?15:variant==1?23:variant==2?24:28);
        uint8_t *colony=colonies+(size_t)colony_id*0x169u;
        memset(colonies,0,sizeof(colonies));
        word(colony+2u,1);
        planets[0x11u+0x08u]=(uint8_t)planet_state;
        input_queue(colony,original);
        colony[0x136u+(unsigned)building]=255u;
        h=(Harness){colony,(int16_t)colony_id,building,0u,0u};
        size_t purged=12345u;
        check(moo2_v131_derived_remove_building_environment(
            &ctx,(int16_t)colony_id,building,&purged)
            ==MOO2_V131_BUILDING_ENV_OK);
        unsigned should_purge=building!=15 && planet_state<2u;
        check(purged==(should_purge?3u:0u));
        check(h.step==3u);
        check(colony[0x136u+(unsigned)building]==0u);
        expected_queue(colony,original,should_purge);
        /* Keep colony owner and signed planet index unchanged. */
        check(moo2_v131_environment_s16(colony+2u)==1);
    }
    /* Conditional product44 removal must collapse repeated
       adjacent 44 IDs and -10 sentinels without skipping entries. */
    uint8_t *colony=colonies;
    const int32_t all[7]={44,44,-10,44,44,-10,44};
    memset(colonies,0,sizeof(colonies));
    word(colony+2u,0);
    input_queue(colony,all);
    planets[8u]=0u;
    h=(Harness){colony,0,24,0u,0u};
    size_t purged=0u;
    check(moo2_v131_derived_remove_building_environment(
        &ctx,0,24,&purged)==MOO2_V131_BUILDING_ENV_OK);
    check(purged==5u);
    for(unsigned i=0;i<7u;i++)
        check(moo2_v131_environment_s16(colony+0x115u+2u*i)==-1);

    /* Invalid context and IDs leave the colony unchanged.
       The original does not validate inputs; host checks are safety. */
    uint8_t snapshot[sizeof(colonies)];
    memcpy(snapshot,colonies,sizeof(colonies));
    check(moo2_v131_derived_remove_building_environment(
        &ctx,0,45,&purged)==MOO2_V131_BUILDING_ENV_UNSUPPORTED_ID);
    check(moo2_v131_derived_remove_building_environment(
        &ctx,-1,24,&purged)==MOO2_V131_BUILDING_ENV_INVALID);
    check(moo2_v131_derived_remove_building_environment(
        &ctx,3,24,&purged)==MOO2_V131_BUILDING_ENV_INVALID);
    check(!memcmp(snapshot,colonies,sizeof(colonies)));

    /* Callback errors expose nontransactional partial original
       effects; do not claim automatic rollback. */
    word(colony+2u,0);
    colony[0x136u+15u]=1u;
    h=(Harness){colony,0,15,0u,2u};
    check(moo2_v131_derived_remove_building_environment(
        &ctx,0,15,&purged)==MOO2_V131_BUILDING_ENV_CALLBACK_FAILED);
    check(h.step==2u && colony[0x136u+15u]==0u);
    puts("PASS: 3072 original colony/planet/building paths, exact product44 queue deletion, 3-step callbacks, nontransactional errors");
    return 0;
}
