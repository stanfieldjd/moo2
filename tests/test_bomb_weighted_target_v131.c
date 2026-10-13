/* Derived source-weighted MOO2 bomb-hit category selection regression.
 * Tests the original target draw and group weights, not actual hit effects.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/random_v131.c"
#include "../decompilation/reconstructed/colony_hit_target_selection_v131.c"

static void demand(int yes){if(!yes){fputs("FAIL original bomb weighted target group\n",stderr);exit(1);}}
static void w16(uint8_t *p,uint16_t bits){
    p[0]=(uint8_t)bits;p[1]=(uint8_t)(bits>>8);
}
static uint32_t independent_rng(uint32_t *seed,uint32_t max) {
    demand(max>0);
    const uint32_t divisor=UINT32_MAX/max,limit=divisor*max;
    do {*seed=*seed*UINT32_C(0x41C64E6D)+UINT32_C(0x3039);}
    while(*seed>=limit);
    return *seed/divisor+1u;
}
int main(void) {
    uint8_t colony[0x169]={0};
    colony[0x136u+48u]=1u;
    colony[0x136u+0u]=1u;
    colony[0x136u+47u]=1u; /* excluded even when nonzero */
    w16(colony+0x130u,2u);
    w16(colony+0x132u,3u);
    w16(colony+0x125u,1u);
    colony[0x0au]=2u;

    /* Source group intervals for total10:
       building [0,1] (indices48,0), +0x130 [2,3],
       +0x132 [4,6], +0x125 [7], population [8,9]. */
    for(uint32_t initial=0;initial<4096u;initial++) {
        uint32_t reference_seed=initial*UINT32_C(0x4C11DB7)+UINT32_C(0x12345);
        uint32_t used_seed=reference_seed;
        const uint32_t position=independent_rng(&reference_seed,10u)-1u;
        Moo2V131BombWeightedSelection value={0};
        demand(moo2_v131_derived_bomb_weighted_target(
            colony,sizeof(colony),&used_seed,&value)==MOO2_V131_HIT_SELECT_OK);
        demand(used_seed==reference_seed && value.total_weight==10u);
        demand(value.zero_based_draw==position);
        if(position<2u) {
            demand(value.kind==MOO2_V131_BOMB_TARGET_BUILDING);
            demand(value.selected_building_index==(position==0u?48u:0u));
            demand(value.source_category_offset==position);
        } else if(position<4u) {
            demand(value.kind==MOO2_V131_BOMB_TARGET_POP_130);
            demand(value.source_category_offset==position-2u);
        } else if(position<7u) {
            demand(value.kind==MOO2_V131_BOMB_TARGET_POP_132);
            demand(value.source_category_offset==position-4u);
        } else if(position==7u) {
            demand(value.kind==MOO2_V131_BOMB_TARGET_COLONY_125);
        } else {
            demand(value.kind==MOO2_V131_BOMB_TARGET_POP_ENTRY);
            demand(value.source_category_offset==position-8u);
        }
    }

    /* A sole pop entry takes the original early path when all
       other group weights are absent, without consuming RNG state. */
    memset(colony,0,sizeof(colony));
    colony[0x0au]=1u;
    uint32_t seed=0x12345678u;
    Moo2V131BombWeightedSelection value={0};
    demand(moo2_v131_derived_bomb_weighted_target(
        colony,sizeof(colony),&seed,&value)==MOO2_V131_HIT_SELECT_OK);
    demand(seed==0x12345678u && value.total_weight==0u);
    demand(value.kind==MOO2_V131_BOMB_TARGET_SINGLE_ENTRY_SPECIAL);

    /* No eligible targets in an empty colony skips RNG. */
    colony[0x0au]=0u;
    demand(moo2_v131_derived_bomb_weighted_target(
        colony,sizeof(colony),&seed,&value)==MOO2_V131_HIT_SELECT_NONE);
    demand(value.kind==MOO2_V131_BOMB_TARGET_NONE && seed==0x12345678u);

    /* Signed colony+0x125 WORD is tested against zero, not positivity.
       Source negative values still contribute one slot when nonzero. */
    w16(colony+0x125u,0xffffu);
    demand(moo2_v131_derived_bomb_weighted_target(
        colony,sizeof(colony),&seed,&value)==MOO2_V131_HIT_SELECT_OK);
    demand(value.total_weight==1u);
    demand(value.kind==MOO2_V131_BOMB_TARGET_COLONY_125);

    /* A single population member with positive other weights does
       NOT add itself as an ordinary weighted group, source has
       a unique ==1 branch. */
    memset(colony,0,sizeof(colony));
    colony[0x0au]=1u;
    w16(colony+0x130u,1u);
    demand(moo2_v131_derived_bomb_weighted_target(
        colony,sizeof(colony),&seed,&value)==MOO2_V131_HIT_SELECT_OK);
    demand(value.total_weight==1u && value.kind==MOO2_V131_BOMB_TARGET_POP_130);

    /* Other non-single population count is included in weighting. */
    memset(colony,0,sizeof(colony));
    colony[0x0au]=2u;
    demand(moo2_v131_derived_bomb_weighted_target(
        colony,sizeof(colony),&seed,&value)==MOO2_V131_HIT_SELECT_OK);
    demand(value.total_weight==2u && value.kind==MOO2_V131_BOMB_TARGET_POP_ENTRY);
    demand(value.source_category_offset<=1u);

    w16(colony+0x130u,0xffffu);
    demand(moo2_v131_derived_bomb_weighted_target(
        colony,sizeof(colony),&seed,&value)==MOO2_V131_HIT_SELECT_INVALID);
    demand(moo2_v131_derived_bomb_weighted_target(
        colony,0x166u,&seed,&value)==MOO2_V131_HIT_SELECT_INVALID);
    demand(moo2_v131_derived_bomb_weighted_target(
        NULL,sizeof(colony),&seed,&value)==MOO2_V131_HIT_SELECT_INVALID);
    puts("PASS: 4096 original seeded bomb target group draws, single/empty and source nonzero-word branches");
    return 0;
}
