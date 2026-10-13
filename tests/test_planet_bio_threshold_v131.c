/* Exhaustive derived original bio damage threshold tests.
 * Reference independently models the source CWD/SUB/SAR and CWD/SHL/
 * SBB/SAR arithmetic, including x86 signed-16-bit and borrow semantics.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "../decompilation/reconstructed/planet_bio_threshold_v131.c"

static void require(int ok) {
  if(!ok){fputs("FAIL original biological threshold arithmetic\n",stderr);exit(1);}
}
static int32_t signed16(uint16_t bits) {
  return bits<32768u?(int32_t)bits:(int32_t)bits-65536;
}
static uint16_t reference(uint16_t bits,int mode) {
    if(mode==0)return bits;
    const int negative=(bits&0x8000u)!=0;
    const int divisor=mode==1?2:4;
    const uint32_t dx=negative?(mode==1?0xFFFFu:0xFFFCu):0u;
    const uint32_t cf=negative && mode==2?1u:0u;
    uint16_t biased=(uint16_t)((uint32_t)bits-dx-cf);
    const int32_t y=signed16(biased);
    const int32_t q=y>=0 ? y/divisor : -((-y+divisor-1)/divisor);
    return (uint16_t)((uint32_t)q&0xFFFFu);
}
int main(void) {
    unsigned matched=0;
    for(uint32_t n=0;n<65536u;n++){
        const uint16_t orig=(uint16_t)n;
        for(int x=0;x<4;x++){
            const uint8_t p182=(uint8_t)((x==1||x==3)?3:0);
            const uint8_t p1d8=(uint8_t)((x==2||x==3)?3:0);
            const int mode=(x==0)?0:(x==2)?2:1;
            uint16_t candidate=orig;
            require(moo2_v131_derived_bio_threshold_adjust(
                &candidate,p182,p1d8)==MOO2_V131_BIO_THRESHOLD_OK);
            uint16_t expected=reference(orig,mode);
            if(candidate!=expected) {
                fprintf(stderr,"at %#x path %d got %#x expected %#x\n",
                    (unsigned)orig,x,candidate,expected);
                return 2;
            }
            matched++;
        }
    }
    uint16_t value=75;
    require(moo2_v131_derived_bio_threshold_adjust(NULL,3,0)
           ==MOO2_V131_BIO_THRESHOLD_INVALID_POINTER);
    require(moo2_v131_derived_bio_threshold_adjust(&value,3,3)
           ==MOO2_V131_BIO_THRESHOLD_OK);
    require(value==37u);
    for(uint32_t r=1;r<=100;r++){
        for(uint16_t chance=0;chance<=150;chance++) {
            require(moo2_v131_derived_bio_roll_passes(chance,r)==(r<=chance));
        }
    }
    require(!moo2_v131_derived_bio_roll_passes((uint16_t)-1,1u));
    printf("PASS: %u exhaustive original bio threshold branches and 15100 source Random_(100) comparisons\n",matched);
    return 0;
}
