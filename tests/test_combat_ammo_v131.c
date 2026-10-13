/* Isolated tests for the derived ORIGINAL v1.31 combat-ammo routine.
 * Original executable and LBX files are intentionally not needed.
 * These tests cover the recovered cases; they are NOT DOS differential tests.
 *
 * Compile:
 *   gcc -std=c11 -O2 -Wall -Wextra -Werror -pedantic \
 *       tests/test_combat_ammo_v131.c -o /tmp/moo2_combat_ammo_check
 *   /tmp/moo2_combat_ammo_check
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "../decompilation/reconstructed/combat_ammo_v131.c"

typedef struct {
    uint16_t respond_to;
    unsigned queries;
    uint16_t most_recent_id;
} SpecialTestContext;

static uint16_t has_special(void *opaque,int16_t combat_ship_id,uint16_t special_id)
{
    SpecialTestContext *s=(SpecialTestContext *)opaque;
    if (combat_ship_id!=0) abort();
    s->queries++;
    s->most_recent_id=special_id;
    return special_id==s->respond_to ? 1u : 0u;
}

static void u16(uint8_t *p,uint16_t word)
{
    p[0]=(uint8_t)word;
    p[1]=(uint8_t)(word>>8);
}

static void check_result(Moo2V131CombatAmmoContext *ctx,
                         uint16_t expected,const char *case_name)
{
    uint16_t got=999;
    Moo2V131CombatAmmoStatus st=
       moo2_v131_derived_ship_out_of_ammo(ctx,0,&got);
    if (st!=MOO2_V131_COMBAT_AMMO_OK || got!=expected) {
        fprintf(stderr,"FAILED %s: status=%d got=%u expected=%u\n",
                case_name,(int)st,(unsigned)got,(unsigned)expected);
        exit(1);
    }
}

static void set_item(uint8_t *ship,unsigned slot,uint16_t weapon_id,
                     uint8_t installed,int16_t stock)
{
    uint8_t *item=ship+0x52+slot*11u;
    u16(item,weapon_id);
    item[2]=installed;
    u16(item+6,(uint16_t)stock);
}

int main(void)
{
    uint8_t ships[2*0x139];
    uint8_t definitions[64*28];
    uint8_t missiles[301*26];
    SpecialTestContext special={0,0,0};
    Moo2V131CombatAmmoContext ctx={
        ships,2,definitions,64,missiles,301,0,
        has_special,&special
    };
    memset(ships,0,sizeof(ships));
    memset(definitions,0,sizeof(definitions));
    memset(missiles,0,sizeof(missiles));
    /* No original missile record initially belongs to combat ship zero. */
    for(unsigned i=0;i<301;i++)u16(missiles+i*26+4,0xffffu);

    check_result(&ctx,1,"empty ship");
    special.respond_to=0x25;
    check_result(&ctx,0,"special 0x25 short circuit");
    if(special.queries!=3||special.most_recent_id!=0x25)abort();
    special.respond_to=0x26;
    special.queries=0;
    check_result(&ctx,0,"special 0x26 short circuit");
    if(special.queries!=2||special.most_recent_id!=0x26)abort();
    special.respond_to=0;
    special.queries=0;

    set_item(ships,0,1,0,0);
    definitions[1*28+12]=0;
    check_result(&ctx,1,"inactive weapon slot");
    set_item(ships,0,0,1,2);
    check_result(&ctx,1,"zero weapon ID");
    set_item(ships,0,1,1,0);
    check_result(&ctx,0,"category 0 ignores stock");

    definitions[1*28+12]=1;
    check_result(&ctx,1,"category 1 zero stock");
    set_item(ships,0,1,1,-2);
    check_result(&ctx,1,"category 1 negative stock");
    set_item(ships,0,1,1,1);
    check_result(&ctx,0,"category 1 positive stock");

    definitions[1*28+12]=2;
    set_item(ships,0,1,1,0);
    check_result(&ctx,0,"category 2 ignores stock");

    definitions[1*28+12]=3;
    ships[0x20]=5;
    ctx.unnamed_comparison_word=6;
    set_item(ships,0,1,1,1);
    check_result(&ctx,1,"category 3 unmatched external word");
    ctx.unnamed_comparison_word=5;
    check_result(&ctx,0,"category 3 matching external word");
    set_item(ships,0,1,1,0);
    check_result(&ctx,1,"category 3 zero stock");
    set_item(ships,0,1,1,-1);
    check_result(&ctx,1,"category 3 negative stock");

    definitions[1*28+12]=4;
    set_item(ships,0,1,1,1);
    check_result(&ctx,0,"category 4 positive stock");
    set_item(ships,0,1,1,0);
    check_result(&ctx,1,"category 4 zero stock and no launched fighters");
    definitions[5*28+12]=4;
    u16(missiles+299*26,5);
    u16(missiles+299*26+4,0);
    check_result(&ctx,0,"category 4 last scanned fighter supports ship");
    u16(missiles+299*26+4,1);
    check_result(&ctx,1,"category 4 other ship fighter not counted");
    u16(missiles+300*26+4,0);
    u16(missiles+300*26,5);
    check_result(&ctx,1,"category 4 after original 300 slot limit ignored");
    u16(missiles+300*26+4,0xffffu);

    definitions[0x21*28+12]=5;
    set_item(ships,0,0x21,1,0);
    check_result(&ctx,1,"category 5 weapon 0x21 requires stock");
    set_item(ships,0,0x21,1,1);
    check_result(&ctx,0,"category 5 weapon 0x21 with stock");
    definitions[6*28+12]=5;
    set_item(ships,0,6,1,0);
    check_result(&ctx,0,"category 5 weapon other than 0x21");

    definitions[1*28+12]=6;
    set_item(ships,0,1,1,50);
    check_result(&ctx,1,"unknown category ignored");
    set_item(ships,7,6,1,0);
    check_result(&ctx,0,"eighth slot reached");

    uint16_t value;
    if(moo2_v131_derived_ship_out_of_ammo(&ctx,-1,&value)!=
       MOO2_V131_COMBAT_AMMO_INVALID_INPUT)abort();
    if(moo2_v131_derived_ship_out_of_ammo(&ctx,2,&value)!=
       MOO2_V131_COMBAT_AMMO_INVALID_INPUT)abort();

    printf("PASS: 24 derived original combat-ammo branch/boundary cases\n");
    return 0;
}
