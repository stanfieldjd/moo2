/*
 * ISOLATED DERIVED Master of Orion II v1.31 original Watcom Random_.
 * Not the original MicroProse source. No game source assets included.
 *
 * Authenticated ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Original CODE Random_ 0x1147A0, 128 bytes, Watcom support module 143.
 * Original state is DWORD _random_seed at LE DATA object 2 offset 0x41E34
 * (relocated virtual address 0x1B1E34).
 *
 * Original input EAX is UINT32 max; original result EAX 1..max inclusive.
 * Source DIV at 0x1147C2 happens BEFORE the apparent zero-max branch,
 * so original max==0 raises x86 DIV error, not normal result=1.
 *
 * First compute limit=(0xFFFFFFFF / max) * max, then advance the LCG
 * using newseed = 0x41C64E6D * oldseed + 0x3039 (modulo 2^32)
 * until newseed < limit (original JBE retries when limit <= seed).
 * Return 1+(newseed / (0xFFFFFFFF / max)).
 *
 * Original CODE does unsigned DIV; this uses unsigned arithmetic for
 * exact modulo behavior. Host API reports zero bound as status rather
 * than attempting the original divide error: intentional safety change.
 */
#include "random_v131.h"

Moo2V131RandomStatus moo2_v131_derived_random(
    uint32_t *random_seed,uint32_t maximum,uint32_t *result)
{
    if(!random_seed || !result)return MOO2_V131_RANDOM_INVALID_POINTER;
    if(maximum==0u)return MOO2_V131_RANDOM_ZERO_MAXIMUM;

    const uint32_t divisor=UINT32_MAX/maximum;
    const uint32_t acceptance_limit=divisor*maximum;
    uint32_t seed;
    do {
        seed=(*random_seed)*UINT32_C(0x41C64E6D)+UINT32_C(0x3039);
        *random_seed=seed;
    } while(seed>=acceptance_limit);
    *result=seed/divisor+UINT32_C(1);
    return MOO2_V131_RANDOM_OK;
}
