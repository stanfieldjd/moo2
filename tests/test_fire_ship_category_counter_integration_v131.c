/*
 * Source-derived integration regression: Fire_Ship_ uses the weapon
 * definition's category BYTE at +0x0C for its 6-case firing switch
 * AND category 2 for a post-missile ammo counter overwrite at +0x58.
 * This tests only the dispatch-to-write linkage, not actual DOS firing.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/fire_ship_category_dispatch_v131.c"
#include "../decompilation/reconstructed/fire_ship_ammo_mutations_v131.c"

static void require(int p){if(!p){fputs("FAIL Fire_Ship category and ammo integration\n",stderr);exit(1);}}
static void setword(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}

int main(void) {
    uint8_t ship[313]={0};
    uint8_t defs[32*28]={0};
    unsigned checked=0;
    for (int slot=0;slot<8;slot++) {
        uint8_t *item=ship+0x52u+(size_t)slot*11u;
        uint8_t *counter=ship+0x58u+(size_t)slot*11u;
        int id=slot+1;
        setword(item,(uint16_t)id);
        for (int category=0;category<=5;category++) {
            defs[(size_t)id*28u+12u]=(uint8_t)category;
            Moo2V131FireCategoryDispatch path={0};
            require(moo2_v131_derived_fire_ship_category(
                ship,sizeof(ship),(int16_t)slot,defs,32,&path)==MOO2_V131_FIRE_ROUTE_OK);
            if(path.path!=MOO2_V131_FIRE_ROUTE_MISSILE) {
                require(category==0 || category==3 || category==5);
                continue;
            }
            for(int reload=0;reload<256;reload++) {
                defs[(size_t)id*28u+13u]=(uint8_t)reload;
                setword(counter,0x4321u);
                require(moo2_v131_derived_after_fire_missile_slot_write(
                    ship,sizeof(ship),(int16_t)slot,path.weapon_category,
                    defs,32)==MOO2_V131_FIRE_SLOT_OK);
                const uint16_t expected=(uint16_t)(
                    category==2 ? reload : 0x4320);
                require(moo2_v131_fire_u16(counter)==expected);
                require(path.replace_counter_after_missile==(category==2));
                checked++;
            }
        }
    }
    printf("PASS: %u derived category-driven missile state writes across 8 slots\n",checked);
    return 0;
}
