/*
 * DERIVED original v1.31 Apply_Damage_To_Planet_ bounded sub-expression.
 * Not a complete planet-damage function or original MicroProse C source.
 *
 * Source authenticated original ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Original CODE 0x2A4EF..0x2A517:
 *   MOV EDX,7; XOR EAX,EAX; CALL Does_Combat_Ship_Have_Special_;
 *   CMP AX,1; JNE 0x2A517
 *   MOV AX,WORD [ECX]; CWD; SHL DX,2; SBB AX,DX; SAR AX,2;
 *   MOV WORD [ECX],AX; DEC WORD [ECX].
 *
 * The original special-7 path takes a signed 16-bit candidate damage
 * and computes trunc_toward_zero(damage/4) - 1 modulo 65536.
 * This independently reconstructs only that arithmetic. It deliberately
 * takes 'has_special7' as input; it does not call the original game helper,
 * set original globals, trigger bio effects or change planet defense state.
 */
#include <stdint.h>

typedef enum {
    MOO2_V131_PLANET_SPECIAL_OK=0,
    MOO2_V131_PLANET_SPECIAL_INVALID_POINTER=1
} Moo2V131PlanetSpecialStatus;

static int32_t moo2_v131_planet_signed16(uint16_t word)
{
    return word < UINT16_C(0x8000)
        ? (int32_t)word : (int32_t)word-65536;
}

Moo2V131PlanetSpecialStatus moo2_v131_derived_apply_special7_adjustment(
    uint16_t *damage_word,uint16_t original_special_query_result)
{
    if (!damage_word)return MOO2_V131_PLANET_SPECIAL_INVALID_POINTER;
    if (original_special_query_result!=1u)
        return MOO2_V131_PLANET_SPECIAL_OK;

    const int32_t signed_value=moo2_v131_planet_signed16(*damage_word);
    const int32_t quarter=signed_value/4; /* CWD/SHL/SBB/SAR = toward zero */
    /* Original DEC WORD wraps for a zero quotient: 0 -> 0xFFFF. */
    *damage_word=(uint16_t)((uint32_t)(quarter-1) & UINT32_C(0xFFFF));
    return MOO2_V131_PLANET_SPECIAL_OK;
}
