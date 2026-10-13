/*
 * ISOLATED original v1.31 Resolve_Bomb_Hit_ special single-entry branch.
 * Original CODE 0xCCF56..0xCCFEE in authenticated ORION2.EXE
 * SHA256 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f.
 * This is DERIVED C, not original MicroProse source.
 *
 * This subpath is reached when unsigned colony entry count+0x0A==1
 * AND all other original target-group weights sum to zero.
 * Source 0xCCF6A reads lone colony entry DWORD low nibble and
 * indexes signed defense WORD colony+0xB4+2*(entry&0xF).
 * If defense > 100 (signed), source 0xCCFDD subtracts 100.
 * Else 0xCCF7E..0xCCFDB:
 *  ++event WORD+0x0C; defense=0; colony count BYTE+0x0A=0;
 *  if colony BYTE+0x13F !=0 call Remove_Building_ with EDX=9
 *      and EAX=colony index (derived from pointer difference/0x169);
 *  event BYTE+0x42=1; owner-v-opponent player WORD+0x6FF +=10.
 * Both branch outcomes set event BYTE+0x41=1 and EAX=1.
 *
 * Remove_Building_ CODE 0x45EA remains a REAL CALLBACK with effects
 * not yet reconstructed. Selection of this subpath is checked but all
 * surrounding ordinary-bomb resolver branches are NOT reproduced.
 * Host guards (invalid IDs, buffers, missing callback) are extra safety,
 * not original DOS behavior.
 */
#include <stddef.h>
#include <stdint.h>
#include "colony_hit_player_stats_v131.h"

typedef void (*Moo2V131RemoveBuilding9)(
    void *opaque,int16_t colony_index,uint16_t building_id);

typedef struct {
    uint8_t *colony_records;
    size_t colony_record_count;
    uint8_t *result_event;
    size_t result_event_size;
    uint8_t *player_records;
    size_t player_record_bytes;
    Moo2V131RemoveBuilding9 remove_building;
    void *opaque;
} Moo2V131SingleEntryBombContext;

typedef enum {
    MOO2_V131_SINGLE_ENTRY_OK=0,
    MOO2_V131_SINGLE_ENTRY_NOT_APPLICABLE=1,
    MOO2_V131_SINGLE_ENTRY_INVALID=2
} Moo2V131SingleEntryBombStatus;

static uint16_t moo2_v131_single_read16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}
static void moo2_v131_single_write16(uint8_t *p,uint16_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
static int32_t moo2_v131_single_signed16(const uint8_t *p) {
    uint16_t v=moo2_v131_single_read16(p);
    return v<UINT16_C(0x8000)?(int32_t)v:(int32_t)v-65536;
}
static int moo2_v131_single_excluded(unsigned index) {
    return index==8u || index==9u || index==26u || index==27u
        || index==40u || index==41u || index==42u || index==47u;
}

Moo2V131SingleEntryBombStatus moo2_v131_derived_single_entry_bomb(
    const Moo2V131SingleEntryBombContext *ctx,int16_t colony_id,
    uint32_t *original_eax_result)
{
    if(!ctx || !original_eax_result || !ctx->colony_records ||
       !ctx->result_event || !ctx->player_records ||
       ctx->result_event_size<0x45u || colony_id<0 ||
       (size_t)colony_id>=ctx->colony_record_count)
        return MOO2_V131_SINGLE_ENTRY_INVALID;

    uint8_t *colony=ctx->colony_records+(size_t)colony_id*0x169u;
    uint8_t *event=ctx->result_event;
    if(colony[0x0Au]!=1u)
        return MOO2_V131_SINGLE_ENTRY_NOT_APPLICABLE;

    /* Original weighted categories: 49 filtered building flags, signed
       colony WORDs +0x130/+0x132, and nonzero +0x125 WORD.
       Only exact zero values here are admitted as a safe sufficient
       condition for the original aggregate weight to be zero. Negative
       / cancelling malformed counts are NOT accepted by this host API. */
    if(moo2_v131_single_read16(colony+0x130u)!=0u ||
       moo2_v131_single_read16(colony+0x132u)!=0u ||
       moo2_v131_single_read16(colony+0x125u)!=0u)
        return MOO2_V131_SINGLE_ENTRY_NOT_APPLICABLE;
    for(unsigned i=0u;i<49u;i++) {
        if(!moo2_v131_single_excluded(i) &&
           colony[0x136u+i]!=0u)
            return MOO2_V131_SINGLE_ENTRY_NOT_APPLICABLE;
    }

    const uint8_t entry_type=(uint8_t)(colony[0x0Cu]&0x0Fu);
    uint8_t *defense=colony+0xB4u+2u*(size_t)entry_type;
    int32_t remaining=moo2_v131_single_signed16(defense);

    if(remaining>100) {
        moo2_v131_single_write16(defense,(uint16_t)(remaining-100));
    } else {
        /* Original player stat uses signed BYTE colony[0], event[0],
           player record stride 0xEA9 and WORD offset 0x6FF+2*opponent.
           Reject invalid host indices BEFORE changing colony/event. */
        const int32_t owner=colony[0]<128u?(int32_t)colony[0]:
                            (int32_t)colony[0]-256;
        const int32_t opponent=event[0]<128u?(int32_t)event[0]:
                               (int32_t)event[0]-256;
        if(owner<0 || opponent<0)
            return MOO2_V131_SINGLE_ENTRY_INVALID;
        const size_t at=(size_t)owner*0xEA9u+0x6FFu+
                        2u*(size_t)opponent;
        if(ctx->player_record_bytes<2u ||
           at>ctx->player_record_bytes-2u ||
           (colony[0x13Fu]!=0u && !ctx->remove_building))
            return MOO2_V131_SINGLE_ENTRY_INVALID;
        moo2_v131_single_write16(
            event+0x0Cu,(uint16_t)(moo2_v131_single_read16(event+0x0Cu)+1u));
        moo2_v131_single_write16(defense,0u);
        colony[0x0Au]=0u;
        if(colony[0x13Fu]!=0u)
            ctx->remove_building(ctx->opaque,colony_id,9u);
        event[0x42u]=1u;
        if(moo2_v131_derived_colony_hit_owner_stat(
            ctx->player_records,ctx->player_record_bytes,
            colony,0x169u,event,ctx->result_event_size,
            MOO2_V131_OWNER_STAT_INCREMENT_TEN)!=MOO2_V131_OWNER_STAT_OK)
            return MOO2_V131_SINGLE_ENTRY_INVALID;
    }
    event[0x41u]=1u;
    *original_eax_result=1u;
    return MOO2_V131_SINGLE_ENTRY_OK;
}
