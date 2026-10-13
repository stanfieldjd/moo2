/*
 * DERIVED Master of Orion II v1.31 combat weapon-state helpers.
 * Original CODE:
 *  Weapons_Left_ 0x26C60..0x26C9B (60 bytes)
 *  Weapon_Is_On_ 0x3584C..0x3586B (32 bytes)
 *  Weapon_Is_Off_ 0x3586C..0x3588B (32 bytes)
 *
 * Source authenticated original v1.31 executable:
 * SHA-256 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Derived semantics, not original MicroProse C.
 * Original input AX and DX use Watcom fastcall-style registers. The original
 * routines perform no host bounds checks. This port checks offsets and
 * zero divisor and reports invalid input separately: deliberate safety change.
 */
#include <stdint.h>
#include <stddef.h>
#include <limits.h>

typedef enum {
    MOO2_V131_WEAPON_HELPER_OK = 0,
    MOO2_V131_WEAPON_HELPER_INVALID_INPUT = 1,
    MOO2_V131_WEAPON_HELPER_ZERO_DIVISOR = 2
} Moo2V131WeaponHelperStatus;

static int16_t moo2_v131_weapon_s16(const uint8_t *p)
{
    const uint16_t v = (uint16_t)p[0] | (uint16_t)((uint16_t)p[1] << 8);
    return (int16_t)(v < UINT16_C(0x8000) ? (int32_t)v : (int32_t)v - 65536);
}

/*
 * Original Weapons_Left_: EAX = pointer to combat ship's record,
 * DX = signed 16-bit weapon-bank index.
 * ESI = signed WORD at base+0x104+2*index;
 * EDI = signed WORD at base+0x114+2*index.
 * Machine code computes signed ESI/EDI, then recomputes it to inspect
 * the remainder, incrementing quotient if ESI>0 AND remainder !=0.
 *
 * This is NOT equivalent to generic ceiling division for EDI<0:
 * 5/-2 => -2 (toward zero -2, then increments to -1). Actually
 * the original yields -1; preserve its exact branch behavior.
 * Zero divisor causes original x86 IDIV exception; derived C reports status.
 */
Moo2V131WeaponHelperStatus moo2_v131_derived_weapons_left(
    const uint8_t *record, size_t record_bytes,
    int16_t weapon_index, int32_t *out)
{
    if (!record || !out || weapon_index < 0)
        return MOO2_V131_WEAPON_HELPER_INVALID_INPUT;
    const size_t index=(size_t)weapon_index;
    if (index > (SIZE_MAX - 0x116u)/2u)
        return MOO2_V131_WEAPON_HELPER_INVALID_INPUT;
    const size_t at=2u*index;
    if (record_bytes<0x116u || at>record_bytes-0x116u)
        return MOO2_V131_WEAPON_HELPER_INVALID_INPUT;
    const int32_t n=moo2_v131_weapon_s16(record+0x104u+at);
    const int32_t d=moo2_v131_weapon_s16(record+0x114u+at);
    if (!d) return MOO2_V131_WEAPON_HELPER_ZERO_DIVISOR;
    const int32_t quotient=n/d;
    const int32_t remainder=n%d;
    *out=quotient+((remainder!=0 && n>0)?1:0);
    return MOO2_V131_WEAPON_HELPER_OK;
}

/* Original Weapon_Is_On_ and Weapon_Is_Off_ operate on a combat ship ID
 * in AX and a signed slot index in DX. They look at the status flag in
 * slot offset +8 (ship+0x5A+11*slot) and SETE AL / SETNE AL after
 * CMP BYTE PTR [...], 1. Original only guarantees the final AL,
 * not that all upper EAX bits form a normalized 32-bit boolean.
 * Derived interface returns a pure uint8_t boolean instead.
 */
static Moo2V131WeaponHelperStatus moo2_v131_weapon_flag(
    const uint8_t *ships,size_t ship_count,
    int16_t ship_index,int16_t weapon_index,
    uint8_t *flag)
{
    if (!ships || !flag || ship_index<0 || weapon_index<0 ||
        (size_t)ship_index>=ship_count || weapon_index>=8)
        return MOO2_V131_WEAPON_HELPER_INVALID_INPUT;
    const size_t off=(size_t)ship_index*0x139u +
                     0x5Au+(size_t)weapon_index*11u;
    *flag=ships[off];
    return MOO2_V131_WEAPON_HELPER_OK;
}

Moo2V131WeaponHelperStatus moo2_v131_derived_weapon_is_on(
    const uint8_t *ships,size_t ship_count,
    int16_t ship_index,int16_t weapon_index,uint8_t *out)
{
    uint8_t flag=0;
    Moo2V131WeaponHelperStatus st=
       moo2_v131_weapon_flag(ships,ship_count,ship_index,weapon_index,&flag);
    if(st!=MOO2_V131_WEAPON_HELPER_OK || !out) 
        return MOO2_V131_WEAPON_HELPER_INVALID_INPUT;
    *out=(uint8_t)(flag==1u);
    return MOO2_V131_WEAPON_HELPER_OK;
}

Moo2V131WeaponHelperStatus moo2_v131_derived_weapon_is_off(
    const uint8_t *ships,size_t ship_count,
    int16_t ship_index,int16_t weapon_index,uint8_t *out)
{
    uint8_t flag=0;
    Moo2V131WeaponHelperStatus st=
       moo2_v131_weapon_flag(ships,ship_count,ship_index,weapon_index,&flag);
    if(st!=MOO2_V131_WEAPON_HELPER_OK || !out)
        return MOO2_V131_WEAPON_HELPER_INVALID_INPUT;
    *out=(uint8_t)(flag!=1u);
    return MOO2_V131_WEAPON_HELPER_OK;
}
