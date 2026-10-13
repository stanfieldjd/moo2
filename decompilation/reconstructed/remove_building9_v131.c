/*
 * Source-derived MOO2 v1.31 Remove_Building_ building-ID-9 branch.
 * NOT original MicroProse source or the full 493-byte Remove_Building_.
 *
 * Original executable SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Original CODE:
 *   0x45F2 MOV ECX,EAX         (colony ID)
 *   0x45F4 MOV EBX,EDX         (building ID)
 *   0x45F6 MOVSX EDX,AX
 *   0x45F9 IMUL EAX,EDX,0x169
 *   0x45FF MOV ESI,DWORD PTR DS:[_colony]
 *   0x4605 ADD EAX,ESI
 *   0x4607 MOVSX ESI,BX
 *   0x460A MOV BYTE PTR [ESI+EAX+0x136],0
 *   0x4662 CMP BX,9; 0x4666 JBE 0x4674 in the 9..14 subrange
 *   0x4674 MOVSX EAX,BYTE PTR [EAX] (colony owner)
 *   EDX still holds sign-extended colony ID from 0x45F6.
 *   0x4677 CALL Assign_New_Home_Planet_ (CODE 0xDCB65)
 *   0x467C JMP 0x45E4: shared LEAVE/POPs/RET from Add_Building_
 *
 * Other Remove_Building_ IDs have different branches. This helper is
 * *only* the original ID 9 path, where it clears original colony+0x13F
 * and passes sign-extended owner byte AND excluded colony ID to the call. Host index
 * and callback validation is deliberate non-DOS safety behavior.
 */
#include <stddef.h>
#include <stdint.h>
#include "remove_building_first_write_v131.h"

typedef void (*Moo2V131AssignHomePlanet)(
    void *opaque,int32_t signed_original_colony_owner,
    int32_t excluded_original_colony_id);

typedef enum {
    MOO2_V131_REMOVE_BUILDING9_OK=0,
    MOO2_V131_REMOVE_BUILDING9_INVALID=1
} Moo2V131RemoveBuilding9Status;

/* Precondition building ID = 9 is intrinsic to this typed entry.
 * The actual original function receives building ID in EDX. */
Moo2V131RemoveBuilding9Status moo2_v131_derived_remove_building9(
    uint8_t *colonies,size_t colony_count,int16_t colony_id,
    Moo2V131AssignHomePlanet assign_new_home_planet,void *opaque)
{
    if(!colonies || !assign_new_home_planet ||
       colony_id<0 || (size_t)colony_id>=colony_count)
        return MOO2_V131_REMOVE_BUILDING9_INVALID;

    uint8_t *colony=colonies+(size_t)colony_id*0x169u;
    if(moo2_v131_derived_remove_building_first_write(
          colonies,colony_count,colony_id,9)!=MOO2_V131_BUILDING_FIRST_WRITE_OK)
        return MOO2_V131_REMOVE_BUILDING9_INVALID;

    int32_t owner=colony[0]<128u ?
        (int32_t)colony[0] : (int32_t)colony[0]-256;
    assign_new_home_planet(opaque,owner,(int32_t)colony_id);
    return MOO2_V131_REMOVE_BUILDING9_OK;
}
