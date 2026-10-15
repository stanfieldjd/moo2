/*
 * DERIVED entire 311-byte original Watcom MOO2 v1.31
 * Compute_Star_Colony_Stuff_. NOT original MicroProse C.
 * Authenticated ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Original CODE 0xD5296..0xD53CC; complete body SHA256:
 * b599c172a8a790494eb319c9edd73c881f6fea26a6e708ebf75cd3feae9d1ee0.
 *
 * Source clears original star bytes +0x38,+0x39,+0x3B,+0x3C,
 * +0x3D,+0x3E,+0x3F,+0x40, then for each of FIVE planet slots
 * (WORD star+0x4A+2*i, i=4..0):
 *   -1: no planet; otherwise _planet[planet_id*0x11] WORD is colony ID;
 *   -1: uncolonized; otherwise _colony[colony_id*0x169] BYTE is owner ID.
 * Per owner, accumulate bit (1 << owner) into:
 *   star+0x38: all colonized planets;
 *   star+0x39: colony building flag +0x136+45 !=0;
 *   star+0x3B: (building flags +40/+8/+41 nonzero) and player+0x1CB==3;
 *   star+0x3C: same building condition and player+0x1C7==3;
 *   star+0x3F: colony building flag +3 !=0;
 *   star+0x40: colony building flag +14 !=0;
 *   star+0x3E: player BYTE+0x17A==3;
 *   star+0x3D: player BYTE+0x1C1==3.
 *
 * Original exit JMP 0xD1F97 to shared Watcom LEAVE/POPs/RET
 * after PUSH EBX ECX EDX ESI EDI; ENTER 8.
 * No external CALL instructions within the full 311-byte body.
 *
 * DOS assumes valid object indexes. Derived C preflights all referenced
 * record bounds and rejects non-player owner bytes before mutating star;
 * that is deliberate safety, not exact behavior on invalid DOS state.
 */
#include <stddef.h>
#include <stdint.h>
#include "compute_star_colony_stuff_v131.h"

static int32_t moo2_v131_star_s16(const uint8_t *p)
{
    uint16_t bits=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return bits<UINT16_C(0x8000)?(int32_t)bits:(int32_t)bits-65536;
}

Moo2V131StarColonyStatus moo2_v131_derived_compute_star_colony_stuff(
    const Moo2V131StarColonyContext *ctx,
    uint8_t *star,size_t star_bytes)
{
    if(!ctx || !star || star_bytes<0x71u ||
       !ctx->planets || !ctx->colonies || !ctx->players)
        return MOO2_V131_STAR_COLONY_INVALID;

    /* First preflight the full source pointer chain for atomic host
       failure. Read only five original star planet slots. */
    for(unsigned i=0;i<5u;i++) {
        int32_t planet_id=moo2_v131_star_s16(star+0x4Au+2u*i);
        if(planet_id==-1)continue;
        if(planet_id<0 || (size_t)planet_id>=ctx->planet_count)
            return MOO2_V131_STAR_COLONY_INVALID;
        const uint8_t *planet=ctx->planets+(size_t)planet_id*0x11u;
        int32_t colony_id=moo2_v131_star_s16(planet);
        if(colony_id==-1)continue;
        if(colony_id<0 || (size_t)colony_id>=ctx->colony_count)
            return MOO2_V131_STAR_COLONY_INVALID;
        const uint8_t *colony=ctx->colonies+(size_t)colony_id*0x169u;
        /* Original source uses signed owner BYTE for player indexes,
           and BL shifted by CL for bit flags. Normal game owners 0..7. */
        if(colony[0]>=8u || (size_t)colony[0]>=ctx->player_count)
            return MOO2_V131_STAR_COLONY_INVALID;
    }

    static const uint8_t fields[]={0x38u,0x39u,0x3Eu,0x3Du,
                                   0x3Bu,0x3Cu,0x3Fu,0x40u};
    for(size_t k=0;k<sizeof(fields);k++)star[fields[k]]=0u;

    for(unsigned remaining=5u;remaining>0u;remaining--) {
        const unsigned index=remaining-1u;
        int32_t planet_id=moo2_v131_star_s16(star+0x4Au+2u*index);
        if(planet_id==-1)continue;
        const uint8_t *planet=ctx->planets+(size_t)planet_id*0x11u;
        int32_t colony_id=moo2_v131_star_s16(planet);
        if(colony_id==-1)continue;
        const uint8_t *colony=ctx->colonies+(size_t)colony_id*0x169u;
        unsigned owner=colony[0];
        uint8_t bit=(uint8_t)(1u<<owner);
        const uint8_t *building=colony+0x136u;
        const uint8_t *player=ctx->players+(size_t)owner*0xEA9u;
        star[0x38u]|=bit;
        if(building[45u]!=0u)star[0x39u]|=bit;
        if(building[40u]!=0u || building[8u]!=0u || building[41u]!=0u) {
            if(player[0x1CBu]==3u)star[0x3Bu]|=bit;
            if(player[0x1C7u]==3u)star[0x3Cu]|=bit;
        }
        if(building[3u]!=0u)star[0x3Fu]|=bit;
        if(building[14u]!=0u)star[0x40u]|=bit;
        if(player[0x17Au]==3u)star[0x3Eu]|=bit;
        if(player[0x1C1u]==3u)star[0x3Du]|=bit;
    }
    return MOO2_V131_STAR_COLONY_OK;
}
