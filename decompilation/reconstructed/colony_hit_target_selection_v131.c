/*
 * DERIVED original Master of Orion II v1.31 hit-resolver selection helpers.
 * Original source is authenticated ORION2.EXE v1.31; this is NOT original C.
 *
 * Resolve_Biological_Hit_ (CODE 0xCD13E, 436 bytes), selector at
 * 0xCD146..0xCD185:
 *   colony+0x0A is an unsigned count N
 *   colony+0x0C+4*i is a DWORD species/population entry
 *   low nibble (entry & 0xF) == 8 is ineligible
 *   reverse-scan i=N-1..0; for eligible item j++, call Random_(j)
 *   and retain index i iff result EAX == 1 (reservoir sampling).
 *   If selected index stays -1, original branches at 0xCD185 to
 *   shared epilogue at 0xCCEB7 without executing effect logic.
 *
 * Resolve_Bomb_Hit_ (CODE 0xCCEBD, 641 bytes), selector
 * 0xCCEE4..0xCCF30:
 *   backward loop i=48..0 tests colony byte at +0x136+i !=0
 *   and explicitly excludes indices 9,26,27,42,47,8,40,41.
 *   Eligible indices accumulate in descending order into a local
 *   scratch byte buffer (original [EBP - 0x44]).
 *
 * Derived host bounds/invalid-argument returns are intentional modern
 * safety additions. Original DOS does not necessarily validate pointers,
 * slot capacities or lack of eligible targets.
 */
#include <stddef.h>
#include <stdint.h>
#include "random_v131.h"

typedef enum {
    MOO2_V131_HIT_SELECT_OK=0,
    MOO2_V131_HIT_SELECT_NONE=1,
    MOO2_V131_HIT_SELECT_INVALID=2,
    MOO2_V131_HIT_SELECT_RANDOM_ERROR=3
} Moo2V131HitSelectStatus;

Moo2V131HitSelectStatus moo2_v131_derived_bio_target_select(
    const uint8_t *colony,size_t colony_size,uint32_t *original_seed,
    int32_t *selected_index,uint32_t *eligible_count)
{
    if(!colony || !original_seed || !selected_index || !eligible_count ||
       colony_size<=0x0Au)
        return MOO2_V131_HIT_SELECT_INVALID;

    const size_t n=(size_t)colony[0x0Au];
    if(n>(SIZE_MAX-0x0Cu)/4u || colony_size<0x0Cu+4u*n)
        return MOO2_V131_HIT_SELECT_INVALID;
    uint32_t eligible=0;
    int32_t picked=-1;

    for(size_t p=n;p>0;p--) {
        const size_t index=p-1u;
        const uint8_t *entry=colony+0x0Cu+4u*index;
        /* Only low nibble of original DWORD is observed. */
        if((entry[0]&0x0Fu)==8u)
            continue;
        eligible++;
        uint32_t roll=0;
        if(moo2_v131_derived_random(original_seed,eligible,&roll)
           !=MOO2_V131_RANDOM_OK)
            return MOO2_V131_HIT_SELECT_RANDOM_ERROR;
        if(roll==1u)
            picked=(int32_t)index;
    }
    *selected_index=picked;
    *eligible_count=eligible;
    return picked>=0?MOO2_V131_HIT_SELECT_OK:MOO2_V131_HIT_SELECT_NONE;
}

/* Number of ordinary candidate slot positions in original loop. */
#define MOO2_V131_BOMB_SLOT_SCAN_COUNT 49u
#define MOO2_V131_BOMB_SLOT_BYTES_REQUIRED (0x136u+MOO2_V131_BOMB_SLOT_SCAN_COUNT)

static int moo2_v131_original_excluded_bomb_index(unsigned index)
{
    return index==9u || index==26u || index==27u || index==42u ||
           index==47u || index==8u || index==40u || index==41u;
}

/* Caller output capacity is checked before writing to avoid overflow.
 * Result indices are in descending original source scan order. */
Moo2V131HitSelectStatus moo2_v131_derived_bomb_eligible_indices(
    const uint8_t *colony,size_t colony_size,
    uint8_t *indices,size_t index_capacity,size_t *eligible_count)
{
    if(!colony || !indices || !eligible_count ||
       colony_size<MOO2_V131_BOMB_SLOT_BYTES_REQUIRED)
        return MOO2_V131_HIT_SELECT_INVALID;
    size_t count=0;
    for(unsigned p=MOO2_V131_BOMB_SLOT_SCAN_COUNT;p>0u;p--) {
        const unsigned index=p-1u;
        if(colony[0x136u+index]==0u ||
           moo2_v131_original_excluded_bomb_index(index))
            continue;
        if(count>=index_capacity)
            return MOO2_V131_HIT_SELECT_INVALID;
        indices[count++]=(uint8_t)index;
    }
    *eligible_count=count;
    return count?MOO2_V131_HIT_SELECT_OK:MOO2_V131_HIT_SELECT_NONE;
}


/*
 * Original Resolve_Bomb_Hit_ weighted draw from 0xCCF30 through
 * 0xCD102. This only chooses a target class; all actual colony,
 * player, tech, result-event, and population mutations remain
 * out of scope.
 *
 * Source weights:
 *   eligible non-excluded building indices (colony+0x136+i),
 *   signed WORD colony+0x130,
 *   signed WORD colony+0x132,
 *   one extra if signed WORD colony+0x125 !=0,
 *   and BYTE colony+0x0A ONLY if that byte !=1.
 * For colony+0x0A ==1 and total zero, original enters its
 * special first population entry treatment (0xCCF6A) without RNG.
 * For other total zero, original skips drawing.
 *
 * Original Random_(total) returns 1..total; LEA EBX,[EAX-1]
 * makes a zero-based position used for cumulative interval checks.
 * All signed-negative count inputs are rejected here as malformed
 * host state, not a simulation of original unsafe DOS behavior.
 */
typedef enum {
    MOO2_V131_BOMB_TARGET_NONE=0,
    MOO2_V131_BOMB_TARGET_BUILDING=1,
    MOO2_V131_BOMB_TARGET_POP_130=2,
    MOO2_V131_BOMB_TARGET_POP_132=3,
    MOO2_V131_BOMB_TARGET_COLONY_125=4,
    MOO2_V131_BOMB_TARGET_POP_ENTRY=5,
    MOO2_V131_BOMB_TARGET_SINGLE_ENTRY_SPECIAL=6
} Moo2V131BombTargetKind;

typedef struct {
    Moo2V131BombTargetKind kind;
    uint32_t total_weight;
    uint32_t zero_based_draw;
    uint32_t source_category_offset;
    uint8_t selected_building_index;
} Moo2V131BombWeightedSelection;

static int32_t moo2_v131_colony_target_signed_word(const uint8_t *p)
{
    uint16_t bits=(uint16_t)p[0]|((uint16_t)p[1]<<8);
    return bits<UINT16_C(0x8000)?(int32_t)bits:(int32_t)bits-65536;
}

Moo2V131HitSelectStatus moo2_v131_derived_bomb_weighted_target(
    const uint8_t *colony,size_t colony_size,uint32_t *original_seed,
    Moo2V131BombWeightedSelection *out)
{
    if(!colony || !original_seed || !out ||
       colony_size<MOO2_V131_BOMB_SLOT_BYTES_REQUIRED)
        return MOO2_V131_HIT_SELECT_INVALID;

    uint8_t eligible_slots[MOO2_V131_BOMB_SLOT_SCAN_COUNT]={0};
    size_t building_count=0;
    Moo2V131HitSelectStatus st=moo2_v131_derived_bomb_eligible_indices(
        colony,colony_size,eligible_slots,sizeof(eligible_slots),
        &building_count);
    if(st==MOO2_V131_HIT_SELECT_INVALID)
        return st;

    const int32_t n130=moo2_v131_colony_target_signed_word(colony+0x130u);
    const int32_t n132=moo2_v131_colony_target_signed_word(colony+0x132u);
    const int32_t extra=moo2_v131_colony_target_signed_word(colony+0x125u);
    if(n130<0 || n132<0)
        return MOO2_V131_HIT_SELECT_INVALID;

    uint32_t total=(uint32_t)building_count+(uint32_t)n130+(uint32_t)n132
                  +(extra!=0?1u:0u);
    const uint32_t population=(uint32_t)colony[0x0au];
    if(population==1u && total==0u) {
        out->kind=MOO2_V131_BOMB_TARGET_SINGLE_ENTRY_SPECIAL;
        out->total_weight=0u;
        out->zero_based_draw=0u;
        out->source_category_offset=0u;
        out->selected_building_index=0u;
        return MOO2_V131_HIT_SELECT_OK;
    }
    if(population!=1u)
        total+=population;

    out->total_weight=total;
    out->zero_based_draw=0u;
    out->source_category_offset=0u;
    out->selected_building_index=0u;
    if(total==0u) {
        out->kind=MOO2_V131_BOMB_TARGET_NONE;
        return MOO2_V131_HIT_SELECT_NONE;
    }

    uint32_t roll=0u;
    if(moo2_v131_derived_random(original_seed,total,&roll)!=
        MOO2_V131_RANDOM_OK)
        return MOO2_V131_HIT_SELECT_RANDOM_ERROR;
    const uint32_t draw=roll-1u;
    out->zero_based_draw=draw;

    uint32_t at=draw;
    if(at<(uint32_t)building_count) {
        out->kind=MOO2_V131_BOMB_TARGET_BUILDING;
        out->source_category_offset=at;
        out->selected_building_index=eligible_slots[at];
        return MOO2_V131_HIT_SELECT_OK;
    }
    at-=(uint32_t)building_count;
    if(at<(uint32_t)n130) {
        out->kind=MOO2_V131_BOMB_TARGET_POP_130;
        out->source_category_offset=at;
        return MOO2_V131_HIT_SELECT_OK;
    }
    at-=(uint32_t)n130;
    if(at<(uint32_t)n132) {
        out->kind=MOO2_V131_BOMB_TARGET_POP_132;
        out->source_category_offset=at;
        return MOO2_V131_HIT_SELECT_OK;
    }
    at-=(uint32_t)n132;
    if(extra!=0 && at==0u) {
        out->kind=MOO2_V131_BOMB_TARGET_COLONY_125;
        return MOO2_V131_HIT_SELECT_OK;
    }
    at-=(extra!=0?1u:0u);
    if(at<population && population!=1u) {
        out->kind=MOO2_V131_BOMB_TARGET_POP_ENTRY;
        out->source_category_offset=at;
        return MOO2_V131_HIT_SELECT_OK;
    }
    return MOO2_V131_HIT_SELECT_INVALID;
}
