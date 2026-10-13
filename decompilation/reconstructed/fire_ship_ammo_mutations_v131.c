/*
 * Isolated DERIVED v1.31 Fire_Ship_ ammunition slot WRITE semantics.
 * NOT the original source and NOT a firing engine.
 *
 * Original authenticated ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Original Watcom CODE:
 *  Fire_Ship_ 0x28B5E (2216 bytes, full routine NOT reconstructed)
 *  missile path: 0x28F85 calls Fire_Missile_,
 *   0x28F95 checks the weapon category == 2; 0x28FB5 writes slot+0x58 from
 *   _weapons[weapon_id].byte+0x0D if category == 2, otherwise 0x28FC3 DEC WORD.
 *  bomb path: 0x290EE calls Fire_Bomb_, then 0x2910C DEC WORD.
 *
 * These helpers ONLY perform the identified slot mutations; they do not
 * call Fire_Missile_/Fire_Bomb_, model effects, or decide if a shot is valid.
 * Original code has no additional pointer validation. Host safety checks
 * below are deliberate differences from the original DOS executable.
 */
#include <stdint.h>
#include <stddef.h>

typedef enum {
    MOO2_V131_FIRE_SLOT_OK = 0,
    MOO2_V131_FIRE_SLOT_INVALID = 1
} Moo2V131FireSlotStatus;

static uint16_t moo2_v131_fire_u16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static void moo2_v131_fire_write_u16(uint8_t *p,uint16_t v) {
    p[0]=(uint8_t)v;
    p[1]=(uint8_t)(v>>8);
}

static int32_t moo2_v131_fire_s16(const uint8_t *p) {
    const uint16_t v=moo2_v131_fire_u16(p);
    return v < UINT16_C(0x8000) ? (int32_t)v : ((int32_t)v-65536);
}

static Moo2V131FireSlotStatus moo2_v131_fire_get_counter(
    uint8_t *combat_ship,size_t ship_record_bytes,int16_t slot,
    uint8_t **counter_ptr,uint8_t **slot_ptr)
{
    if (!combat_ship || !counter_ptr || !slot_ptr || slot<0 || slot>=8 ||
        ship_record_bytes<0x139u)
        return MOO2_V131_FIRE_SLOT_INVALID;
    *slot_ptr=combat_ship+0x52u+(size_t)slot*11u;
    *counter_ptr=combat_ship+0x58u+(size_t)slot*11u;
    return MOO2_V131_FIRE_SLOT_OK;
}

/*
 * Original missile path AFTER Fire_Missile_ side effects.
 * [EBP-0x14] is the category byte from _weapons[weapon_id]+0x0C,\n * widened to a stored DWORD (later consumed as WORD); category 2 rewrites\n * the slot counter, categories 1 and 4 decrement in their missile paths.
 */
Moo2V131FireSlotStatus moo2_v131_derived_after_fire_missile_slot_write(
    uint8_t *combat_ship,size_t ship_record_bytes,int16_t slot,
    uint16_t weapon_category,const uint8_t *weapon_definitions,
    size_t weapon_definition_count)
{
    uint8_t *count,*item;
    if(moo2_v131_fire_get_counter(combat_ship,ship_record_bytes,slot,
                                  &count,&item)!=MOO2_V131_FIRE_SLOT_OK)
        return MOO2_V131_FIRE_SLOT_INVALID;
    if(weapon_category==2u) {
        const int32_t weapon_id=moo2_v131_fire_s16(item);
        if(!weapon_definitions || weapon_id<0 ||
           (size_t)weapon_id>=weapon_definition_count)
            return MOO2_V131_FIRE_SLOT_INVALID;
        /* 0x28FAD: BYTE PTR [_weapons + 28*id + 0x0D] -> DX.
         * 0x28FB5: MOV WORD [slot + 0x58], DX, zero extended. */
        const uint8_t new_value=weapon_definitions[(size_t)weapon_id*28u+13u];
        moo2_v131_fire_write_u16(count,(uint16_t)new_value);
    } else {
        /* Original 0x28FC3: DEC WORD; intentional modulo-65536 wrap. */
        const uint16_t prior=moo2_v131_fire_u16(count);
        moo2_v131_fire_write_u16(count,(uint16_t)(prior-1u));
    }
    return MOO2_V131_FIRE_SLOT_OK;
}

/* Original bomb path AFTER Fire_Bomb_: 0x2910C DEC WORD of slot+0x58. */
Moo2V131FireSlotStatus moo2_v131_derived_after_fire_bomb_slot_write(
    uint8_t *combat_ship,size_t ship_record_bytes,int16_t slot)
{
    uint8_t *count,*item;
    if(moo2_v131_fire_get_counter(combat_ship,ship_record_bytes,slot,
                                  &count,&item)!=MOO2_V131_FIRE_SLOT_OK)
        return MOO2_V131_FIRE_SLOT_INVALID;
    (void)item;
    const uint16_t prior=moo2_v131_fire_u16(count);
    moo2_v131_fire_write_u16(count,(uint16_t)(prior-1u));
    return MOO2_V131_FIRE_SLOT_OK;
}
