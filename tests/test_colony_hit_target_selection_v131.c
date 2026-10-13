/*
 * Host-side tests for original v1.31 biological reservoir selector
 * and ordinary 49-slot bomb eligibility scan. Does not implement
 * the original player/colony hit side effects.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/random_v131.c"
#include "../decompilation/reconstructed/colony_hit_target_selection_v131.c"

static void require(int v){if(!v){fputs("FAIL source biological/bomb target selector\n",stderr);exit(1);}}
static int excluded(unsigned i){
    const unsigned stops[]={9,26,27,42,47,8,40,41};
    for(unsigned p=0;p<sizeof(stops)/sizeof(stops[0]);p++)
        if(stops[p]==i)return 1;
    return 0;
}
/* Independent numeric reference: original modulo-2^32 seed recurrence,
 * source rejection threshold, inclusive 1..N, backwards reservoir. */
static int32_t reference_select(const uint8_t *colony,unsigned count,
                                uint32_t *seed,uint32_t *eligible)
{
    int32_t selected=-1;
    *eligible=0u;
    for(unsigned p=count;p>0;p--){
        unsigned index=p-1u;
        if((colony[0x0cu+4u*index]&0x0fu)==8u)continue;
        uint32_t k=++*eligible;
        const uint32_t divisor=UINT32_MAX/k;
        const uint32_t acceptance_limit=divisor*k;
        do {
            *seed=(*seed)*UINT32_C(0x41c64e6d)+UINT32_C(0x3039);
        }while(*seed>=acceptance_limit);
        if(*seed/divisor+1u==1u)selected=(int32_t)index;
    }
    return selected;
}

int main(void)
{
    uint8_t colony[0x0cu+255u*4u]={0};
    unsigned matched=0;
    for(unsigned count=0;count<=255u;count++) {
        colony[0x0au]=(uint8_t)count;
        for(unsigned pattern=0;pattern<5u;pattern++) {
            for(unsigned i=0;i<count;i++){
                uint8_t nibble=(uint8_t)(
                    pattern==0u?8u:
                    pattern==1u?0u:
                    pattern==2u?(i%3u==0u?8u:7u):
                    pattern==3u?(i%2u==0u?8u:4u):
                    (i*17u+pattern)%16u);
                /* Other DWORD bytes should not change the low-nibble test. */
                colony[0x0cu+4u*i]=nibble;
                colony[0x0du+4u*i]=0xF3u;
                colony[0x0eu+4u*i]=0xA5u;
                colony[0x0fu+4u*i]=0x5Au;
            }
            uint32_t seed=(uint32_t)(count*1234567u+pattern*101u);
            uint32_t reference_seed=seed,eligible=999,ref_count=999;
            int32_t selected=777;
            int32_t wanted=reference_select(colony,count,
                                              &reference_seed,&ref_count);
            Moo2V131HitSelectStatus status=moo2_v131_derived_bio_target_select(
                colony,sizeof(colony),&seed,&selected,&eligible);
            require(status==(wanted<0?MOO2_V131_HIT_SELECT_NONE:MOO2_V131_HIT_SELECT_OK));
            require(selected==wanted && seed==reference_seed && eligible==ref_count);
            matched++;
        }
    }
    colony[0x0au]=2u;
    colony[0x0cu]=1u;
    colony[0x10u]=2u;
    uint32_t seed=0,eligible=0;
    int32_t index=-1;
    require(moo2_v131_derived_bio_target_select(
        colony,0x13u,&seed,&index,&eligible)==MOO2_V131_HIT_SELECT_INVALID);
    require(moo2_v131_derived_bio_target_select(
        colony,sizeof(colony),NULL,&index,&eligible)==MOO2_V131_HIT_SELECT_INVALID);

    /* The ordinary hit selector scans exactly 49 slots, 48 to 0.
       Eight source-defined indices are skipped even if nonzero. */
    uint8_t candidate[49]={0};
    size_t valid=0;
    memset(colony,0,sizeof(colony));
    memset(colony+0x136u,1u,49u);
    require(moo2_v131_derived_bomb_eligible_indices(
        colony,sizeof(colony),candidate,sizeof(candidate),&valid)==MOO2_V131_HIT_SELECT_OK);
    require(valid==41u);
    size_t j=0;
    for(int i=48;i>=0;i--) {
        if(excluded((unsigned)i))continue;
        require(j<valid && candidate[j++]==(uint8_t)i);
    }
    require(j==41u);
    for(unsigned i=0;i<49u;i++){
        memset(colony+0x136u,0,49u);
        colony[0x136u+i]=0xFFu;
        valid=123u;
        Moo2V131HitSelectStatus status=moo2_v131_derived_bomb_eligible_indices(
            colony,sizeof(colony),candidate,sizeof(candidate),&valid);
        if(excluded(i)){
            require(status==MOO2_V131_HIT_SELECT_NONE && valid==0u);
        }else{
            require(status==MOO2_V131_HIT_SELECT_OK && valid==1u);
            require(candidate[0]==i);
        }
    }
    memset(colony+0x136u,1u,49u);
    require(moo2_v131_derived_bomb_eligible_indices(
        colony,sizeof(colony),candidate,40u,&valid)==MOO2_V131_HIT_SELECT_INVALID);
    require(moo2_v131_derived_bomb_eligible_indices(
        colony,0x166u,candidate,sizeof(candidate),&valid)==MOO2_V131_HIT_SELECT_INVALID);
    printf("PASS: %u seeded reverse biological reservoir fixtures and 49-slot bomb eligibility scan\n",matched);
    return 0;
}
