/*
 * Complete source-derived v1.31 Watcom Random_ and Shuffle_Int_
 * for original 4-byte population entries, used by Shuffle_ when
 * record stride EDX=4.
 * Original ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Random_ CODE 0x1147A0,128B SHA256
 * fed72b3293ed869db1e3ff6c93477767f0322794a2185d18c95798a49c92ff56
 * Shuffle_Int_ CODE 0xEEA3C,70B SHA256
 * 89379ad9f18797040d7bf7d33ef316c72c77d746f75c9ba95e5e47a3147e2315
 * Generic Shuffle_ wrapper CODE 0xEEA82,190B SHA256
 * d5dc211bc4f2300aa5c591335beac6e905aac5d6134309eb71e0a1a26e28a604
 *
 * Random_(EAX=unsigned n) with _random_seed DATA 0x41E34:
 *   q=UINT32_MAX/n; cutoff=q*n;
 *   repeat seed=seed*0x41C64E6D+0x3039 (wrap mod 2^32)
 *   until seed<cutoff (signedness: original comparison JBE skips
 *   when cutoff<=seed). Return seed/q +1, range [1,n].
 * Random_ has a source division before checking input n==0, which
 * would trap on DOS; derived C rejects zero rather than divide by0.
 *
 * Shuffle_Int_(EAX=DWORD-array, CX=count) loops i=0..count-1:
 *   j=(Random_(count-i)+i-1); swap DWORD[i] and DWORD[j].
 * Original Shuffle_ dispatches to Shuffle_Int_ for EDX stride4.
 * The per-call host draw cap is a safety guard absent from DOS.
 */
#include <stdint.h>
#include <stddef.h>
#include "random_shuffle_population_v131.h"

static uint32_t moo2_v131_shuffle_dword(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void moo2_v131_shuffle_write(uint8_t *p,uint32_t value) {
    for(unsigned i=0;i<4u;i++)p[i]=(uint8_t)(value>>(8u*i));
}
Moo2V131ShuffleResult moo2_v131_derived_random(
    uint32_t *seed,uint32_t n,uint32_t *result)
{
    if(!seed || !result || n==0u)
        return MOO2_V131_SHUFFLE_INVALID;
    uint32_t div=UINT32_MAX/n;
    uint32_t cutoff=(uint32_t)(div*n);
    /* Normally only one RNG update is required. Host guard avoids
       potentially unbounded looping on malformed/adversarial state. */
    for(unsigned attempt=0u;attempt<100000u;attempt++) {
        *seed=(*seed)*UINT32_C(0x41C64E6D)+UINT32_C(0x3039);
        if(*seed<cutoff) {
            *result=(*seed)/div+1u;
            return MOO2_V131_SHUFFLE_OK;
        }
    }
    return MOO2_V131_SHUFFLE_RNG_FAILED;
}
Moo2V131ShuffleResult moo2_v131_derived_shuffle_int(
    uint32_t *seed,uint8_t *records,size_t count,size_t stride)
{
    if(!seed || !records || stride!=4u || count>32767u)
        return MOO2_V131_SHUFFLE_INVALID;
    for(size_t i=0u;i<count;i++) {
        uint32_t draw=0u;
        Moo2V131ShuffleResult rc=moo2_v131_derived_random(
            seed,(uint32_t)(count-i),&draw);
        if(rc!=MOO2_V131_SHUFFLE_OK)return rc;
        size_t j=i+(size_t)draw-1u;
        uint8_t *a=records+4u*i;
        uint8_t *b=records+4u*j;
        uint32_t word=moo2_v131_shuffle_dword(a);
        moo2_v131_shuffle_write(a,moo2_v131_shuffle_dword(b));
        moo2_v131_shuffle_write(b,word);
    }
    return MOO2_V131_SHUFFLE_OK;
}
