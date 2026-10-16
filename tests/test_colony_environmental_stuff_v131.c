/* Full original 108-byte Colony_Environmental_Stuff_ source
 * regression. Food_Per_Farmer original named callee is typed
 * test callback, not a guessed source implementation. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/colony_environmental_stuff_v131.c"
static void must(int pass) {
    if(!pass){fputs("FAIL original colony environmental source\n",stderr);exit(1);}
}
static void put16(uint8_t *p,int32_t v){
    uint16_t n=(uint16_t)v;p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);
}
typedef struct {
    uint8_t *colony;
    int32_t owner;
    int16_t production;
    unsigned calls;
    uint8_t expect_environment;
} Fixture;
static int16_t farmer(void *opaque,uint8_t *colony,
                      int32_t owner,int32_t zero) {
    Fixture *f=(Fixture*)opaque;
    must(colony==f->colony);
    must(owner==f->owner && zero==0);
    must(colony[0xe2u]==f->expect_environment);
    f->calls++;
    return f->production;
}
int main(void){
    uint8_t colony[0x169u]={0};
    uint8_t planets[2u*0x11u]={0};
    Fixture f={colony,1,0,0,0};
    Moo2V131ColonyEnvironmentContext ctx={
        planets,2u,farmer,&f
    };
    put16(colony+2u,1);
    unsigned tests=0u;
    for(unsigned status=0;status<256u;status++)
      for(unsigned flags=0;flags<8u;flags++)
        for(unsigned case_id=0;case_id<3u;case_id++) {
        memset(colony,0,sizeof(colony));
        put16(colony+2u,1);
        f.colony=colony;
        f.owner=(case_id==2u ? -1 : (int32_t)case_id);
        colony[0]=(uint8_t)f.owner;
        planets[0x11u+8u]=(uint8_t)status;
        colony[0x14du]=(uint8_t)(flags&1u);
        colony[0x14eu]=(uint8_t)(flags&2u);
        colony[0x152u]=(uint8_t)(flags&4u);
        colony[0xe0u]=0xa5u;colony[0xe2u]=0xb4u;
        f.production=(int16_t)(case_id==0u?0:case_id==1u?3:-1);
        f.expect_environment=(uint8_t)((status==1u && (flags&3u))?2u:status);
        f.calls=0u;
        must(moo2_v131_derived_colony_environmental(
            &ctx,colony,sizeof(colony))==MOO2_V131_COLONY_ENV_OK);
        must(f.calls==1u);
        must(colony[0xe2u]==f.expect_environment);
        must(colony[0xe0u]==(uint8_t)(f.production==0?0u:255u));
        must(colony[0x152u]==(uint8_t)(flags&4u));
        tests++;
    }
    /* Invalid planet index must be rejected prior to state mutation. */
    put16(colony+2u,-1);
    uint8_t saved[sizeof(colony)];
    memcpy(saved,colony,sizeof(colony));
    must(moo2_v131_derived_colony_environmental(
        &ctx,colony,sizeof(colony))==MOO2_V131_COLONY_ENV_INVALID);
    must(!memcmp(saved,colony,sizeof(colony)));
    put16(colony+2u,2);
    must(moo2_v131_derived_colony_environmental(
        &ctx,colony,sizeof(colony))==MOO2_V131_COLONY_ENV_INVALID);
    ctx.food_per_farmer=NULL;
    must(moo2_v131_derived_colony_environmental(
        &ctx,colony,sizeof(colony))==MOO2_V131_COLONY_ENV_INVALID);
    printf("PASS: %u planet-byte/colony-flags/food-source cases, dead branch +0x152, host bounds\n",tests);
    return 0;
}
