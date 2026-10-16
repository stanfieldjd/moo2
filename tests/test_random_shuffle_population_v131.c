/* Original v1.31 Random_ 128-byte source and Shuffle_Int_ 70-byte
 * source tests with independent exact reproducible seed/permutation
 * vectors for population's original four-byte Shuffle_ dispatch.
 */
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../decompilation/reconstructed/random_shuffle_population_v131.c"
static void require(int yes) {
    if(!yes){fputs("FAIL original Random_/Shuffle_Int_ source\n",stderr);exit(1);}
}
static void w32(uint8_t *p,uint32_t v){
    for(unsigned i=0;i<4u;i++)p[i]=(uint8_t)(v>>(8u*i));
}
static uint32_t r32(const uint8_t *p){
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
int main(void){
    const uint32_t starts[]={0u,1u,UINT32_C(0x12345678),UINT32_MAX};
    const uint32_t vectors[][5]={
        {1u,4u,2u,2u,1u},{2u,3u,1u,2u,1u},
        {1u,2u,1u,2u,1u},{4u,1u,1u,2u,1u}
    };
    const uint32_t finalseeds[]={
        UINT32_C(0x0DAA96F5),UINT32_C(0xF94BDF32),
        UINT32_C(0xA5ECF18D),UINT32_C(0x22094EB8)
    };
    const uint32_t permutations[][5]={
        {0,4,3,1,2},{1,3,2,4,0},
        {0,2,1,4,3},{3,1,2,4,0}
    };
    for(unsigned v=0;v<4;v++){
        uint32_t seed=starts[v],draw=0;
        for(unsigned i=0;i<5;i++) {
            require(moo2_v131_derived_random(
                &seed,5u-i,&draw)==MOO2_V131_SHUFFLE_OK);
            require(draw==vectors[v][i]);
        }
        require(seed==finalseeds[v]);
        uint8_t arr[20]={0};
        for(unsigned i=0;i<5;i++)w32(arr+4u*i,i);
        seed=starts[v];
        require(moo2_v131_derived_shuffle_int(
            &seed,arr,5u,4u)==MOO2_V131_SHUFFLE_OK);
        for(unsigned i=0;i<5;i++)
            require(r32(arr+4u*i)==permutations[v][i]);
        require(seed==finalseeds[v]);
    }
    uint8_t records[42u*4u]={0};
    unsigned trials=0u;
    for(uint32_t n=0u;n<=42u;n++)
      for(uint32_t initial=0u;initial<100u;initial++) {
        uint32_t seed=(uint32_t)(initial*UINT32_C(0xA953FD4E)+5u);
        for(uint32_t i=0;i<n;i++)
            w32(records+4u*i,i);
        uint32_t original_seed=seed;
        require(moo2_v131_derived_shuffle_int(
            &seed,records,(size_t)n,4u)==MOO2_V131_SHUFFLE_OK);
        uint8_t seen[42u]={0};
        for(uint32_t i=0;i<n;i++) {
            uint32_t x=r32(records+4u*i);
            require(x<n && seen[x]==0u);
            seen[x]=1u;
        }
        if(n>0u)require(seed!=original_seed);
        trials++;
      }
    uint32_t seed=0u,result=99u;
    require(moo2_v131_derived_random(
        &seed,0u,&result)==MOO2_V131_SHUFFLE_INVALID);
    require(seed==0u && result==99u);
    require(moo2_v131_derived_shuffle_int(
        &seed,records,43u,3u)==MOO2_V131_SHUFFLE_INVALID);
    printf("PASS: four original Random_/Shuffle_Int_ vectors, %u permutations over source pop bounds\n",trials);
    return 0;
}
