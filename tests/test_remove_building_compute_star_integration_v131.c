/*
 * Full source-derived Compute_Star_Colony_Stuff_ integrated with original
 * Remove_Building_ direct cases 3,14,45 (and original ETA callback for 45).
 * Validates real star flag changes after the original building BYTE clears;
 * DOES NOT replace Update_Ship_ETAs_ or original DOS executable.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/compute_star_colony_stuff_v131.c"
#include "../decompilation/reconstructed/remove_building_star_recalc_v131.c"

static void must(int good){
    if(!good){fputs("FAIL star computation + source building removal integration\n",stderr);exit(1);}
}
static void w16(uint8_t *p,uint16_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
typedef struct {
    Moo2V131StarColonyContext source;
    uint8_t *star;
    unsigned compute_calls;
    unsigned eta_calls;
    int32_t expected_owner;
} Harness;
static void calc(void *opaque,uint8_t *star) {
    Harness *h=(Harness*)opaque;
    must(star==h->star);
    must(moo2_v131_derived_compute_star_colony_stuff(
        &h->source,star,0x71u)==MOO2_V131_STAR_COLONY_OK);
    h->compute_calls++;
}
static void eta(void *opaque,int32_t owner) {
    Harness *h=(Harness*)opaque;
    must(h->compute_calls==3u);
    must(h->star[0x39u]==0u);
    must(owner==h->expected_owner);
    h->eta_calls++;
}
int main(void) {
    uint8_t colonies[0x169u]={0};
    uint8_t planets[0x11u]={0};
    uint8_t stars[0x71u]={0};
    uint8_t players[8u*0xEA9u]={0};
    for(unsigned i=0;i<5u;i++)w16(stars+0x4Au+2u*i,UINT16_MAX);
    w16(stars+0x4Au,0u);
    w16(planets,0u);
    w16(colonies+2u,0u);
    Harness h={{planets,1,colonies,1,players,8},stars,0,0,0};
    Moo2V131BuildingStarRecalcContext ctx={
        colonies,1,planets,1,stars,1,calc,eta,&h
    };
    for(unsigned owner=0;owner<8u;owner++) {
        memset(players,0,sizeof(players));
        colonies[0]=(uint8_t)owner;
        uint8_t *player=players+(size_t)owner*0xEA9u;
        player[0x17Au]=3u;player[0x1C1u]=3u;
        colonies[0x136u+3u]=1u;
        colonies[0x136u+14u]=1u;
        colonies[0x136u+45u]=1u;
        h.expected_owner=(int32_t)owner;
        h.compute_calls=h.eta_calls=0u;
        const uint8_t bit=(uint8_t)(1u<<owner);
        must(moo2_v131_derived_compute_star_colony_stuff(
            &h.source,stars,sizeof(stars))==MOO2_V131_STAR_COLONY_OK);
        must(stars[0x38u]==bit && stars[0x39u]==bit);
        must(stars[0x3Fu]==bit && stars[0x40u]==bit);
        must(stars[0x3Eu]==bit && stars[0x3Du]==bit);

        must(moo2_v131_derived_remove_building_star_recalc(
            &ctx,0,3)==MOO2_V131_BUILDING_STAR_RECALC_OK);
        must(h.compute_calls==1u && h.eta_calls==0u);
        must(stars[0x3Fu]==0 && stars[0x40u]==bit);
        must(stars[0x39u]==bit && stars[0x38u]==bit);
        must(colonies[0x136u+3u]==0u);

        must(moo2_v131_derived_remove_building_star_recalc(
            &ctx,0,14)==MOO2_V131_BUILDING_STAR_RECALC_OK);
        must(h.compute_calls==2u && h.eta_calls==0u);
        must(stars[0x3Fu]==0 && stars[0x40u]==0);
        must(stars[0x39u]==bit && stars[0x38u]==bit);
        must(colonies[0x136u+14u]==0u);

        must(moo2_v131_derived_remove_building_star_recalc(
            &ctx,0,45)==MOO2_V131_BUILDING_STAR_RECALC_OK);
        must(h.compute_calls==3u && h.eta_calls==1u);
        must(stars[0x39u]==0 && stars[0x38u]==bit);
        must(stars[0x3Eu]==bit && stars[0x3Du]==bit);
        must(colonies[0x136u+45u]==0u);
    }
    puts("PASS: 8 original owners x three building-removal calls recompute real star flags and ID45 ETA ordering");
    return 0;
}
