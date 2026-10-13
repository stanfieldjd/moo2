/*
 * BOUNDED FIRST WRITE of original MOO2 v1.31 Remove_Building_.
 *
 * Original CODE 0x45EA, function body length 493 bytes;
 * entire body SHA256 8e0eb8d52268bf214d1ce3ec73d0e9970f0b4db1b0d1cae035810ace87179875.
 * Original executable SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Watcom original:
 * 0x45F6 MOVSX EDX,AX
 * 0x45F9 IMUL EAX,EDX,0x169
 * 0x45FF MOV ESI,[DS:_colony] (DATA offset 0x1AB18)
 * 0x4605 ADD EAX,ESI
 * 0x4607 MOVSX ESI,BX
 * 0x460A MOV BYTE PTR [ESI+EAX+0x136],0
 *
 * The remainder of the 493-byte routine handles race/economy/colony
 * and building-dependent effects. It is NOT implemented by this helper.
 * This C function makes ONLY the first verified building-presence
 * byte clear and imposes host bounds checks absent from original DOS.
 */
#include "remove_building_first_write_v131.h"

Moo2V131BuildingFirstWriteStatus
moo2_v131_derived_remove_building_first_write(
    uint8_t *colonies,size_t colony_count,
    int16_t colony_id,int16_t building_id)
{
    if(!colonies || colony_id<0 || (size_t)colony_id>=colony_count ||
       building_id<0 || building_id>=49)
        return MOO2_V131_BUILDING_FIRST_WRITE_INVALID;
    colonies[(size_t)colony_id*0x169u+0x136u+(size_t)building_id]=0u;
    return MOO2_V131_BUILDING_FIRST_WRITE_OK;
}
