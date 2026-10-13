/* Regression for bounded ORIGINAL v1.31 Fire_Ship_ slot-write semantics.
 * Not a test of the original DOS game or the full firing engine.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/fire_ship_ammo_mutations_v131.c"

static void wr(uint8_t *p,uint16_t value){
    p[0]=(uint8_t)value;
    p[1]=(uint8_t)(value>>8);
}
static void must(int ok){if(!ok){fputs("FAIL fire ship slot mutation\n",stderr);exit(1);}}

int main(void){
    uint8_t ship[0x139];
    uint8_t defs[64*28];
    memset(ship,0,sizeof(ship));
    memset(defs,0,sizeof(defs));
    for(int slot=0;slot<8;slot++){
        uint8_t *item=ship+0x52u+(size_t)slot*11u;
        uint8_t *count=ship+0x58u+(size_t)slot*11u;
        wr(item,(uint16_t)(slot+1));
        for(int source=0;source<256;source++){
            defs[(size_t)(slot+1)*28u+13u]=(uint8_t)source;
            wr(count,0xa55au);
            must(moo2_v131_derived_after_fire_missile_slot_write(
                 ship,sizeof(ship),(int16_t)slot,2u,defs,64)==MOO2_V131_FIRE_SLOT_OK);
            must(moo2_v131_fire_u16(count)==(uint16_t)source);
        }
        for(uint32_t n=0;n<=0xffffu;n++){
            wr(count,(uint16_t)n);
            must(moo2_v131_derived_after_fire_bomb_slot_write(
                ship,sizeof(ship),(int16_t)slot)==MOO2_V131_FIRE_SLOT_OK);
            must(moo2_v131_fire_u16(count)==(uint16_t)(n-1u));
        }
        /* Original missile alternative path: any mode other than 2 decrements. */
        for(uint32_t n=0;n<=0xffffu;n+=127){
            wr(count,(uint16_t)n);
            must(moo2_v131_derived_after_fire_missile_slot_write(
                ship,sizeof(ship),(int16_t)slot,0u,NULL,0u)==MOO2_V131_FIRE_SLOT_OK);
            must(moo2_v131_fire_u16(count)==(uint16_t)(n-1u));
        }
        wr(count,0);
        must(moo2_v131_derived_after_fire_missile_slot_write(
                ship,sizeof(ship),(int16_t)slot,3u,NULL,0u)==MOO2_V131_FIRE_SLOT_OK);
        must(moo2_v131_fire_u16(count)==0xffffu);
    }
    uint8_t copy[sizeof(ship)];
    memcpy(copy,ship,sizeof(ship));
    must(moo2_v131_derived_after_fire_bomb_slot_write(ship,sizeof(ship),8)==
         MOO2_V131_FIRE_SLOT_INVALID);
    must(moo2_v131_derived_after_fire_missile_slot_write(
         ship,sizeof(ship),-1,2u,defs,64)==MOO2_V131_FIRE_SLOT_INVALID);
    must(moo2_v131_derived_after_fire_missile_slot_write(
         ship,0x100u,0,2u,defs,64)==MOO2_V131_FIRE_SLOT_INVALID);
    wr(ship+0x52u,0xffffu);
    must(moo2_v131_derived_after_fire_missile_slot_write(
         ship,sizeof(ship),0,2u,defs,64)==MOO2_V131_FIRE_SLOT_INVALID);
    wr(ship+0x52u,0);
    must(moo2_v131_derived_after_fire_missile_slot_write(
         ship,sizeof(ship),0,2u,NULL,0)==MOO2_V131_FIRE_SLOT_INVALID);
    (void)copy;
    puts("PASS original firing-site writes: all eight slots, full 16-bit decrement range, and reload bytes");
    return 0;
}
