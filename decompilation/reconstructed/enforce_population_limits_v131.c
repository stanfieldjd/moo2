/*
 * Master of Orion II v1.31 source-derived 489-byte Watcom
 * Enforce_Population_Limits_At_Colony_ (original CODE 0xDC97C).
 * Original ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Original complete named body SHA256:
 * 6e728e998d84105e2a3004ad1809c94ea1acf201db4ab907a6a935be54b92845
 *
 * External original function effects explicitly provided via callback:
 * Colony_Race_Pop_Limit_ CODE 0xD0C1D, Shuffle_ CODE 0xEEA82,
 * Colony_Food2_Per_Farmer_ CODE 0xCE03E.
 * This recovers source-defined loop and copying/removal decision,
 * not those external functions' effects or a DOS differential run.
 *
 * Input is mutable colony record, at least 0x169 bytes.
 * Population count=BYTE+0x0A, four-byte population records+0x0C.
 * Population type = record DWORD & 15. Valid in-game low-nibble
 * classes are bounded here to 0..9 because Watcom allocates 10
 * signed-WORD capacities in 20 stack bytes.
 * Original first scan traverses the population in REVERSE, caches
 * the race-capacity for each distinct class, and marks an array
 * of 42 BYTE flags at index returned by capacity. It then calls
 * Shuffle_ on the population records (length=count, stride=4).
 * For each marked capacity t from 1 to 41:
 *   rescan in reverse and count entries whose class cap <=t;
 *   if count>t remove exactly ONE such entry, choosing a source
 *   priority among five group buckets, overwrite that entry
 *   with the LAST population DWORD, decrement colony+0x0A,
 *   then REPEAT until no excess entries remain for t.
 * Choice priority: type 9, non-owner match, owner-at-bits4..6 match,
 *                  type 8, type matching colony owner.
 * Repeated reverse scan selects the FIRST source-order occurrence
 * within the class as a result of overwriting the last pointer.
 * An original cap=0 mark is not scanned by original loop,
 * which starts at t=1. This behavior is intentionally preserved.
 *
 * After limits, call food-per-farmer with EBX=0 and owner signed
 * BYTE+0; if returned AX==0, for all remaining population records
 * in reverse: when WORD&0x0180==0 and class!=8, replace low WORD
 * with (word & 0xFE7F)|0x0080. Other two bytes are unchanged.
 *
 * Host bounds/callback failure detection differs from original DOS
 * potentially corrupt states. The host API does not rollback prior
 * population mutations when a callback fails mid-call.
 */
#include <stddef.h>
#include <stdint.h>
#include "enforce_population_limits_v131.h"

static uint32_t moo2_v131_pop_load(const uint8_t *p) {
    return (uint32_t)p[0] | (uint32_t)p[1]<<8 |
           (uint32_t)p[2]<<16 | (uint32_t)p[3]<<24;
}
static void moo2_v131_pop_store(uint8_t *p,uint32_t value) {
    p[0]=(uint8_t)value;p[1]=(uint8_t)(value>>8);
    p[2]=(uint8_t)(value>>16);p[3]=(uint8_t)(value>>24);
}
Moo2V131PopLimitResult moo2_v131_derived_enforce_population_limits(
    const Moo2V131PopLimitContext *ctx,uint8_t *colony,size_t colony_bytes)
{
    if(!ctx || !ctx->race_capacity || !ctx->shuffle ||
       !ctx->food_per_farmer || !colony || colony_bytes<0x169u)
        return MOO2_V131_POPLIMIT_INVALID;
    size_t count=(size_t)colony[0x0Au];
    if(count>42u || 0x0Cu+4u*count>colony_bytes || colony[0]>7u)
        return MOO2_V131_POPLIMIT_INVALID;
    uint8_t *const first=colony+0x0Cu;
    int16_t limit[10];
    uint8_t flagged[42]={0};
    for(unsigned k=0;k<10u;k++)limit[k]=-1;
    for(size_t i=count;i>0u;i--) {
        uint32_t record=moo2_v131_pop_load(first+(i-1u)*4u);
        unsigned type=(unsigned)(record&0xFu);
        if(type>=10u)return MOO2_V131_POPLIMIT_INVALID;
        if(limit[type]!=-1)continue;
        int16_t value=0;
        if(!ctx->race_capacity(ctx->opaque,colony,(uint8_t)type,&value))
            return MOO2_V131_POPLIMIT_CALLBACK_FAILED;
        if(value<0 || value>=42)
            return MOO2_V131_POPLIMIT_INVALID;
        limit[type]=value;
        flagged[(unsigned)value]=1u;
    }
    if(!ctx->shuffle(ctx->opaque,first,count,4u))
        return MOO2_V131_POPLIMIT_CALLBACK_FAILED;

    /* The original uses 32-bit signed comparisons for threshold and
       count, and recomputes all candidate buckets after each deletion.
       The host loop is bounded by 42 entries / 41 thresholds. */
    for(unsigned threshold=1u;threshold<42u;threshold++) {
        if(!flagged[threshold])continue;
        for(;;) {
            size_t num_qualifying=0u;
            size_t priority9=SIZE_MAX, priority_other=SIZE_MAX,
                   priority_ownerbits=SIZE_MAX,priority8=SIZE_MAX,
                   priority_ownerclass=SIZE_MAX;
            count=(size_t)colony[0x0Au];
            if(count>42u)return MOO2_V131_POPLIMIT_INVALID;
            for(size_t i=count;i>0u;i--) {
                const size_t slot=i-1u;
                uint32_t record=moo2_v131_pop_load(first+4u*slot);
                unsigned type=(unsigned)(record&0xFu);
                if(type>=10u || limit[type]<0)
                    return MOO2_V131_POPLIMIT_INVALID;
                if(limit[type]>(int16_t)threshold)continue;
                num_qualifying++;
                if(type==9u)priority9=slot;
                else if(type==8u)priority8=slot;
                else if((int32_t)(int8_t)colony[0]==(int32_t)type)
                    priority_ownerclass=slot;
                else if((int32_t)(int8_t)colony[0]==
                        (int32_t)((record>>4)&7u))
                    priority_ownerbits=slot;
                else priority_other=slot;
            }
            if(num_qualifying<=threshold)
                break;
            size_t victim=priority9!=SIZE_MAX?priority9:
                          priority_other!=SIZE_MAX?priority_other:
                          priority_ownerbits!=SIZE_MAX?priority_ownerbits:
                          priority8!=SIZE_MAX?priority8:
                          priority_ownerclass;
            if(victim==SIZE_MAX || count==0u)
                return MOO2_V131_POPLIMIT_INVALID;
            colony[0x0Au]=(uint8_t)(count-1u);
            moo2_v131_pop_store(first+victim*4u,
                               moo2_v131_pop_load(first+(count-1u)*4u));
        }
    }
    int16_t food=0;
    if(!ctx->food_per_farmer(ctx->opaque,colony,(int8_t)colony[0],&food))
        return MOO2_V131_POPLIMIT_CALLBACK_FAILED;
    if(food==0) {
        count=(size_t)colony[0x0Au];
        for(size_t i=count;i>0;i--) {
            uint8_t *entry=first+(i-1u)*4u;
            const uint32_t record=moo2_v131_pop_load(entry);
            if((record&UINT32_C(0x180))==0u &&
               (record&0xFu)!=8u) {
                const uint32_t replacement=
                    (record&UINT32_C(0xFFFFFE7F))|UINT32_C(0x80);
                moo2_v131_pop_store(entry,replacement);
            }
        }
    }
    return MOO2_V131_POPLIMIT_OK;
}
