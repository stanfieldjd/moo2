/* Original x86-derived special-7 planet damage arithmetic regression.
 * Exhaustive 65,536 signed 16-bit candidate words.
 * Reference models original CWD/SHL/SBB/SAR/DEC via separate bit arithmetic.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "../decompilation/reconstructed/planet_special7_damage_v131.c"

static void must(int ok) {
    if(!ok){fputs("FAIL original special-7 planet damage formula\n",stderr);exit(1);}
}
static uint16_t machine_reference(uint16_t original)
{
    /* CWD sign-extends AX into DX. SHL DX,2 leaves DX=0xFFFC
       and carry=1 for negative AX; zero otherwise. SBB subtracts both. */
    const int negative=(original & UINT16_C(0x8000))!=0;
    const uint32_t shifted_dx=negative?UINT32_C(0xFFFC):0u;
    const uint32_t carry=negative?1u:0u;
    const uint16_t result_after_sbb=(uint16_t)(
        (uint32_t)original-shifted_dx-carry
    );
    /* Arithmetic right shift by 2 in portable integer arithmetic. */
    const int32_t v=(result_after_sbb<0x8000u)
        ? (int32_t)result_after_sbb : ((int32_t)result_after_sbb-65536);
    const int32_t q=(v>=0)?v/4:-((-v+3)/4);
    return (uint16_t)(((uint32_t)(q-1)) & UINT32_C(0xFFFF));
}
int main(void)
{
    unsigned checked=0;
    for(uint32_t x=0;x<=0xFFFFu;x++){
        const uint16_t original=(uint16_t)x;
        uint16_t word=original;
        must(moo2_v131_derived_apply_special7_adjustment(
            &word,1u)==MOO2_V131_PLANET_SPECIAL_OK);
        if(word!=machine_reference(original)){
            fprintf(stderr,"mismatch %#x got %#x expected %#x\n",
                    (unsigned)original,(unsigned)word,
                    (unsigned)machine_reference(original));
            return 2;
        }
        for(uint16_t special=0;special<=2;special+=2) {
            word=original;
            must(moo2_v131_derived_apply_special7_adjustment(
                &word,special)==MOO2_V131_PLANET_SPECIAL_OK);
            must(word==original);
        }
        checked++;
    }
    uint16_t word=0;
    must(moo2_v131_derived_apply_special7_adjustment(NULL,1u)
         ==MOO2_V131_PLANET_SPECIAL_INVALID_POINTER);
    must(moo2_v131_derived_apply_special7_adjustment(&word,1u)
         ==MOO2_V131_PLANET_SPECIAL_OK);
    must(word==0xFFFFu);
    puts("PASS: all 65536 signed 16-bit inputs match independent x86 CWD/SHL/SBB/SAR/DEC emulation");
    return checked==65536u?0:3;
}
