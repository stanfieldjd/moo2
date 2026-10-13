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
