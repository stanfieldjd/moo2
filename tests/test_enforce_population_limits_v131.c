/*
 * Original v1.31 Enforce_Population_Limits_At_Colony_ regression.
 * Dependency callbacks are explicit: race limit, Shuffle_, Food2.
 * Assesses source-defined priority, repeated last-record
 * replacement, threshold-0 behavior, and exact zero-food bitmask.
 * Not a DOS-executable behavioral differential test.
 */
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../decompilation/reconstructed/enforce_population_limits_v131.c"
static void need(int condition) {
    if(!condition) {fputs("FAIL original population limit branch\n",stderr);exit(1);}
}
typedef struct {
    int16_t limits[10];
    int16_t food;
    size_t cap_calls[10];
    unsigned shuffle_calls;
    unsigned food_calls;
    unsigned fail_cap,fail_shuffle,fail_food;
    uint8_t expected_owner;
} Fixture;
static int cap(void *opaque,const uint8_t *colony,
               uint8_t type,int16_t *out) {
    Fixture *f=(Fixture*)opaque;
    need(colony[0]==f->expected_owner && type<10u);
    f->cap_calls[type]++;
    if(f->fail_cap)return 0;
    *out=f->limits[type];
    return 1;
}
static int shuffle(void *opaque,uint8_t *records,
                   size_t count,size_t stride) {
    Fixture *f=(Fixture*)opaque;
    need(records && stride==4u && count<=42u);
    f->shuffle_calls++;
    return f->fail_shuffle==0;
}
static int food(void *opaque,uint8_t *colony,
                int8_t owner,int16_t *result) {
    Fixture *f=(Fixture*)opaque;
    need(colony[0]==f->expected_owner);
    need(owner==(int8_t)f->expected_owner);
    f->food_calls++;
    if(f->fail_food)return 0;
    *result=f->food;
    return 1;
}
static void put32(uint8_t *p,uint32_t word) {
    for(unsigned i=0;i<4u;i++)p[i]=(uint8_t)(word>>(8u*i));
}
static void reset(Fixture *f,uint8_t colony[0x169u],unsigned owner) {
    memset(colony,0,0x169u);
    memset(f,0,sizeof(*f));
    f->expected_owner=(uint8_t)owner;
    for(unsigned i=0;i<10;i++)f->limits[i]=2;
    colony[0]=(uint8_t)owner;
}
static void set(uint8_t *colony,size_t index,uint32_t value) {
    put32(colony+0x0Cu+4u*index,value);
}
static uint32_t entry(const uint8_t *colony,size_t index) {
    return moo2_v131_pop_load(colony+0x0Cu+4u*index);
}
int main(void) {
    uint8_t colony[0x169u];
    Fixture fixture;
    Moo2V131PopLimitContext ctx={cap,shuffle,food,&fixture};

    /* Five categories have original victim preference:
       type9 > other-owner > owner-in-high-flags > type8 > owner-type.
       All cap2, so 3 removed; first two must remain. */
    reset(&fixture,colony,1u);
    colony[0x0au]=5u;
    set(colony,0,UINT32_C(0x10001)); /* type1 == owner */
    set(colony,1,UINT32_C(0x20008)); /* type8 */
    set(colony,2,UINT32_C(0x3012));  /* type2, 3bit owner==1 */
    set(colony,3,UINT32_C(0x403));   /* type3, race bits not owner */
    set(colony,4,UINT32_C(0x50009)); /* type9 */
    fixture.food=1;
    need(moo2_v131_derived_enforce_population_limits(
        &ctx,colony,sizeof(colony))==MOO2_V131_POPLIMIT_OK);
    need(colony[0x0au]==2u && entry(colony,0)==UINT32_C(0x10001)
         && entry(colony,1)==UINT32_C(0x20008));
    need(fixture.shuffle_calls==1u && fixture.food_calls==1u);
    for(unsigned i=0;i<10u;i++)
        need(fixture.cap_calls[i]==(unsigned)(i==1u||i==2u||i==3u||i==8u||i==9u));

    /* All 42 original marks/slots and cumulative cap thresholds:
       type2 cap3, type3 cap5 -> combined count<=5, type2 <=3. */
    reset(&fixture,colony,1u);
    colony[0x0au]=7u;
    fixture.limits[2]=3;
    fixture.limits[3]=5;
    for(unsigned i=0;i<7u;i++)set(colony,i,
        UINT32_C(0x10000)|(i<4u?2u:3u));
    fixture.food=1;
    need(moo2_v131_derived_enforce_population_limits(
        &ctx,colony,sizeof(colony))==MOO2_V131_POPLIMIT_OK);
    need(colony[0x0au]==5u); /* total cap5, type2 cap3 */
    unsigned count2=0,count3=0;
    for(unsigned i=0;i<colony[0x0au];i++) {
        if((entry(colony,i)&15u)==2u)count2++;
        if((entry(colony,i)&15u)==3u)count3++;
    }
    need(count2<=3u && count2+count3==5u);

    /* Original mark zero has no effect: source t loop begins at 1. */
    reset(&fixture,colony,1u);
    colony[0x0au]=4u;
    fixture.limits[2]=0;
    for(unsigned i=0;i<4u;i++)set(colony,i,2u);
    fixture.food=1;
    need(moo2_v131_derived_enforce_population_limits(
        &ctx,colony,sizeof(colony))==MOO2_V131_POPLIMIT_OK);
    need(colony[0x0au]==4u);

    /* Real source no-food sweep exact low word rewriting.
       BYTE flag7 is set, flag8 cleared, except type8 or any
       original population status in mask 0x180. */
    reset(&fixture,colony,1u);
    colony[0x0au]=5u;
    for(unsigned i=0;i<10u;i++)fixture.limits[i]=41;
    set(colony,0,UINT32_C(0xCAFE0001));
    set(colony,1,UINT32_C(0xBAAD0008));
    set(colony,2,UINT32_C(0xDEAD0102));
    set(colony,3,UINT32_C(0xC0DE0083));
    set(colony,4,UINT32_C(0xBEEF0203));
    fixture.food=0;
    need(moo2_v131_derived_enforce_population_limits(
        &ctx,colony,sizeof(colony))==MOO2_V131_POPLIMIT_OK);
    need(entry(colony,0)==UINT32_C(0xCAFE0081));
    need(entry(colony,1)==UINT32_C(0xBAAD0008));
    need(entry(colony,2)==UINT32_C(0xDEAD0102));
    need(entry(colony,3)==UINT32_C(0xC0DE0083));
    need(entry(colony,4)==UINT32_C(0xBEEF0283));

    /* Source no-op food path when all original flags already set. */
    fixture.food=2;
    uint8_t previous[sizeof(colony)];
    memcpy(previous,colony,sizeof(colony));
    need(moo2_v131_derived_enforce_population_limits(
        &ctx,colony,sizeof(colony))==MOO2_V131_POPLIMIT_OK);
    need(!memcmp(previous,colony,sizeof(colony)));

    /* Invalid type nibble is not safe for source 10-slot capacity
       table; C must reject, without population compaction. */
    reset(&fixture,colony,1u);
    colony[0x0au]=1u;
    set(colony,0,UINT32_C(0xABCDEF1F));
    memcpy(previous,colony,sizeof(colony));
    need(moo2_v131_derived_enforce_population_limits(
        &ctx,colony,sizeof(colony))==MOO2_V131_POPLIMIT_INVALID);
    need(!memcmp(previous,colony,sizeof(colony)));

    /* Callback errors are visible rather than silently claiming
       calculations happened. */
    reset(&fixture,colony,1u);
    colony[0x0au]=1u;set(colony,0,2u);fixture.fail_cap=1;
    need(moo2_v131_derived_enforce_population_limits(
        &ctx,colony,sizeof(colony))==MOO2_V131_POPLIMIT_CALLBACK_FAILED);
    fixture.fail_cap=0;fixture.fail_shuffle=1;
    need(moo2_v131_derived_enforce_population_limits(
        &ctx,colony,sizeof(colony))==MOO2_V131_POPLIMIT_CALLBACK_FAILED);
    fixture.fail_shuffle=0;fixture.fail_food=1;
    need(moo2_v131_derived_enforce_population_limits(
        &ctx,colony,sizeof(colony))==MOO2_V131_POPLIMIT_CALLBACK_FAILED);
    /* Loop over all population counts up to original 42-space
       marker capacity, every class 0..9, capacity range 1..41.
       Exactly one class per run, expected final <=cap. */
    unsigned scenarios=0u;
    for(unsigned n=0;n<=42u;n++)
      for(unsigned type=0;type<10u;type++)
      for(unsigned limit=1;limit<42u;limit++) {
        reset(&fixture,colony,1u);
        colony[0x0au]=(uint8_t)n;
        fixture.limits[type]=(int16_t)limit;
        fixture.food=1;
        for(unsigned i=0;i<n;i++)set(colony,i,(UINT32_C(0x10000)*i)|type);
        need(moo2_v131_derived_enforce_population_limits(
            &ctx,colony,sizeof(colony))==MOO2_V131_POPLIMIT_OK);
        need(colony[0x0au]==(uint8_t)(n<limit?n:limit));
        scenarios++;
      }
    printf("PASS: %u original class/capacity/count cases, 5-priority removals, zero-food status word and callback bounds\n",scenarios);
    return 0;
}
