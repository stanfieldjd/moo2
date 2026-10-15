/* Regression of original v1.31 per-nebula 3-coordinate grid and
 * named any-nebula wrapper. Synthetic in-memory nebula bitmap fixtures;
 * no original copyrighted graphics are included.
 */
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../decompilation/reconstructed/point_in_nebula_v131.c"
static void must(int ok){if(!ok){fputs("FAIL v1.31 nebula grid\n",stderr);exit(1);}}
static void word(uint8_t *p,int32_t n){uint16_t b=(uint16_t)n;p[0]=(uint8_t)b;p[1]=(uint8_t)(b>>8);}
int main(void) {
    uint8_t nebula[2u*5u]={0},image0[16u+9u]={0},image1[16u+4u]={0};
    Moo2V131NebulaBitmap bm[]={{image0,sizeof(image0)},{image1,sizeof(image1)}};
    Moo2V131NebulaContext ctx={nebula,2u,bm};
    word(nebula+0u,-100);word(nebula+2u,200);
    word(nebula+5u,400);word(nebula+7u,-300);
    word(image0,3);word(image0+2,3);
    word(image1,2);word(image1+2,2);
    image0[16+4]=6u;
    image1[16+3]=200u;
    uint8_t hit=90u;
    for(unsigned yy=0;yy<3;yy++)for(unsigned xx=0;xx<3;xx++)
       for(unsigned pix=0;pix<256u;pix++) {
        memset(image0+16,0,9);
        image0[16+yy*3u+xx]=(uint8_t)pix;
        for(int dy=0;dy<3;dy++)for(int dx=0;dx<3;dx++) {
            int32_t x=-100+(int32_t)xx*3+dx;
            int32_t y=200+(int32_t)yy*3+dy;
            must(moo2_v131_derived_point_in_one_nebula(
                &ctx,0,x,y,&hit)==MOO2_V131_NEBULA_OK);
            must(hit==(uint8_t)(pix>5u));
        }
       }
    memset(image0+16,0,9);
    image0[16+4u]=6u;
    for(int offset=-10;offset<20;offset++) {
        int32_t x=-100+offset;
        must(moo2_v131_derived_point_in_one_nebula(
            &ctx,0,x,204,&hit)==MOO2_V131_NEBULA_OK);
        /* Original signed IDIV truncates -1 or -2 to zero, so
           negative offset -2,-1 still maps to grid x=0. */
        int32_t col=offset/3;
        must(hit==(uint8_t)(col==1));
    }
    must(moo2_v131_derived_point_in_some_nebula(
        &ctx,403,-297,&hit)==MOO2_V131_NEBULA_OK);
    must(hit==1u);
    must(moo2_v131_derived_point_in_some_nebula(
        &ctx,404,-300,&hit)==MOO2_V131_NEBULA_OK);
    must(hit==0u);
    ctx.nebula_count=0u;
    must(moo2_v131_derived_point_in_some_nebula(
        &ctx,403,-297,&hit)==MOO2_V131_NEBULA_OK);
    must(hit==0u);
    ctx.nebula_count=2u;
    image0[0]=255u;image0[1]=255u;
    must(moo2_v131_derived_point_in_one_nebula(
        &ctx,0,-100,200,&hit)==MOO2_V131_NEBULA_INVALID);
    word(image0,3);
    image0[16u]=10u;
    bm[0].size=16u;
    must(moo2_v131_derived_point_in_one_nebula(
        &ctx,0,-100,200,&hit)==MOO2_V131_NEBULA_INVALID);
    puts("PASS 2304 full-byte nebula cells x 9 subcell positions, negative-coordinate truncation and any-nebula scan");
}
