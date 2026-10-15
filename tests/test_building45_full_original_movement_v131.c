/*
 * Original MOO2 v1.31 end-to-end source-derived building45:
 * Remove_Building_ flag clear -> full Compute_Star_Colony_Stuff_
 * -> full Update_Ship_ETAs_ -> full Move_Player_1_Turn_To_Star_
 * -> original isqrt_, nebula and warp-field checks.
 * Runtime callbacks ONLY connect independently source-recovered C
 * functions, rather than replacing gameplay with fake movement.
 *
 * This is a source consistency test, not original DOS differential play.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/remove_building_star_recalc_v131.c"
#include "../decompilation/reconstructed/compute_star_colony_stuff_v131.c"
#include "../decompilation/reconstructed/update_ship_etas_v131.c"
#include "../decompilation/reconstructed/isqrt_v131.c"
#include "../decompilation/reconstructed/point_in_nebula_v131.c"
#include "../decompilation/reconstructed/point_in_warp_field_v131.c"
#include "../decompilation/reconstructed/move_player_one_turn_v131.c"

static void must(int ok) {
    if(!ok){fputs("FAIL full original building45 -> ship ETA movement chain\n",stderr);exit(1);}
}
static void w16(uint8_t *p,int32_t n){
    uint16_t x=(uint16_t)n;p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8);
}
typedef struct {
    uint8_t *colony;
    uint8_t *star;
    Moo2V131StarColonyContext star_source;
    Moo2V131MoveContext move_source;
    Moo2V131EtaContext eta_source;
    unsigned star_recalculations;
    unsigned eta_updates;
    unsigned movement_calls;
    int32_t changed_owner;
    uint8_t movement_expected_speed;
} Harness;
static int ship_step(void *opaque,int32_t owner,int32_t star_index,
                     uint8_t speed,int16_t *x,int16_t *y,
                     uint8_t *nebula,uint8_t *warp) {
    Harness *h=(Harness*)opaque;
    must(h->star_recalculations==1 && h->eta_updates==1);
    must(owner>=0 && owner<8 && owner!=h->changed_owner);
    must(star_index==0 && speed==h->movement_expected_speed);
    must(x && y && warp);
    h->movement_calls++;
    return moo2_v131_derived_move_player_one_turn(
        &h->move_source,owner,star_index,*x,*y,speed,
        x,y,nebula,warp)==MOO2_V131_MOVE_OK;
}
static void star_recalc(void *opaque,uint8_t *star){
    Harness *h=(Harness*)opaque;
    must(star==h->star && h->colony[0x136u+45u]==0u);
    must(moo2_v131_derived_compute_star_colony_stuff(
        &h->star_source,star,0x71u)==MOO2_V131_STAR_COLONY_OK);
    must(star[0x39u]==0u);
    h->star_recalculations++;
}
static void ship_etas(void *opaque,int32_t changed_owner){
    Harness *h=(Harness*)opaque;
    must(changed_owner==h->changed_owner);
    must(h->star_recalculations==1 && h->eta_updates==0);
    must(h->star[0x39u]==0u);
    h->eta_updates++;
    size_t processed=777u;
    must(moo2_v131_derived_update_ship_etas(
        &h->eta_source,(int16_t)changed_owner,&processed)
        ==MOO2_V131_ETA_OK);
    must(processed==1u);
}
int main(void){
    uint8_t colonies[0x169u]={0},planets[0x11u]={0},
            star[0x71u]={0},players[8u*0xEA9u]={0},
            ships[2u*0x81u]={0};
    Moo2V131NebulaContext no_nebula={NULL,0,NULL};
    w16(colonies+2u,0);
    w16(planets,0);
    for(unsigned i=0;i<5;i++)w16(star+0x4au+2u*i,-1);
    w16(star+0x4au,0);
    w16(star+0x0fu,120);
    w16(star+0x11u,90);
    Harness h={0};
    h.colony=colonies;h.star=star;
    h.star_source=(Moo2V131StarColonyContext){
        planets,1,colonies,1,players,8};
    h.move_source=(Moo2V131MoveContext){star,1,&no_nebula};
    h.eta_source=(Moo2V131EtaContext){
        ships,2,star,1,ship_step,&h,16};
    Moo2V131BuildingStarRecalcContext remove={
        colonies,1,planets,1,star,1,star_recalc,ship_etas,&h
    };
    for(unsigned changed_owner=0;changed_owner<8;changed_owner++)
      for(unsigned state=1;state<=2;state++)
        for(unsigned speed=1;speed<=5;speed++) {
        colonies[0]=(uint8_t)changed_owner;
        colonies[0x136u+45u]=1u;
        memset(ships,0,sizeof(ships));
        /* Ship0 is same original player and is excluded. */
        ships[0x63u]=(uint8_t)changed_owner;
        ships[0x64u]=1u;
        w16(ships+0x65u,6000); /* would be invalid if accessed */
        ships[0x6du]=0xBAu;
        /* Ship1 is another owner and gets recomputed. */
        uint8_t *other=ships+0x81u;
        other[0x63u]=(uint8_t)((changed_owner+1u)%8u);
        other[0x64u]=(uint8_t)state;
        w16(other+0x65u,(int32_t)(state==1?500:1000));
        w16(other+0x67u,0);w16(other+0x69u,0);
        other[0x6bu]=0u;other[0x6cu]=(uint8_t)speed;
        other[0x6du]=0xCBu;
        h.changed_owner=(int32_t)changed_owner;
        h.movement_expected_speed=(uint8_t)speed;
        h.star_recalculations=h.eta_updates=h.movement_calls=0u;
        must(moo2_v131_derived_compute_star_colony_stuff(
            &h.star_source,star,sizeof(star))==MOO2_V131_STAR_COLONY_OK);
        const uint8_t owner_bit=(uint8_t)(1u<<changed_owner);
        must(star[0x39u]==owner_bit);
        must(moo2_v131_derived_remove_building_star_recalc(
            &remove,0,45)==MOO2_V131_BUILDING_STAR_RECALC_OK);
        const unsigned wanted=(5u+speed-1u)/speed;
        must(h.star_recalculations==1 && h.eta_updates==1);
        must(h.movement_calls==wanted);
        must(star[0x38u]==owner_bit && star[0x39u]==0u);
        must(other[0x6du]==wanted && ships[0x6du]==0xBAu);
        must(colonies[0x136u+45u]==0u);
        must(moo2_v131_eta_s16(other+0x67u)==0);
        must(moo2_v131_eta_s16(other+0x69u)==0);
    }
    puts("PASS 80 full source-derived MOO2 building45->star->ETA->movement->environment cases");
}
