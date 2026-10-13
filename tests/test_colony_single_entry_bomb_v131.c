/*
 * Source-derived original v1.31 single-population bomb branch regression.
 * NOT entire Resolve_Bomb_Hit_ or Remove_Building_ equivalence.
 * Compare all signed 16-bit defense values and all 16 colony entry types.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/colony_hit_player_stats_v131.c"
#include "../decompilation/reconstructed/colony_single_entry_bomb_v131.c"

static void require(int okay){if(!okay){fputs("FAIL single-population bomb resolver\n",stderr);exit(1);}}
static uint16_t read16(const uint8_t *p){return (uint16_t)(p[0]|((uint16_t)p[1]<<8));}
static void put16(uint8_t *p,uint16_t x){p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8);}
typedef struct {
    uint8_t *colony;
    uint8_t *event;
    unsigned calls;
    int16_t expected_id;
} RemoveCtx;
static void remove_building(void *opaque,int16_t colony_id,uint16_t building_id) {
    RemoveCtx *ctx=(RemoveCtx*)opaque;
    require(colony_id==ctx->expected_id && building_id==9u);
    require(ctx->colony[0x0Au]==0u);
    require(ctx->event[0x42u]==0u); /* set AFTER source callback */
    require(read16(ctx->event+0x0Cu)==1u);
    ctx->calls++;
}
int main(void) {
    uint8_t colonies[2u*0x169u]={0};
    uint8_t event[0x49u]={0};
    uint8_t players[2u*0xEA9u]={0};
    uint8_t *colony=colonies+0x169u;
    colony[0]=1u;event[0]=2u;
    RemoveCtx recorder={colony,event,0u,1};
    Moo2V131SingleEntryBombContext ctx={
        colonies,2u,event,sizeof(event),players,sizeof(players),
        remove_building,&recorder
    };
    uint8_t *stat=players+0xEA9u+0x6FFu+2u*2u;
    uint32_t returned=777u;
    const unsigned kind=3u;
    colony[0x0Cu]=(uint8_t)kind;
    uint8_t *defense=colony+0xB4u+2u*kind;

    for(uint32_t n=0;n<=UINT16_MAX;n++) {
        colony[0x0Au]=1u;
        put16(defense,(uint16_t)n);
        put16(event+0x0Cu,UINT16_MAX);
        put16(stat,UINT16_MAX);
        event[0x41u]=0u;
        event[0x42u]=0u;
        returned=777u;
        require(moo2_v131_derived_single_entry_bomb(&ctx,1,&returned)
            ==MOO2_V131_SINGLE_ENTRY_OK);
        const int32_t signed_n=n<32768u?(int32_t)n:(int32_t)n-65536;
        if(signed_n>100) {
            require(read16(defense)==(uint16_t)(n-100u));
            require(colony[0x0Au]==1u && event[0x42u]==0u);
            require(read16(event+0x0Cu)==UINT16_MAX);
            require(read16(stat)==UINT16_MAX);
        } else {
            require(read16(defense)==0u);
            require(colony[0x0Au]==0u && event[0x42u]==1u);
            require(read16(event+0x0Cu)==0u);
            require(read16(stat)==9u);
        }
        require(event[0x41u]==1u && returned==1u);
    }

    /* All 16 potential original low-nibble defense index values. */
    for(unsigned k=0;k<16u;k++){
        memset(colony+0xB4u,0,0x20u);
        colony[0x0Au]=1u;
        colony[0x0Cu]=(uint8_t)(0xA0u|k);
        put16(colony+0xB4u+2u*k,101u);
        event[0x41u]=event[0x42u]=0u;
        require(moo2_v131_derived_single_entry_bomb(&ctx,1,&returned)
            ==MOO2_V131_SINGLE_ENTRY_OK);
        require(read16(colony+0xB4u+2u*k)==1u);
        require(colony[0x0Au]==1u && !event[0x42u]);
    }

    /* Building 9 marker is in the original EXCLUDED 49-slot list,
       yet triggers Remove_Building_ after death. */
    colony[0x0Cu]=1u;colony[0x0Au]=1u;
    put16(colony+0xB4u+2u,100u);
    colony[0x13Fu]=1u;
    put16(event+0x0Cu,0u);
    event[0x42u]=0u;
    unsigned before=recorder.calls;
    require(moo2_v131_derived_single_entry_bomb(&ctx,1,&returned)
        ==MOO2_V131_SINGLE_ENTRY_OK);
    require(recorder.calls==before+1u);
    require(event[0x42u]==1u && event[0x41u]==1u);

    /* No callback is needed if surviving defense is > 100. */
    ctx.remove_building=NULL;
    colony[0x0Au]=1u;put16(colony+0xB4u+2u,101u);
    require(moo2_v131_derived_single_entry_bomb(&ctx,1,&returned)
        ==MOO2_V131_SINGLE_ENTRY_OK);
    require(read16(colony+0xB4u+2u)==1u);
    /* Death with marker and missing callback safely fails closed. */
    colony[0x0Au]=1u;put16(colony+0xB4u+2u,100u);
    uint8_t old_colony[0x169u];memcpy(old_colony,colony,sizeof(old_colony));
    require(moo2_v131_derived_single_entry_bomb(&ctx,1,&returned)
        ==MOO2_V131_SINGLE_ENTRY_INVALID);
    require(memcmp(old_colony,colony,sizeof(old_colony))==0);
    ctx.remove_building=remove_building;
    colony[0x13Fu]=0u;

    /* Other weighted targets or multiple population entries cannot
       enter this original special branch. */
    colony[0x0Au]=2u;
    require(moo2_v131_derived_single_entry_bomb(&ctx,1,&returned)
        ==MOO2_V131_SINGLE_ENTRY_NOT_APPLICABLE);
    colony[0x0Au]=1u;colony[0x136u]=1u;
    require(moo2_v131_derived_single_entry_bomb(&ctx,1,&returned)
        ==MOO2_V131_SINGLE_ENTRY_NOT_APPLICABLE);
    colony[0x136u]=0u;
    put16(colony+0x130u,1u);
    require(moo2_v131_derived_single_entry_bomb(&ctx,1,&returned)
        ==MOO2_V131_SINGLE_ENTRY_NOT_APPLICABLE);
    put16(colony+0x130u,0u);
    require(moo2_v131_derived_single_entry_bomb(&ctx,-1,&returned)
        ==MOO2_V131_SINGLE_ENTRY_INVALID);
    require(moo2_v131_derived_single_entry_bomb(&ctx,2,&returned)
        ==MOO2_V131_SINGLE_ENTRY_INVALID);
    ctx.player_record_bytes=16u;
    put16(colony+0xB4u+2u,100u);
    require(moo2_v131_derived_single_entry_bomb(&ctx,1,&returned)
        ==MOO2_V131_SINGLE_ENTRY_INVALID);
    puts("PASS: all 65536 original signed defense WORD states, 16 entry indices, callback order and branch guards");
    return 0;
}
