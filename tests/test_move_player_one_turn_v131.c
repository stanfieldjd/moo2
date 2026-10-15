/* Source-anchored whole 422-byte MOO2 v1.31 movement reconstruction.
 * Uses real derived integer sqrt, nebula bitmap and warp-radius helpers.
 * No approximation callbacks; does not execute original DOS for
 * differential comparison. Valid game coordinates and speed<=255 only.
 */
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../decompilation/reconstructed/isqrt_v131.c"
#include "../decompilation/reconstructed/point_in_nebula_v131.c"
#include "../decompilation/reconstructed/point_in_warp_field_v131.c"
#include "../decompilation/reconstructed/move_player_one_turn_v131.c"

static void must(int good) {
    if(!good){fputs("FAIL original one-turn source movement\n",stderr);exit(1);}
}
static void write16(uint8_t *ptr,int32_t x){
    uint16_t n=(uint16_t)x;ptr[0]=(uint8_t)n;ptr[1]=(uint8_t)(n>>8);
}
static void scenario(Moo2V131MoveContext *ctx,int32_t owner,
        int16_t sx,int16_t sy,uint32_t speed,
        int16_t wantx,int16_t wanty,
        uint8_t *optional,unsigned want_opt,unsigned want_warp)
{
    int16_t x=1111,y=2222;
    uint8_t warp=69u;
    if(optional)*optional=0;
    must(moo2_v131_derived_move_player_one_turn(
        ctx,owner,0,sx,sy,speed,&x,&y,optional,&warp)
        ==MOO2_V131_MOVE_OK);
    must(x==wantx && y==wanty &&
         warp==(uint8_t)want_warp);
    if(optional)must(*optional==(uint8_t)want_opt);
}
int main(void)
{
    uint8_t star[0x71u]={0};
    uint8_t nebula[5u]={0};
    uint8_t image[16u+9u]={0};
    Moo2V131NebulaBitmap bitmap={image,sizeof(image)};
    Moo2V131NebulaContext neb={nebula,0u,&bitmap};
    Moo2V131MoveContext ctx={star,1u,&neb};
    uint8_t optional=0;
    /* Original distance 150, +120,+90 delta, step=30, exact
       projected first X=24,Y=18, fifth lands on destination. */
    write16(star+0x0fu,120);write16(star+0x11u,90);
    scenario(&ctx,1,0,0,1,24,18,&optional,0,0);
    scenario(&ctx,1,0,0,2,48,36,&optional,0,0);
    scenario(&ctx,1,0,0,5,120,90,&optional,0,0);
    scenario(&ctx,1,0,0,0,24,18,&optional,0,0);
    /* Signed coordinate differences both negative, ceiling towards
       target from original absolute projection, then subtract. */
    write16(star+0x0fu,-120);write16(star+0x11u,-90);
    scenario(&ctx,1,0,0,1,-24,-18,&optional,0,0);
    scenario(&ctx,1,0,0,5,-120,-90,&optional,0,0);
    /* Already at target must write destination and zero warp if
       star's mask has no other players. */
    write16(star+0x0fu,45);write16(star+0x11u,60);
    scenario(&ctx,1,45,60,1,45,60,&optional,0,0);

    /* Original special case: on arrival CODE 0xDBBA8 writes owner
       low WORD zero. Warp test then EXCLUDES owner0, not owner3.
       Star bit3 therefore triggers a warp hit exactly on arrival. */
    star[0x39u]=(uint8_t)(1u<<3);
    scenario(&ctx,3,45,60,1,45,60,&optional,0,1);
    /* An intermediate point sees original owner3 and excludes it. */
    write16(star+0x0fu,200);write16(star+0x11u,60);
    scenario(&ctx,3,0,60,1,30,60,&optional,0,0);
    star[0x39u]=0;

    /* Source calls nebula test ONLY if optional output pointer
       supplied. Point (30,0) is within synthetic 1x1 pixel value6. */
    neb.nebula_count=1u;
    write16(nebula,30);write16(nebula+2u,0);
    write16(image,1);write16(image+2u,1);
    image[16u]=6u;
    write16(star+0x0fu,120);write16(star+0x11u,0);
    scenario(&ctx,1,0,0,4,30,0,&optional,1,0);
    scenario(&ctx,1,0,0,4,120,0,NULL,0,0);
    image[16u]=5u;
    scenario(&ctx,1,0,0,4,120,0,&optional,0,0);
    neb.nebula_count=0u;

    /* Independent source projection reference for axis-aligned cases:
       distance sqrt(dx^2)=abs(dx), so candidate coordinate after t
       steps is exactly start +/- min(t*30, abs(dx)) for valid grid. */
    for(int dx=-250;dx<=250;dx++)if(dx!=0) {
        write16(star+0x0fu,dx);write16(star+0x11u,0);
        uint32_t steps=4u;
        int32_t absx=dx<0?-dx:dx;
        int32_t travel=absx<120?absx:120;
        int16_t expected=(int16_t)(dx<0?-travel:travel);
        scenario(&ctx,1,0,0,steps,expected,0,NULL,0,0);
    }
    /* Unsafe stars and null outputs: host prevents DOS bad reads. */
    int16_t x=12,y=34;uint8_t flag=1u;
    must(moo2_v131_derived_move_player_one_turn(
        &ctx,1,1,0,0,1,&x,&y,NULL,&flag)==MOO2_V131_MOVE_INVALID);
    must(x==12 && y==34 && flag==1u);
    must(moo2_v131_derived_move_player_one_turn(
        &ctx,8,0,0,0,1,&x,&y,NULL,&flag)==MOO2_V131_MOVE_INVALID);
    puts("PASS 422-byte source movement projection, exact arrival, original warp owner overwrite, nebula gating and 500 axis paths");
}
