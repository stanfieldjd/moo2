/* C11 tests for isolated original v1.31 combat weapon-state reconstructions.
 * These are derived-code tests, not original DOS execution equivalence tests.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/combat_weapon_status_v131.c"

static void word(uint8_t *dst,int16_t val) {
    uint16_t n=(uint16_t)val;
    dst[0]=(uint8_t)n;
    dst[1]=(uint8_t)(n>>8);
}

static void test_division(uint8_t *record,int16_t n,int16_t d,
                          int32_t expected) {
    word(record+0x104,n);
    word(record+0x114,d);
    int32_t out=INT32_MIN;
    Moo2V131WeaponHelperStatus got=
        moo2_v131_derived_weapons_left(record,0x139,0,&out);
    if(got!=MOO2_V131_WEAPON_HELPER_OK || out!=expected){
        fprintf(stderr,"FAILED: %d / %d -> %ld expected %ld\n",
                (int)n,(int)d,(long)out,(long)expected);
        exit(1);
    }
}

int main(void) {
    uint8_t ships[2*0x139];
    memset(ships,0,sizeof(ships));
    test_division(ships,0,1,0);
    test_division(ships,1,1,1);
    test_division(ships,3,2,2);
    test_division(ships,4,2,2);
    test_division(ships,5,2,3);
    test_division(ships,-3,2,-1);
    test_division(ships,-5,2,-2);
    test_division(ships,3,-2,0);  /* trunc -1, increment = 0 */
    test_division(ships,5,-2,-1); /* trunc -2, increment = -1 */
    test_division(ships,-3,-2,1);
    test_division(ships,-4,-2,2);
    test_division(ships,32767,1,32767);
    test_division(ships,-32768,1,-32768);
    test_division(ships,-32768,-1,32768);
    test_division(ships,32767,-1,-32767);
    int32_t ignored=987;
    word(ships+0x114,0);
    if(moo2_v131_derived_weapons_left(ships,0x139,0,&ignored)!=
         MOO2_V131_WEAPON_HELPER_ZERO_DIVISOR || ignored!=987)abort();

    /* Fill every original +0x104 and +0x114 16-bit bank position,
       and ensure the selected slot uses independent bank values. */
    memset(ships,0,sizeof(ships));
    for(int i=0;i<8;i++){
        word(ships+0x104+2*i,(int16_t)(2*i+1));
        word(ships+0x114+2*i,2);
        int32_t out=-99;
        if(moo2_v131_derived_weapons_left(ships,0x139,(int16_t)i,&out) ||
           out!=i+1)abort();
    }
    if(moo2_v131_derived_weapons_left(ships,0x139,-1,&ignored)!=
       MOO2_V131_WEAPON_HELPER_INVALID_INPUT)abort();
    if(moo2_v131_derived_weapons_left(ships,0x110,7,&ignored)!=
       MOO2_V131_WEAPON_HELPER_INVALID_INPUT)abort();

    memset(ships,0,sizeof(ships));
    for(int player=0;player<2;player++){
        for(int slot=0;slot<8;slot++){
            size_t at=(size_t)player*0x139u+0x5Au+(size_t)slot*11u;
            for(int v=0;v<256;v++){
                ships[at]=(uint8_t)v;
                uint8_t on=255,off=255;
                Moo2V131WeaponHelperStatus a=
                    moo2_v131_derived_weapon_is_on(ships,2,(int16_t)player,
                                                    (int16_t)slot,&on);
                Moo2V131WeaponHelperStatus b=
                    moo2_v131_derived_weapon_is_off(ships,2,(int16_t)player,
                                                     (int16_t)slot,&off);
                if(a || b || on!=(v==1) || off!=(v!=1) || on+off!=1){
                    fprintf(stderr,"BAD FLAG ship=%d slot=%d flag=%d\n",
                            player,slot,v);
                    exit(2);
                }
            }
        }
    }
    uint8_t out=255;
    if(moo2_v131_derived_weapon_is_on(ships,2,0,8,&out)!=
       MOO2_V131_WEAPON_HELPER_INVALID_INPUT)abort();
    if(moo2_v131_derived_weapon_is_off(ships,2,2,0,&out)!=
       MOO2_V131_WEAPON_HELPER_INVALID_INPUT)abort();
    if(moo2_v131_derived_weapon_is_off(ships,2,-1,0,&out)!=
       MOO2_V131_WEAPON_HELPER_INVALID_INPUT)abort();
    puts("PASS: weapon division boundaries, all eight banks and all 4096 status-byte combinations");
    return 0;
}
