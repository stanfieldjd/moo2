/*
 * BOUNDED source-derived v1.31 Remove_Building_ construction queue paths.
 * Not original MicroProse C, nor full 493-byte original function.
 *
 * Authenticated v1.31 CODE 0x4681..0x46D4:
 * building ID 8,40,41: loop 7 WORDs colony+0x115+2*i;
 *   if signed WORD <= -100: ship_index=-(word+100),
 *   _ship ship-record stride 0x81 (129), BYTE+0x10 >= 2:
 *      Delete_From_Colony_Queue_(colony_id,slot), --slot.
 *   Then shared parent-star recomputation 0x46D4..0x4708
 *   (IDs 8,40,41 never take ID45-only ETA update).
 *
 * Authenticated CODE 0x4721..0x4775:
 * building ID 22: same 7 queue positions and negative-ship encoding;
 *   delete only when ship BYTE+0x11 == 2;
 *   use original Delete_From_Colony_Queue_(colony_id,slot), --slot;
 *   then jump to shared return, NO star recomputation.
 *
 * Original function always clears the building flag +0x136+ID
 * FIRST at CODE 0x460A, before entering these branches.
 *
 * Source Delete_From_Colony_Queue_ itself modifies queue and ship
 * state and is kept as an explicit callback here. Callback must
 * actually shift/remove matching entries, or host loop will exit with
 * iteration-limit error (non-DOS safety guard).
 */
#include <stddef.h>
#include <stdint.h>
#include "remove_building_first_write_v131.h"

typedef int (*Moo2V131QueueDelete)(
    void *opaque,int16_t original_colony_id,int16_t queue_slot);
typedef void (*Moo2V131QueueStarCompute)(
    void *opaque,uint8_t *original_star_record);

typedef struct {
    uint8_t *colonies;
    size_t colony_count;
    const uint8_t *ships;
    size_t ship_count;
    const uint8_t *planets;
    size_t planet_count;
    uint8_t *stars;
    size_t star_count;
    Moo2V131QueueDelete delete_queue;
    Moo2V131QueueStarCompute compute_star;
    void *opaque;
    size_t max_deletions;
} Moo2V131QueueBuildingContext;

typedef enum {
    MOO2_V131_QUEUE_BUILDING_OK=0,
    MOO2_V131_QUEUE_BUILDING_UNSUPPORTED_ID=1,
    MOO2_V131_QUEUE_BUILDING_INVALID=2,
    MOO2_V131_QUEUE_BUILDING_ITERATION_LIMIT=3,
    MOO2_V131_QUEUE_BUILDING_CALLBACK_FAILED=4
} Moo2V131QueueBuildingStatus;

static int32_t moo2_v131_queue_read_signed_word(const uint8_t *ptr) {
    uint16_t bits=(uint16_t)((uint16_t)ptr[0]|
                             ((uint16_t)ptr[1]<<8));
    return bits<UINT16_C(0x8000)?(int32_t)bits:(int32_t)bits-65536;
}
Moo2V131QueueBuildingStatus moo2_v131_derived_remove_building_queue(
    Moo2V131QueueBuildingContext *ctx,
    int16_t colony_id,int16_t building_id,size_t *actual_deletions)
{
    if(building_id!=8 && building_id!=22 &&
       building_id!=40 && building_id!=41)
        return MOO2_V131_QUEUE_BUILDING_UNSUPPORTED_ID;
    if(!ctx || !ctx->colonies || !ctx->ships ||
       !ctx->delete_queue || !ctx->max_deletions ||
       colony_id<0 || (size_t)colony_id>=ctx->colony_count ||
       (building_id!=22 && (!ctx->planets || !ctx->stars ||
                             !ctx->compute_star)))
        return MOO2_V131_QUEUE_BUILDING_INVALID;

    uint8_t *colony=ctx->colonies+(size_t)colony_id*0x169u;
    if(moo2_v131_derived_remove_building_first_write(
           ctx->colonies,ctx->colony_count,colony_id,building_id)
          !=MOO2_V131_BUILDING_FIRST_WRITE_OK)
        return MOO2_V131_QUEUE_BUILDING_INVALID;

    size_t deleted=0;
    for(unsigned index=0u;index<7u;) {
        int32_t value=moo2_v131_queue_read_signed_word(
            colony+0x115u+2u*index);
        if(value<=-100) {
            const int32_t ship_id=-(value+100);
            if(ship_id<0 || (size_t)ship_id>=ctx->ship_count)
                return MOO2_V131_QUEUE_BUILDING_INVALID;
            const uint8_t *ship=ctx->ships+(size_t)ship_id*0x81u;
            int should_delete=building_id==22 ?
                ship[0x11u]==2u : ship[0x10u]>=2u;
            if(should_delete) {
                if(deleted>=ctx->max_deletions) {
                    if(actual_deletions)*actual_deletions=deleted;
                    return MOO2_V131_QUEUE_BUILDING_ITERATION_LIMIT;
                }
                if(!ctx->delete_queue(ctx->opaque,colony_id,(int16_t)index))
                    return MOO2_V131_QUEUE_BUILDING_CALLBACK_FAILED;
                deleted++;
                /* Source DEC SI then INC SI, so reassess this index
                   after callback has compacted the colony queue. */
                continue;
            }
        }
        index++;
    }
    if(actual_deletions)*actual_deletions=deleted;
    if(building_id!=22) {
        int32_t planet_id=moo2_v131_queue_read_signed_word(colony+2u);
        if(planet_id<0 || (size_t)planet_id>=ctx->planet_count)
            return MOO2_V131_QUEUE_BUILDING_INVALID;
        const uint8_t *planet=ctx->planets+(size_t)planet_id*0x11u;
        size_t star_id=planet[2u];
        if(star_id>=ctx->star_count)
            return MOO2_V131_QUEUE_BUILDING_INVALID;
        ctx->compute_star(ctx->opaque,ctx->stars+star_id*0x71u);
    }
    return MOO2_V131_QUEUE_BUILDING_OK;
}
