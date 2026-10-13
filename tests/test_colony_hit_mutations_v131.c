/* Exhaustive 16-bit original-code-derived write tests.
 * Branch choices are supplied; no original DOS executable is run. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "../decompilation/reconstructed/colony_hit_mutations_v131.c"

static void must(int v){if(!v){fputs("FAIL v1.31 colony write\\n",stderr);exit(1);}}
static void put16(uint8_t *p,uint16_t x){p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8);}
static uint16_t get16(const uint8_t *p){return (uint16_t)(p[0]|((uint16_t)p[1]<<8));}

int main(void) {
    uint8_t colony[0x169]={0},event[0x49]={0};
    for(uint32_t n=0;n<=UINT16_MAX;n++) {
        const uint16_t x=(uint16_t)n;
        put16(colony+0x130,x);put16(event+0x08,x);event[0x41]=0;
        must(!moo2_v131_derived_bomb_hit_write(
            colony,sizeof(colony),event,sizeof(event),MOO2_V131_BOMB_WRITE_POP_130));
        must(get16(colony+0x130)==(uint16_t)(n-1u));
        must(get16(event+0x08)==(uint16_t)(n+1u) && event[0x41]==1);
        put16(colony+0x132,x);put16(event+0x0a,x);event[0x41]=0;
        must(!moo2_v131_derived_bomb_hit_write(
            colony,sizeof(colony),event,sizeof(event),MOO2_V131_BOMB_WRITE_POP_132));
        must(get16(colony+0x132)==(uint16_t)(n-1u));
        must(get16(event+0x0a)==(uint16_t)(n+1u) && event[0x41]==1);
        put16(colony+0x125,x);put16(event+0x43,0xa5a5u);
        must(!moo2_v131_derived_bomb_hit_write(
            colony,sizeof(colony),event,sizeof(event),MOO2_V131_BOMB_WRITE_STATUS_125));
        must(get16(colony+0x125)==0 && get16(event+0x43)==x);
        put16(colony+0x130,x);put16(event+0x08,x);event[0x41]=0;
        must(!moo2_v131_derived_bio_hit_write(
            colony,sizeof(colony),event,sizeof(event),
            MOO2_V131_BIO_WRITE_POP_130,0,0,1));
        must(get16(colony+0x130)==(uint16_t)(n-1u));
        must(get16(event+0x08)==(uint16_t)(n+1u) && event[0x41]==1);
        put16(colony+0x132,x);put16(event+0x0a,x);
        must(!moo2_v131_derived_bio_hit_write(
            colony,sizeof(colony),event,sizeof(event),
            MOO2_V131_BIO_WRITE_POP_132,0,0,0));
        must(get16(colony+0x132)==(uint16_t)(n-1u));
        must(get16(event+0x0a)==(uint16_t)(n+1u));
        if(n>100u && n<32768u) {
            const unsigned idx=(unsigned)(n%16u);
            put16(colony+0xb4+2u*idx,x);
            must(!moo2_v131_derived_bio_hit_write(
                colony,sizeof(colony),event,sizeof(event),
                MOO2_V131_BIO_WRITE_REDUCE_DEFENSE_100,0,idx,0));
            must(get16(colony+0xb4+2u*idx)==(uint16_t)(n-100u));
        }
    }
    /* Original removes a middle entry by moving the last DWORD into it,
       decrementing entry count and incrementing two result-event WORDs. */
    memset(colony,0,sizeof(colony));memset(event,0,sizeof(event));
    colony[0x0a]=3;
    for(unsigned i=0;i<3;i++)for(unsigned j=0;j<4;j++)
        colony[0x0c+4u*i+j]=(uint8_t)(10u*i+j);
    uint8_t original_last[4];memcpy(original_last,colony+0x14,4);
    put16(event+0x0c,UINT16_MAX);put16(event+0x3f,UINT16_MAX);
    must(!moo2_v131_derived_bio_hit_write(
        colony,sizeof(colony),event,sizeof(event),
        MOO2_V131_BIO_WRITE_REMOVE_ENTRY,1,0,1));
    must(colony[0x0a]==2 && !memcmp(colony+0x10,original_last,4));
    must(get16(event+0x0c)==0 && get16(event+0x3f)==0 && event[0x41]==1);
    colony[0x0a]=1;colony[0x0c]=77;
    must(!moo2_v131_derived_bio_hit_write(
        colony,sizeof(colony),event,sizeof(event),
        MOO2_V131_BIO_WRITE_REMOVE_ENTRY,0,0,1));
    must(colony[0x0a]==0 && colony[0x0c]==77);
    uint8_t saved_colony[sizeof(colony)],saved_event[sizeof(event)];
    memcpy(saved_colony,colony,sizeof(colony));
    memcpy(saved_event,event,sizeof(event));
    must(moo2_v131_derived_bio_hit_write(
        colony,sizeof(colony),event,sizeof(event),
        MOO2_V131_BIO_WRITE_REMOVE_ENTRY,1,0,1)==MOO2_V131_HIT_WRITE_INVALID);
    must(!memcmp(saved_colony,colony,sizeof(colony)) &&
         !memcmp(saved_event,event,sizeof(event)));
    must(moo2_v131_derived_bio_hit_write(
        colony,sizeof(colony),event,sizeof(event),
        MOO2_V131_BIO_WRITE_REDUCE_DEFENSE_100,0,16,1)==MOO2_V131_HIT_WRITE_INVALID);
    must(moo2_v131_derived_bomb_hit_write(
        colony,0x100,event,sizeof(event),
        MOO2_V131_BOMB_WRITE_POP_130)==MOO2_V131_HIT_WRITE_INVALID);
    must(moo2_v131_derived_bomb_hit_write(
        colony,sizeof(colony),event,0x44u,
        MOO2_V131_BOMB_WRITE_POP_130)==MOO2_V131_HIT_WRITE_INVALID);
    puts("PASS: 65536 branch-selected 16-bit patterns, packed population removal and host guards");
    return 0;
}
