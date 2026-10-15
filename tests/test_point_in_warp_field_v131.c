/*
 * Source-defined warp-interdictor 73-byte function: original status
 * bitmap at star+0x39, signed WORD target coords and radius squared 8100.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/point_in_warp_field_v131.c"
static void check(int ok){if(!ok){fputs("FAIL original warp radius / owner mask\n",stderr);exit(1);}}
static void w16(uint8_t *p,int32_t n){uint16_t x=(uint16_t)n;p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8);}
int main(void) {
    uint8_t star[0x71u]={0},inside=99;
    for(unsigned owner=0;owner<8u;owner++)
      for(unsigned mask=0;mask<256u;mask++)
        for(unsigned case_id=0;case_id<9u;case_id++) {
            memset(star,0,sizeof(star));
            star[0x39u]=(uint8_t)mask;
            w16(star+0x0fu,-100);
            w16(star+0x11u,200);
            const int xy[9][2]={
               {-100,200},{-10,200},{-190,200},{-9,200},
               {-191,200},{-100,290},{-100,291},{-28,254},{-28,255}
            };
            int32_t x=xy[case_id][0],y=xy[case_id][1];
            unsigned eligible=(mask & (unsigned)~(1u<<owner))!=0u;
            int64_t dx=(int64_t)x+100,dy=(int64_t)y-200;
            unsigned expected=eligible && dx*dx+dy*dy<=8100;
            inside=99;
            check(moo2_v131_derived_is_in_warp_field(
               star,sizeof(star),x,y,(uint8_t)owner,&inside)==MOO2_V131_WARP_OK);
            check(inside==(uint8_t)expected);
        }
    star[0x39u]=0xffu;
    w16(star+0x0fu,32767);
    w16(star+0x11u,-32768);
    check(moo2_v131_derived_is_in_warp_field(
        star,sizeof(star),32767,-32768,0,&inside)==MOO2_V131_WARP_OK);
    check(inside==1u);
    uint8_t copy[sizeof(star)];memcpy(copy,star,sizeof(star));
    check(moo2_v131_derived_is_in_warp_field(
        star,sizeof(star),0,0,8,&inside)==MOO2_V131_WARP_INVALID);
    check(moo2_v131_derived_is_in_warp_field(
        star,0,0,0,1,&inside)==MOO2_V131_WARP_INVALID);
    check(!memcmp(star,copy,sizeof(star)));
    puts("PASS original warp: 8 owners x 256 bitmasks x 9 coordinate cases, exact <=90 radius boundary");
}
