/* Derived-code regression for original MOO2 v1.31 firing category router.
 * Does NOT execute the original DOS game.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/fire_ship_category_dispatch_v131.c"

static void expect(int ok){if(!ok){fputs("FAIL original fire category dispatch\n",stderr);exit(1);}}
static void wr(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}

int main(void) {
    uint8_t ship[313]={0};
    uint8_t defs[16*28]={0};
    const uint32_t targets[6]={0x28FD1,0x28F6A,0x28F6A,0x290E2,0x28F6A,0x29113};
    const Moo2V131FireRoute action[6]={
        MOO2_V131_FIRE_ROUTE_BEAM,MOO2_V131_FIRE_ROUTE_MISSILE,
        MOO2_V131_FIRE_ROUTE_MISSILE,MOO2_V131_FIRE_ROUTE_BOMB,
        MOO2_V131_FIRE_ROUTE_MISSILE,MOO2_V131_FIRE_ROUTE_SPECIAL
    };
    for(int slot=0;slot<8;slot++) {
        const int id=slot+1;
        wr(ship+0x52u+(size_t)slot*11u,(uint16_t)id);
        for(int n=0;n<=255;n++) {
            defs[(size_t)id*28u+12u]=(uint8_t)n;
            Moo2V131FireCategoryDispatch actual={0};
            expect(moo2_v131_derived_fire_ship_category(
                ship,sizeof(ship),(int16_t)slot,defs,16,&actual)==MOO2_V131_FIRE_ROUTE_OK);
            const Moo2V131FireRoute expected=n<=5?action[n]:
                MOO2_V131_FIRE_ROUTE_NONE_IN_SIX_CASE_TABLE;
            expect(actual.weapon_category==(uint8_t)n);
            expect(actual.path==expected);
            expect(actual.original_code_case_target==(n<=5?targets[n]:0u));
            expect(actual.replace_counter_after_missile==(n==2));
        }
    }
    Moo2V131FireCategoryDispatch actual={0};
    expect(moo2_v131_derived_fire_ship_category(ship,sizeof(ship),-1,defs,16,&actual)
        ==MOO2_V131_FIRE_ROUTE_INVALID_INPUT);
    expect(moo2_v131_derived_fire_ship_category(ship,sizeof(ship),8,defs,16,&actual)
        ==MOO2_V131_FIRE_ROUTE_INVALID_INPUT);
    expect(moo2_v131_derived_fire_ship_category(ship,280,0,defs,16,&actual)
        ==MOO2_V131_FIRE_ROUTE_INVALID_INPUT);
    wr(ship+0x52,0xffffu);
    expect(moo2_v131_derived_fire_ship_category(ship,sizeof(ship),0,defs,16,&actual)
        ==MOO2_V131_FIRE_ROUTE_INVALID_INPUT);
    wr(ship+0x52,16);
    expect(moo2_v131_derived_fire_ship_category(ship,sizeof(ship),0,defs,16,&actual)
        ==MOO2_V131_FIRE_ROUTE_INVALID_INPUT);
    puts("PASS: original six-case mapping on all 2048 category/slot combinations");
    return 0;
}
