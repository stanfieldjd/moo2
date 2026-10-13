/*
 * BOUNDED original v1.31 Remove_Building_ IDs 3,14,45,
 * the direct star-colony recalculation branch.
 * This does NOT implement the entire 493-byte Remove_Building_ body;
 * ID8/40/41 reach the same recalculation only AFTER queue cleanups,
 * so are deliberately not accepted by this helper.
 *
 * Original Watcom CODE:
 * 0x460A clears _colony[colony_id].building_flag[building_id].
 * 0x466E / 0x4668 / 0x4636 compare original building IDs 3/14/45
 * and branch at 0x463A directly to CODE 0x46D4.
 * 0x46D4..0x46E2 read signed colony ID (CX) and signed WORD
 * original colony+0x02 = planet ID; multiply by 17.
 * 0x46EA..0x46F4 read _planet[planet_id].BYTE+0x02,
 * unsigned STAR index; multiply by 113.
 * 0x46F7..0x46FF resolve _star[star_index] pointer and call
 * Compute_Star_Colony_Stuff_ (CODE 0xD5296).
 * 0x4704 checks original building ID 45, only then
 * 0x470E..0x4717 reads signed colony owner BYTE+0 and calls
 * Update_Ship_ETAs_ (CODE 0xF041C).
 * Return via shared LEAVE/POPs/RET at CODE 0x45E4.
 *
 * This helper preserves actual source read/write/callback sequence
 * but uses caller-owned original-format buffers, explicit callbacks,
 * and bounds checking not performed by original DOS.
 */
#include <stddef.h>
#include <stdint.h>
#include "remove_building_first_write_v131.h"

typedef void (*Moo2V131RecomputeStarStuff)(
    void *opaque,uint8_t *original_star_record);
typedef void (*Moo2V131UpdateShipEta)(
    void *opaque,int32_t original_colony_owner);

typedef struct {
    uint8_t *colonies;
    size_t colony_count;
    const uint8_t *planets;
    size_t planet_count;
    uint8_t *stars;
    size_t star_count;
    Moo2V131RecomputeStarStuff compute_star;
    Moo2V131UpdateShipEta update_ship_etas;
    void *opaque;
} Moo2V131BuildingStarRecalcContext;

typedef enum {
    MOO2_V131_BUILDING_STAR_RECALC_OK=0,
    MOO2_V131_BUILDING_STAR_RECALC_UNSUPPORTED_ID=1,
    MOO2_V131_BUILDING_STAR_RECALC_INVALID=2
} Moo2V131BuildingStarRecalcStatus;

Moo2V131BuildingStarRecalcStatus
moo2_v131_derived_remove_building_star_recalc(
    Moo2V131BuildingStarRecalcContext *ctx,int16_t colony_id,
    int16_t original_building_id)
{
    if(original_building_id!=3 && original_building_id!=14 &&
       original_building_id!=45)
        return MOO2_V131_BUILDING_STAR_RECALC_UNSUPPORTED_ID;
    if(!ctx || !ctx->colonies || !ctx->planets || !ctx->stars ||
       !ctx->compute_star ||
       (original_building_id==45 && !ctx->update_ship_etas) ||
       colony_id<0 || (size_t)colony_id>=ctx->colony_count)
        return MOO2_V131_BUILDING_STAR_RECALC_INVALID;

    uint8_t *colony=ctx->colonies+(size_t)colony_id*0x169u;
    uint16_t planet_bits=(uint16_t)((uint16_t)colony[2]|
                                    ((uint16_t)colony[3]<<8));
    int32_t planet_id=planet_bits<UINT16_C(0x8000)
        ? (int32_t)planet_bits : (int32_t)planet_bits-65536;
    if(planet_id<0 || (size_t)planet_id>=ctx->planet_count)
        return MOO2_V131_BUILDING_STAR_RECALC_INVALID;

    const uint8_t *planet=ctx->planets+(size_t)planet_id*0x11u;
    const uint8_t star_id=planet[2];
    if((size_t)star_id>=ctx->star_count)
        return MOO2_V131_BUILDING_STAR_RECALC_INVALID;
    uint8_t *star=ctx->stars+(size_t)star_id*0x71u;

    if(moo2_v131_derived_remove_building_first_write(
        ctx->colonies,ctx->colony_count,colony_id,original_building_id)
        !=MOO2_V131_BUILDING_FIRST_WRITE_OK)
        return MOO2_V131_BUILDING_STAR_RECALC_INVALID;

    ctx->compute_star(ctx->opaque,star);
    if(original_building_id==45) {
        /* Read owner BYTE AFTER star callback, as source does. */
        int32_t owner=colony[0]<128u
            ?(int32_t)colony[0]:(int32_t)colony[0]-256;
        ctx->update_ship_etas(ctx->opaque,owner);
    }
    return MOO2_V131_BUILDING_STAR_RECALC_OK;
}
