/*
 * Bounded original source-derived v1.31 Remove_Building_ IDs 15,24,28.
 * This does NOT implement the full Remove_Building_ nor full economy.
 * Authenticated source ORION2.EXE:
 * SHA256 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Watcom CODE 0x45EA..0x47D6, 493 bytes.
 *
 * 1. CODE 0x460A always clears building presence:
 *      _colony[colony_id].BYTE[0x136+building_id] = 0
 * 2. ID15 dispatches directly to common CODE 0x47AA.
 *    IDs24,28 enter at CODE 0x477A, look up signed colony
 *    planet ID WORD+2 in _planet (17-byte stride), compare BYTE+8
 *    to 2 (unsigned). Only when status <2, source calls
 *    Delete_Prod_From_Colony_Queue_(colony_id,44) at CODE 0x47A5.
 * 3. Original Delete_Prod ... at 0xA206F repeatedly calls
 *    First_Prod_Colony_Queue_Slot_(colony,44) (0xA1C5D), deletes
 *    the first exact queue WORD ==44, and repeats until missing.
 *    Direct Delete_From_Colony_Queue_(colony,slot) compacts the
 *    seven queue WORDs and re-compacts -10 placeholders at slot.
 *    Value 44 is NOT a ship encoding, so no _ship state write.
 * 4. Common CODE 0x47AA invokes in exact order:
 *      Colony_Environmental_Stuff_(colony pointer) at 0xD1CED;
 *      Enforce_Population_Limits_At_Colony_(colony pointer) 0xDC97C;
 *      Colony_Calculation_(colony index) 0xD2A70.
 *    The first two original functions preserve EDX via
 *    save/restore, so CODE 0x47CB MOV EAX,EDX passes
 *    the original colony index to the third.
 *
 * The latter three larger original named function effects
 * remain explicit callbacks. Callback failures are surfaced
 * without rollback; original DOS functions do not report
 * these host validation errors.
 */
#include <stddef.h>
#include <stdint.h>
#include "remove_building_first_write_v131.h"

typedef int (*Moo2V131ColonyStep)(
    void *opaque,uint8_t *original_colony);
typedef int (*Moo2V131ColonyRecalculate)(
    void *opaque,int16_t original_colony_id);
typedef struct {
    uint8_t *colonies;
    size_t colony_count;
    const uint8_t *planets;
    size_t planet_count;
    Moo2V131ColonyStep environmental;
    Moo2V131ColonyStep population_limits;
    Moo2V131ColonyRecalculate colony_calculation;
    void *opaque;
} Moo2V131BuildingEnvironmentContext;
typedef enum {
    MOO2_V131_BUILDING_ENV_OK=0,
    MOO2_V131_BUILDING_ENV_UNSUPPORTED_ID=1,
    MOO2_V131_BUILDING_ENV_INVALID=2,
    MOO2_V131_BUILDING_ENV_CALLBACK_FAILED=3
} Moo2V131BuildingEnvironmentStatus;

static int32_t moo2_v131_environment_s16(const uint8_t *p)
{
    uint16_t bits=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return bits<32768u?(int32_t)bits:(int32_t)bits-65536;
}
static void moo2_v131_environment_put16(uint8_t *p,int32_t n)
{
    uint16_t val=(uint16_t)n;
    p[0]=(uint8_t)val;
    p[1]=(uint8_t)(val>>8);
}
/* Source direct specialization of the original
 * Delete_Prod_From_Colony_Queue_(colony,44) and original anonymous
 * colony-specific compaction routine CODE 0xA20ED.
 * Source first-queue search uses an exact WORD+0x115 comparison
 * for a positive product 44, independent of negative ship records.
 */
static size_t moo2_v131_environment_delete_production_44(uint8_t *colony)
{
    size_t count=0u;
    for(;;) {
        unsigned slot=0u;
        for(;slot<7u;slot++) {
            if(moo2_v131_environment_s16(
                    colony+0x115u+2u*slot)==44)
                break;
        }
        if(slot==7u)
            break;
        /* Delete_From_Colony_Queue_(colony,slot), for positive
           product ID44, invokes anonymous 0xA20ED compactor.
           A negative -10 moved into the removed slot is compacted
           again until this slot no longer holds -10. */
        for(;;) {
            for(unsigned j=slot;j<6u;j++) {
                uint8_t *a=colony+0x115u+2u*j;
                a[0]=a[2];
                a[1]=a[3];
            }
            moo2_v131_environment_put16(colony+0x121u,-1);
            if(moo2_v131_environment_s16(
                colony+0x115u+2u*slot)!=-10)
                break;
        }
        count++;
    }
    return count;
}
Moo2V131BuildingEnvironmentStatus
moo2_v131_derived_remove_building_environment(
    Moo2V131BuildingEnvironmentContext *ctx,
    int16_t colony_id,int16_t building_id,
    size_t *removed_product_44)
{
    if(building_id!=15 && building_id!=24 && building_id!=28)
        return MOO2_V131_BUILDING_ENV_UNSUPPORTED_ID;
    if(!ctx || !ctx->colonies || !ctx->environmental ||
       !ctx->population_limits || !ctx->colony_calculation ||
       colony_id<0 || (size_t)colony_id>=ctx->colony_count)
        return MOO2_V131_BUILDING_ENV_INVALID;

    uint8_t *colony=ctx->colonies+(size_t)colony_id*0x169u;
    int remove_product=0;
    if(building_id!=15) {
        if(!ctx->planets)
            return MOO2_V131_BUILDING_ENV_INVALID;
        int32_t planet_id=moo2_v131_environment_s16(colony+2u);
        if(planet_id<0 || (size_t)planet_id>=ctx->planet_count)
            return MOO2_V131_BUILDING_ENV_INVALID;
        const uint8_t *planet=ctx->planets+(size_t)planet_id*0x11u;
        remove_product=(planet[0x08u]<2u);
    }
    if(moo2_v131_derived_remove_building_first_write(
        ctx->colonies,ctx->colony_count,colony_id,building_id)
        !=MOO2_V131_BUILDING_FIRST_WRITE_OK)
        return MOO2_V131_BUILDING_ENV_INVALID;

    size_t removed=remove_product ?
        moo2_v131_environment_delete_production_44(colony) : 0u;
    if(removed_product_44)*removed_product_44=removed;

    if(!ctx->environmental(ctx->opaque,colony) ||
       !ctx->population_limits(ctx->opaque,colony) ||
       !ctx->colony_calculation(ctx->opaque,colony_id))
        return MOO2_V131_BUILDING_ENV_CALLBACK_FAILED;
    return MOO2_V131_BUILDING_ENV_OK;
}
