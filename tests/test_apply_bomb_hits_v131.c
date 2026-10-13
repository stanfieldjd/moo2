/* Regression of original Apply_Bomb_Hits_ shared-epilogue loop.
 * Resolver callbacks are test stubs, not actual original combat effects.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/apply_bomb_hits_v131.c"

typedef struct {
    unsigned bio_calls,bomb_calls;
    int32_t bomb_returns[8];
    unsigned return_position;
    uint8_t *expected_colony;
    uint8_t *expected_event;
} Harness;
static void require(int x){if(!x){fputs("FAIL Apply_Bomb_Hits original loop semantics\n",stderr);exit(1);}}
static void write16(uint8_t *p,int32_t x){
    uint16_t v=(uint16_t)x;p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
static void write32(uint8_t *p,uint32_t v){
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
    p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);
}
static int32_t on_bomb(void *opaque,uint8_t *colony,int32_t remaining,uint8_t *event){
    Harness *h=(Harness *)opaque;
    require(colony==h->expected_colony && event==h->expected_event);
    require(remaining>0);
    h->bomb_calls++;
    require(h->return_position<8);
    return h->bomb_returns[h->return_position++];
}
static void on_bio(void *opaque,uint8_t *colony,uint8_t *event){
    Harness *h=(Harness *)opaque;
    require(colony==h->expected_colony && event==h->expected_event);
    h->bio_calls++;
}
int main(void) {
    uint8_t colonies[4*0x169]={0};
    uint8_t event[0x49]={0};
    event[1]=3;
    Harness h={0};
    h.expected_colony=colonies+3u*0x169u;
    h.expected_event=event;
    Moo2V131ApplyBombHitsContext ctx={
        colonies,4,on_bomb,on_bio,&h
    };
    int32_t final_eax=777;

    write16(event+3,3);write16(event+6,2);
    write32(event+0x45,0u);
    h.bomb_returns[0]=1;h.bomb_returns[1]=2;
    require(moo2_v131_derived_apply_bomb_hits(
        &ctx,event,sizeof(event),16,&final_eax)==MOO2_V131_APPLY_BOMB_HITS_OK);
    require(final_eax==0 && h.bio_calls==2 && h.bomb_calls==2);
    require(moo2_v131_bomb_hits_u32(event+0x45)==3u);
    require(moo2_v131_bomb_hits_u16(event+3)==3u);
    require(moo2_v131_bomb_hits_u16(event+6)==2u);

    /* A zero ordinary hit resolver result resets local count to zero. */
    h.bio_calls=h.bomb_calls=h.return_position=0;
    h.bomb_returns[0]=0;
    write16(event+3,99);write16(event+6,0);
    write32(event+0x45,43);
    require(moo2_v131_derived_apply_bomb_hits(
        &ctx,event,sizeof(event),3,&final_eax)==MOO2_V131_APPLY_BOMB_HITS_OK);
    require(h.bomb_calls==1 && final_eax==0);
    require(moo2_v131_bomb_hits_u32(event+0x45)==43);

    /* Ordinary hit accumulator is a 32-bit modulo addition. */
    h.bio_calls=h.bomb_calls=h.return_position=0;
    h.bomb_returns[0]=3;
    write16(event+3,3);write16(event+6,0);
    write32(event+0x45,UINT32_MAX-1u);
    require(moo2_v131_derived_apply_bomb_hits(
        &ctx,event,sizeof(event),3,&final_eax)==MOO2_V131_APPLY_BOMB_HITS_OK);
    require(h.bomb_calls==1 && final_eax==0);
    require(moo2_v131_bomb_hits_u32(event+0x45)==1u);

    /* No hits -> immediate source LEA/test and shared epilogue. */
    h.bio_calls=h.bomb_calls=0;
    write16(event+3,0);write16(event+6,0);
    require(moo2_v131_derived_apply_bomb_hits(
        &ctx,event,sizeof(event),1,&final_eax)==MOO2_V131_APPLY_BOMB_HITS_OK);
    require(!h.bio_calls && !h.bomb_calls && final_eax==0);

    write16(event+3,-2);write16(event+6,1);
    require(moo2_v131_derived_apply_bomb_hits(
        &ctx,event,sizeof(event),1,&final_eax)==MOO2_V131_APPLY_BOMB_HITS_OK);
    require(final_eax==-1 && !h.bio_calls && !h.bomb_calls);

    /* Host-only guard handles unbounded pathological resolver progress. */
    write16(event+3,2);write16(event+6,0);
    h.bio_calls=h.bomb_calls=h.return_position=0;
    for(unsigned i=0;i<8;i++)h.bomb_returns[i]=-1;
    require(moo2_v131_derived_apply_bomb_hits(
        &ctx,event,sizeof(event),3,&final_eax)
        ==MOO2_V131_APPLY_BOMB_HITS_ITERATION_LIMIT);
    require(h.bomb_calls==3);

    require(moo2_v131_derived_apply_bomb_hits(
        &ctx,event,0x48u,3,&final_eax)
        ==MOO2_V131_APPLY_BOMB_HITS_INVALID);
    require(moo2_v131_derived_apply_bomb_hits(
        &ctx,NULL,sizeof(event),3,&final_eax)
        ==MOO2_V131_APPLY_BOMB_HITS_INVALID);
    require(moo2_v131_derived_apply_bomb_hits(
        &ctx,event,sizeof(event),0,&final_eax)
        ==MOO2_V131_APPLY_BOMB_HITS_INVALID);
    event[1]=4;
    require(moo2_v131_derived_apply_bomb_hits(
        &ctx,event,sizeof(event),3,&final_eax)
        ==MOO2_V131_APPLY_BOMB_HITS_INVALID);
    puts("PASS original bomb/bio resolver loop, 32-bit accumulation, shared return and safe host guards");
    return 0;
}
