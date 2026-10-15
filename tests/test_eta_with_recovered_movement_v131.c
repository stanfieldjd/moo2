/*
 * Full original-derived pipeline for v1.31 ship ETA:
 * authenticated Update_Ship_ETAs_ 253-byte reverse scan calls
 * authenticated Move_Player_1_Turn_To_Star_ 422-byte projection,
 * using original isqrt_, nebula and warp-field helpers (all now
 * source-derived C). No DOS dynamic differential run.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/isqrt_v131.c"
#include "../decompilation/reconstructed/point_in_nebula_v131.c"
#include "../decompilation/reconstructed/point_in_warp_field_v131.c"
#include "../decompilation/reconstructed/move_player_one_turn_v131.c"
#include "../decompilation/reconstructed/update_ship_etas_v131.c"
static void must(int yes){
    if(!yes){fputs("FAIL ETA with recovered movement\n",stderr);exit(1);}
}
static void word(uint8_t *p,int32_t n){
    uint16_t v=(uint16_t)n;p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
typedef struct {
    Moo2V131MoveContext source_move;
    unsigned calls;
} Movement;
static int step(void *opaque,int32_t original_owner,
                int32_t target_star,uint8_t speed,
                int16_t *x,int16_t *y,
                uint8_t *nebula_flag,uint8_t *warp_flag)
{
    Movement *m=(Movement*)opaque;
    must(x && y && warp_flag);
    Moo2V131MoveResult rc=moo2_v131_derived_move_player_one_turn(
        &m->source_move,original_owner,target_star,*x,*y,
        speed,x,y,nebula_flag,warp_flag);
    m->calls++;
    return rc==MOO2_V131_MOVE_OK;
}
int main(void){
    uint8_t ships[2u*0x81u]={0},star[0x71]={0};
    Moo2V131NebulaContext none={NULL,0,NULL};
    Movement movement={{star,1u,&none},0};
    Moo2V131EtaContext eta={
        ships,2u,star,1u,step,&movement,1600u
    };
    word(star+0x0fu,120);word(star+0x11u,90);
    for(unsigned own=0;own<8u;own++)for(unsigned state=1u;state<=2u;state++)
      for(unsigned speed=1u;speed<=5u;speed++){
        memset(ships,0,sizeof(ships));
        /* Ship0 belongs to changed player: source skips it, even if
           destination encoding is intentionally invalid. */
        ships[0x63u]=(uint8_t)own;
        ships[0x64u]=1u;word(ships+0x65u,30000);
        ships[0x6du]=0xABu;
        uint8_t *moving=ships+0x81u;
        moving[0x63u]=(uint8_t)((own+1u)%8u);
        moving[0x64u]=(uint8_t)state;
        word(moving+0x65u,(int32_t)(state==1u?500:1000));
        word(moving+0x67u,0);word(moving+0x69u,0);
        moving[0x6bu]=0u;moving[0x6cu]=(uint8_t)speed;
        moving[0x6du]=0xCDu;
        movement.calls=0u;
        size_t processed=0u;
        must(moo2_v131_derived_update_ship_etas(
            &eta,(int16_t)own,&processed)==MOO2_V131_ETA_OK);
        unsigned expected=(5u+speed-1u)/speed;
        must(processed==1u);
        must(movement.calls==expected);
        must(moving[0x6du]==(uint8_t)expected);
        must(ships[0x6du]==0xABu);
        must(moo2_v131_eta_s16(moving+0x67u)==0);
        must(moo2_v131_eta_s16(moving+0x69u)==0);
    }
    /* Long 1000-unit/turn-count trip verifies 16-bit turn counter
       is written to ETA as low eight bits, not saturated. */
    eta.ship_count=1u;
    uint8_t *ship=ships;
    memset(ships,0,sizeof(ships));
    ship[0x63u]=2u;ship[0x64u]=1u;
    word(ship+0x65u,500);
    ship[0x6cu]=1u;ship[0x6du]=0xEEu;
    word(star+0x0fu,30000);word(star+0x11u,0);
    movement.calls=0u;
    size_t processed=999u;
    must(moo2_v131_derived_update_ship_etas(
        &eta,1,&processed)==MOO2_V131_ETA_OK);
    must(movement.calls==1000u && processed==1u);
    must(ship[0x6du]==(uint8_t)(1000u%256u));
    puts("PASS original 253-byte ETA -> 422-byte movement -> isqrt/nebula/warp: 80 cases plus 1000-turn low-byte wrap");
    return 0;
}
