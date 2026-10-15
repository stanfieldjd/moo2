/* Independent bitwise-reference integer sqrt regression for Watcom isqrt_. */
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include "../decompilation/reconstructed/isqrt_v131.c"

static uint32_t sqrt_reference(uint32_t n) {
    /* Digit-by-digit base-4 restoring square root, structurally
       independent of original Watcom binary search. */
    uint32_t root=0,bit=UINT32_C(1)<<30;
    while(bit>n)bit>>=2;
    while(bit) {
        if(n>=root+bit) {
            n-=root+bit;
            root=(root>>1)+bit;
        } else {
            root>>=1;
        }
        bit>>=2;
    }
    return root;
}
static void test(uint32_t n) {
    uint32_t result=moo2_v131_derived_isqrt(n);
    uint32_t expected=sqrt_reference(n);
    if(result!=expected) {
        fprintf(stderr,"FAIL original isqrt input %u result %u reference %u\n",
                n,result,expected);
        exit(1);
    }
    uint64_t square=(uint64_t)result*result;
    if(square>n || ((uint64_t)result+1u)*((uint64_t)result+1u)<=n) {
        fputs("FAIL original sqrt mathematical bounds\n",stderr);
        exit(1);
    }
}
int main(void) {
    for(uint32_t n=0;n<=UINT16_MAX;n++)test(n);
    /* Exact boundary cases around squares k^2 for every unsigned
       16-bit possible resulting root. Covers the full output range. */
    for(uint32_t k=0;k<=UINT16_MAX;k++) {
        uint64_t sq=(uint64_t)k*k;
        if(sq>0) test((uint32_t)(sq-1u));
        test((uint32_t)sq);
        if(sq<UINT32_MAX)test((uint32_t)(sq+1u));
    }
    uint32_t seed=UINT32_C(0x89ABCDEF);
    for(uint32_t i=0;i<200000u;i++) {
        seed=seed*UINT32_C(1664525)+UINT32_C(1013904223);
        test(seed);
    }
    test(UINT32_MAX);
    test(UINT32_C(0xFFFE0000));
    test(UINT32_C(0xFFFE0001));
    printf("PASS: exhaustive 16-bit inputs, all 65536 root square boundaries and 200000 independent random 32-bit integers\n");
    return 0;
}
