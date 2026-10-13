/* Original-source-derived Random_ C regression, not DOS differential test. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "../decompilation/reconstructed/random_v131.c"

static void check(int ok) {
    if(!ok){fputs("FAIL original v1.31 RNG state and return\n",stderr);exit(1);}
}

int main(void) {
    uint32_t seed=0,out=0;
    const uint32_t outputs[5]={1u,83u,66u,84u,6u};
    const uint32_t states[5]={12345u,3554416254u,2802067423u,3596950572u,229283573u};
    for(int i=0;i<5;i++) {
        check(moo2_v131_derived_random(&seed,100u,&out)==MOO2_V131_RANDOM_OK);
        check(out==outputs[i] && seed==states[i]);
    }
    seed=0x0DBDBB1Eu;
    out=0;
    check(moo2_v131_derived_random(&seed,100u,&out)==MOO2_V131_RANDOM_OK);
    /* First advance produces 0xffffffff, rejected because >=0xffffffa0.
       Second produces 0xbe39e1cc, accepted with result 75. */
    check(seed==UINT32_C(0xBE39E1CC) && out==75u);

    seed=0; out=0;
    check(moo2_v131_derived_random(&seed,1u,&out)==MOO2_V131_RANDOM_OK);
    check(seed==12345u && out==1u);
    seed=0; out=0;
    check(moo2_v131_derived_random(&seed,UINT32_MAX,&out)==MOO2_V131_RANDOM_OK);
    check(seed==12345u && out==12346u);

    seed=0xABCDEF01u;
    out=19;
    check(moo2_v131_derived_random(&seed,0u,&out)==MOO2_V131_RANDOM_ZERO_MAXIMUM);
    check(seed==0xABCDEF01u && out==19u);
    check(moo2_v131_derived_random(NULL,100,&out)==MOO2_V131_RANDOM_INVALID_POINTER);
    check(moo2_v131_derived_random(&seed,100,NULL)==MOO2_V131_RANDOM_INVALID_POINTER);

    /* Determinism for independent state objects and valid return range
       across a broader set of bounds. */
    const uint32_t bounds[]={
        1u,2u,3u,5u,7u,10u,13u,19u,100u,101u,1000u,
        32768u,65535u,65536u,100000u,UINT32_MAX
    };
    for(size_t k=0;k<sizeof(bounds)/sizeof(bounds[0]);k++) {
        uint32_t a=0xDEADBEEFu,b=0xDEADBEEFu;
        for(int i=0;i<128;i++) {
            uint32_t x=0,y=0;
            check(moo2_v131_derived_random(&a,bounds[k],&x)==MOO2_V131_RANDOM_OK);
            check(moo2_v131_derived_random(&b,bounds[k],&y)==MOO2_V131_RANDOM_OK);
            check(a==b && x==y && x>=1u && x<=bounds[k]);
        }
    }
    puts("PASS: original v1.31 Random_ seed fixtures, rejection retry, range, zero-divisor guard");
    return 0;
}
