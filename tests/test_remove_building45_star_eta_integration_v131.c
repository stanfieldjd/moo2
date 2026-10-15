/*
 * Original building ID45 removal through complete source-derived
 * Compute_Star_Colony_Stuff_ and Update_Ship_ETAs_ loops.
 * Move_Player_1_Turn_To_Star_ remains an explicit deterministic
 * test callback, NOT equivalent original space-movement physics.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/remove_building_star_recalc_v131.c"
#include "../decompilation/reconstructed/compute_star_colony_stuff_v131.c"
#include "../decompilation/reconstructed/update_ship_etas_v131.c"

static void must(int test) {
    if(!test){fputs("FAIL building45 star+ETA source integration\n",stderr);exit(1);}
}
static void word(uint8_t *p,int32_t n) {
    uint16_t v=(uint16_t)n;p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
typedef struct {
    uint8_t *colony;
    uint8_t *star;
    Moo2V131StarColonyContext compute;
    Moo2V131EtaContext eta;
    int32_t expected_owner;
    int32_t expected_travel_owner;
    unsigned star_calls;
    unsigned eta_calls;
    unsigned movement_calls;
} Harness;
static int move(void *opaque,int32_t owner,int32_t target_star,
                uint8_t parameter,int16_t *x,int16_t *y,
                uint8_t *optional,uint8_t *required) {
    Harness *h=(Harness*)opaque;
    must(h->star_calls==1 && h->eta_calls==1);
    must(owner==h->expected_travel_owner && target_star==0);
    must(parameter==5 && optional && required);
    *required=0u;*optional=0u;
    *x=(int16_t)(*x+2);
    *y=0;
    h->movement_calls++;
    return 1;
}
static void compute_star(void *opaque,uint8_t *star) {
    Harness *h=(Harness*)opaque;
    must(star==h->star);
    must(h->colony[0x136u+45u]==0);
    must(moo2_v131_derived_compute_star_colony_stuff(
        &h->compute,star,0x71u)==MOO2_V131_STAR_COLONY_OK);
    must(star[0x39u]==0u);
    h->star_calls++;
}
static void update_eta(void *opaque,int32_t changed_owner) {
    Harness *h=(Harness*)opaque;
    must(h->star_calls==1 && h->eta_calls==0);
    must(changed_owner==h->expected_owner);
    must(h->star[0x39u]==0);
    h->eta_calls++;
    size_t processed=999u;
    must(moo2_v131_derived_update_ship_etas(
        &h->eta,(int16_t)changed_owner,&processed)==MOO2_V131_ETA_OK);
    must(processed==1u);
}
int main(void) {
    uint8_t colonies[0x169]={0},planets[0x11]={0},
            stars[0x71]={0},players[8u*0xEA9u]={0};
    uint8_t ships[2u*0x81u]={0};
    word(colonies+2u,0);
    word(planets,0);
    for(unsigned i=0;i<5;i++)word(stars+0x4Au+2u*i,-1);
    word(stars+0x4Au,0);
    word(stars+0x0Fu,4);
    word(stars+0x11u,0);
    Harness h={0};
    h.colony=colonies;
    h.star=stars;
    h.compute=(Moo2V131StarColonyContext){planets,1,colonies,1,players,8};
    h.eta=(Moo2V131EtaContext){ships,2,stars,1,move,&h,16};
    Moo2V131BuildingStarRecalcContext ctx={
        colonies,1,planets,1,stars,1,compute_star,update_eta,&h
    };
    for(unsigned owner=0;owner<8;owner++) {
        memset(ships,0,sizeof(ships));
        colonies[0]=(uint8_t)owner;
        colonies[0x136u+45u]=1u;
        h.expected_owner=(int32_t)owner;
        h.expected_travel_owner=(int32_t)((owner+1u)%8u);
        h.star_calls=h.eta_calls=h.movement_calls=0u;
        /* Ship 0 belongs to removed-building owner, source ETA skips.
           Ship 1 belongs to another player, state1 dest star0. */
        ships[0x63u]=(uint8_t)owner;
        ships[0x64u]=1u;word(ships+0x65u,500);
        ships[0x6Du]=0x9Fu;
        uint8_t *other=ships+0x81u;
        other[0x63u]=(uint8_t)h.expected_travel_owner;
        other[0x64u]=1u;word(other+0x65u,500);
        word(other+0x67u,0);word(other+0x69u,0);
        other[0x6Bu]=0;other[0x6Cu]=5;
        other[0x6Du]=0x9Fu;
        must(moo2_v131_derived_compute_star_colony_stuff(
            &h.compute,stars,sizeof(stars))==MOO2_V131_STAR_COLONY_OK);
        const uint8_t bit=(uint8_t)(1u<<owner);
        must(stars[0x38u]==bit && stars[0x39u]==bit);
        must(moo2_v131_derived_remove_building_star_recalc(
            &ctx,0,45)==MOO2_V131_BUILDING_STAR_RECALC_OK);
        must(h.star_calls==1u && h.eta_calls==1u && h.movement_calls==2u);
        must(stars[0x38u]==bit && stars[0x39u]==0);
        must(other[0x6Du]==2u && ships[0x6Du]==0x9Fu);
        must(colonies[0x136u+45u]==0u);
        must(moo2_v131_eta_s16(other+0x67u)==0);
    }
    puts("PASS: eight original owners, building45 flag clear -> real star-field rebuild -> ETA scan and counted movement callback");
    return 0;
}
