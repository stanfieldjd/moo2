/*
 * Source-derived v1.31 Remove_Building_ direct star recompute path.
 * Original building IDs 3,14,45 only; IDs 8/40/41 require unmodeled
 * queue updates before reaching the same shared code and are rejected.
 * Actual Compute_Star_Colony_Stuff_ and Update_Ship_ETAs_ effects
 * are explicit callbacks, not fake game implementations.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/remove_building_star_recalc_v131.c"

static void check(int ok){if(!ok){fputs("FAIL v1.31 Remove_Building_ star recalculation\n",stderr);exit(1);}}

typedef struct {
    uint8_t *colony;
    uint8_t *expected_star;
    int original_building_id;
    int modify_owner;
    unsigned compute_calls;
    unsigned eta_calls;
    int32_t expected_owner_after_compute;
} Harness;
static void compute(void *opaque,uint8_t *star_record) {
    Harness *x=(Harness*)opaque;
    check(star_record==x->expected_star);
    check(x->colony[0x136u+(unsigned)x->original_building_id]==0u);
    x->compute_calls++;
    if(x->modify_owner)x->colony[0]=0xFEu;
}
static void update_etas(void *opaque,int32_t owner) {
    Harness *x=(Harness*)opaque;
    check(x->compute_calls==1u && x->eta_calls==0u);
    check(owner==x->expected_owner_after_compute);
    x->eta_calls++;
}
static void write16(uint8_t *p,uint16_t v){
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
int main(void) {
    uint8_t colonies[2u*0x169u]={0};
    uint8_t planets[2u*0x11u]={0};
    uint8_t stars[256u*0x71u]={0};
    uint8_t *colony=colonies+0x169u;
    Harness h={0};
    h.colony=colony;
    Moo2V131BuildingStarRecalcContext ctx={
        colonies,2u,planets,2u,stars,256u,compute,update_etas,&h
    };
    write16(colony+2u,1u);
    colony[0]=1u;
    for(unsigned idcase=0;idcase<3u;idcase++) {
        const int building=idcase==0?3:idcase==1?14:45;
        for(unsigned star=0;star<256u;star++) {
            memset(stars,0,sizeof(stars));
            planets[0x11u+2u]=(uint8_t)star;
            h.expected_star=stars+(size_t)star*0x71u;
            h.original_building_id=building;
            h.compute_calls=h.eta_calls=0u;
            h.modify_owner=(building==45);
            h.expected_owner_after_compute=(building==45)?-2:1;
            colony[0]=1u;
            colony[0x136u+(unsigned)building]=0xFFu;
            check(moo2_v131_derived_remove_building_star_recalc(
                &ctx,1,(int16_t)building)==MOO2_V131_BUILDING_STAR_RECALC_OK);
            check(h.compute_calls==1u);
            check(h.eta_calls==(unsigned)(building==45));
            check(colony[0x136u+(unsigned)building]==0u);
            check(colony[0]==(building==45?0xFEu:1u));
        }
    }
    /* Valid removal should not run callbacks for invalid pointers. */
    h.compute_calls=h.eta_calls=0u;
    colony[0x136u+3u]=0xABu;
    write16(colony+2u,2u);
    check(moo2_v131_derived_remove_building_star_recalc(
        &ctx,1,3)==MOO2_V131_BUILDING_STAR_RECALC_INVALID);
    check(colony[0x136u+3u]==0xABu && h.compute_calls==0u);
    write16(colony+2u,1u);
    ctx.star_count=1u;
    planets[0x11u+2u]=2u;
    check(moo2_v131_derived_remove_building_star_recalc(
        &ctx,1,3)==MOO2_V131_BUILDING_STAR_RECALC_INVALID);
    check(colony[0x136u+3u]==0xABu);
    ctx.star_count=256u;
    /* Queue-using IDs cannot be incorrectly routed as direct
       recalculations: their original side effects must be modeled. */
    for(int building=8;building<=41;building+=building==8?32:1) {
        colony[0x136u+(unsigned)building]=0xB3u;
        check(moo2_v131_derived_remove_building_star_recalc(
            &ctx,1,(int16_t)building)==MOO2_V131_BUILDING_STAR_RECALC_UNSUPPORTED_ID);
        check(colony[0x136u+(unsigned)building]==0xB3u);
    }
    ctx.update_ship_etas=NULL;
    colony[0x136u+45u]=0x5Au;
    check(moo2_v131_derived_remove_building_star_recalc(
        &ctx,1,45)==MOO2_V131_BUILDING_STAR_RECALC_INVALID);
    check(colony[0x136u+45u]==0x5Au);
    puts("PASS: 3 source building IDs x 256 planet->star indices, callback order, owner reread, no unsafe partial writes");
    return 0;
}
