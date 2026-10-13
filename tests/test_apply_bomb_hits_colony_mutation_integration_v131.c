/* Derived original Apply_Bomb_Hits_ loop + branch-selected population writes.
 * NO claim of complete original resolver branch selection or DOS behavior. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "../decompilation/reconstructed/apply_bomb_hits_v131.c"
#include "../decompilation/reconstructed/colony_hit_mutations_v131.c"
static void demand(int ok){if(!ok){fputs("FAIL bomb-hit colony mutation integration\n",stderr);exit(1);}}
static void wr16(uint8_t *p,uint16_t n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static uint16_t rd16(const uint8_t *p){return (uint16_t)(p[0]|((uint16_t)p[1]<<8));}
typedef struct {
    uint8_t *colony;
    unsigned biological_calls;
    unsigned ordinary_calls;
    int observed_normal_after_bio;
} IntegrationState;
static void biological(void *opaque,uint8_t *colony,uint8_t *event){
    IntegrationState *s=(IntegrationState*)opaque;
    demand(colony==s->colony && s->ordinary_calls==0u);
    s->biological_calls++;
    demand(!moo2_v131_derived_bio_hit_write(colony,0x169,event,0x49,
           MOO2_V131_BIO_WRITE_POP_132,0,0,1));
}
static int32_t ordinary(void *opaque,uint8_t *colony,int32_t count,uint8_t *event){
    IntegrationState *s=(IntegrationState*)opaque;
    demand(colony==s->colony && count>0);
    if(s->biological_calls==2u)s->observed_normal_after_bio=1;
    s->ordinary_calls++;
    demand(!moo2_v131_derived_bomb_hit_write(colony,0x169,event,0x49,
           MOO2_V131_BOMB_WRITE_POP_130));
    return 1;
}
int main(void){
    uint8_t colonies[2*0x169]={0},event[0x49]={0};
    uint8_t *colony=colonies+0x169;
    event[1]=1; /* original byte-sized colony index */
    wr16(colony+0x130,5);wr16(colony+0x132,4);
    wr16(event+3,3);wr16(event+6,2);
    IntegrationState s={colony,0,0,0};
    Moo2V131ApplyBombHitsContext ctx={colonies,2,ordinary,biological,&s};
    int32_t result=777;
    demand(!moo2_v131_derived_apply_bomb_hits(&ctx,event,sizeof(event),16,&result));
    demand(result==0 && s.biological_calls==2 && s.ordinary_calls==3);
    demand(s.observed_normal_after_bio);
    demand(rd16(colony+0x130)==2 && rd16(colony+0x132)==2);
    demand(rd16(event+0x08)==3 && rd16(event+0x0a)==2);
    demand(event[0x41]==1 && moo2_v131_bomb_hits_u32(event+0x45)==3);
    /* Original outer loop decrements local pending hit counts, not
       underlying event count WORDs at +3/+6. */
    demand(rd16(event+3)==3 && rd16(event+6)==2);
    puts("PASS source-derived bomb/bio loop integrated with original selected population mutations");
    return 0;
}
