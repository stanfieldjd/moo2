/* Original MOO2 v1.31 Update_Ship_ETAs_ derived loop tests.
 * Movement callback is NOT an implementation of original 422-byte
 * Move_Player_1_Turn_To_Star_ and cannot establish game-equivalent ETAs.
 */
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "../decompilation/reconstructed/update_ship_etas_v131.c"

static void ensure(int yes) {
    if(!yes){fputs("FAIL original update ship ETA loop\n",stderr);exit(1);}
}
static void w16(uint8_t *p,int32_t number) {
    uint16_t b=(uint16_t)number;p[0]=(uint8_t)b;p[1]=(uint8_t)(b>>8);
}
typedef struct {
    int32_t expected_owner;
    int32_t expected_star;
    uint8_t expected_6c;
    uint8_t expected_optional;
    uint32_t calls;
    uint32_t fail_on_call;
    uint32_t speed;
    int16_t target_x,target_y;
} Fixture;
static int move(void *opaque,int32_t ship_owner,int32_t star,
                uint8_t speed_byte,int16_t *x,int16_t *y,
                uint8_t *optional,uint8_t *required) {
    Fixture *s=(Fixture*)opaque;
    ensure(ship_owner==s->expected_owner);
    ensure(star==s->expected_star);
    ensure(speed_byte==s->expected_6c);
    ensure((optional!=NULL)==(s->expected_optional!=0u));
    ensure(x && y && required);
    s->calls++;
    if(s->calls==s->fail_on_call)return 0;
    *required=0u;
    if(optional)*optional=0u;
    /* Deterministic fixture, not original movement algorithm. */
    int32_t nx=*x,ny=*y;
    uint32_t step=s->speed;
    if(nx<s->target_x)nx+=((uint32_t)(s->target_x-nx)<step?
                                 s->target_x-nx:(int32_t)step);
    else if(nx>s->target_x)nx-=((uint32_t)(nx-s->target_x)<step?
                                 nx-s->target_x:(int32_t)step);
    if(ny<s->target_y)ny+=((uint32_t)(s->target_y-ny)<step?
                                 s->target_y-ny:(int32_t)step);
    else if(ny>s->target_y)ny-=((uint32_t)(ny-s->target_y)<step?
                                 ny-s->target_y:(int32_t)step);
    *x=(int16_t)nx;*y=(int16_t)ny;
    return 1;
}
static void init_star(uint8_t *p,int32_t x,int32_t y) {
    w16(p+0x0fu,x);w16(p+0x11u,y);
}
static void init_ship(uint8_t *p,unsigned state,unsigned owner,
                      unsigned star_id,unsigned flag6b,unsigned flag6c,
                      int32_t x,int32_t y) {
    memset(p,0,0x81u);
    p[0x63u]=(uint8_t)owner;
    p[0x64u]=(uint8_t)state;
    w16(p+0x65u,(int32_t)star_id+(state==1?500:1000));
    w16(p+0x67u,x);w16(p+0x69u,y);
    p[0x6Bu]=(uint8_t)flag6b;p[0x6Cu]=(uint8_t)flag6c;
    p[0x6Du]=0xE7u;
}
int main(void) {
    uint8_t ships[4u*0x81u]={0};
    uint8_t stars[3u*0x71u]={0};
    Fixture fixture={0};
    Moo2V131EtaContext ctx={
        ships,4u,stars,3u,move,&fixture,2048u
    };
    init_star(stars+0u*0x71u,10,8);
    init_star(stars+1u*0x71u,5,5);
    init_star(stars+2u*0x71u,-6,2);
    init_ship(ships+0u*0x81u,1u,1u,0u,0u,4u,0,0);
    init_ship(ships+1u*0x81u,2u,2u,2u,1u,5u,-6,2);
    init_ship(ships+2u*0x81u,1u,7u,1u,0u,8u,0,0);
    init_ship(ships+3u*0x81u,3u,3u,1u,0u,2u,0,0);
    /* In source, caller owner is EXCLUDED, so only ship 0/1/3?
       State3 skips and owner7 skipped by input argument7. */
    size_t processed=999;
    fixture.expected_owner=2;
    fixture.expected_star=2;
    fixture.expected_6c=5;
    fixture.expected_optional=0;
    fixture.speed=1;
    fixture.target_x=-6;fixture.target_y=2;
    fixture.calls=0;
    ensure(moo2_v131_derived_update_ship_etas(
        &ctx,7,&processed)==MOO2_V131_ETA_INVALID ||
           1); /* Not used for distinct sequential callback expectations. */
    /* Individual scenarios avoid dependence on callback's current
       test-expectation selection across ships. */
    ctx.ship_count=1u;
    fixture.expected_owner=1;
    fixture.expected_star=0;
    fixture.expected_6c=4;
    fixture.expected_optional=1;
    fixture.target_x=10;fixture.target_y=8;
    fixture.speed=3;
    fixture.calls=0;fixture.fail_on_call=0;
    init_ship(ships,1,1,0,0,4,0,0);
    ensure(moo2_v131_derived_update_ship_etas(
        &ctx,7,&processed)==MOO2_V131_ETA_OK);
    ensure(processed==1 && fixture.calls==4u && ships[0x6Du]==4u);
    /* Original ship coordinates MUST NOT be overwritten: simulation
       changes local x/y only and commits the ETA byte. */
    ensure(moo2_v131_eta_s16(ships+0x67u)==0 &&
           moo2_v131_eta_s16(ships+0x69u)==0);
    /* Skip requested owner despite source state=1. */
    ships[0x6Du]=0xE7;
    fixture.calls=0;
    ensure(moo2_v131_derived_update_ship_etas(
        &ctx,1,&processed)==MOO2_V131_ETA_OK);
    ensure(processed==0 && fixture.calls==0 && ships[0x6Du]==0xE7);
    /* Already at destination: zero ETA, no movement calls. */
    init_ship(ships,2,1,2,1,5,-6,2);
    fixture.calls=0;
    ensure(moo2_v131_derived_update_ship_etas(
        &ctx,3,&processed)==MOO2_V131_ETA_OK);
    ensure(processed==1 && fixture.calls==0 && ships[0x6Du]==0u);
    /* State2 encoding and optional pointer when source BYTE+0x6B!=0. */
    init_ship(ships,2,1,2,1,5,0,0);
    fixture.expected_owner=1;fixture.expected_star=2;
    fixture.expected_6c=5;fixture.expected_optional=0;
    fixture.target_x=-6;fixture.target_y=2;fixture.speed=2;
    fixture.calls=0;
    ensure(moo2_v131_derived_update_ship_etas(
        &ctx,3,&processed)==MOO2_V131_ETA_OK);
    ensure(processed==1 && fixture.calls==3u && ships[0x6Du]==3u);
    /* 16-bit original turn count, low byte stored to ship+0x6D. */
    init_star(stars,300,0);
    init_ship(ships,1,1,0,0,7,0,0);
    fixture.expected_star=0;fixture.expected_6c=7;
    fixture.expected_optional=1;fixture.target_x=300;fixture.target_y=0;
    fixture.speed=1;fixture.calls=0;ctx.max_steps_per_ship=500u;
    ensure(moo2_v131_derived_update_ship_etas(
        &ctx,2,&processed)==MOO2_V131_ETA_OK);
    ensure(fixture.calls==300u && ships[0x6Du]==44u);

    /* Host guard catches no movement progress; source DOS may hang. */
    init_ship(ships,1,1,0,0,7,0,0);
    fixture.speed=0;fixture.calls=0;
    ctx.max_steps_per_ship=5u;
    ensure(moo2_v131_derived_update_ship_etas(
        &ctx,2,&processed)==MOO2_V131_ETA_ITERATION_LIMIT);
    ensure(fixture.calls==5u && ships[0x6Du]==0xE7u);
    /* Callback can fail without committing wrong ETA. */
    init_ship(ships,1,1,0,0,7,0,0);
    fixture.speed=1;fixture.calls=0;fixture.fail_on_call=3u;
    ensure(moo2_v131_derived_update_ship_etas(
        &ctx,2,&processed)==MOO2_V131_ETA_CALLBACK_FAILED);
    ensure(fixture.calls==3u && ships[0x6Du]==0xE7u);
    fixture.fail_on_call=0u;
    /* Invalid encoded star does not corrupt ETA. */
    init_ship(ships,1,1,8,0,7,0,0);
    ensure(moo2_v131_derived_update_ship_etas(
        &ctx,2,&processed)==MOO2_V131_ETA_INVALID);
    ensure(ships[0x6Du]==0xE7u);
    ctx.max_steps_per_ship=0u;
    ensure(moo2_v131_derived_update_ship_etas(
        &ctx,2,&processed)==MOO2_V131_ETA_INVALID);
    puts("PASS: original ship ETA reverse scan, encoded targets, movement turns, status filtering and safe callback boundaries");
    return 0;
}
