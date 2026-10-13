/* Original MOO2 v1.31 92-byte colony defense packing regression.
 * Exhaustive per-field values and bitwise overlaps; not DOS execution.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/combat_planet_defenses_v131.c"

static void must(int yes){if(!yes){fputs("FAIL original packed colony defenses\n",stderr);exit(1);}}
static uint32_t independent(uint8_t a,uint8_t b,uint8_t c,uint8_t d) {
    return (uint32_t)a | 2u*(uint32_t)b | 4u*(uint32_t)c | 8u*(uint32_t)d;
}
int main(void)
{
    uint8_t records[2*0x169]={0};
    uint32_t result=99;
    must(moo2_v131_derived_combat_planet_defenses(NULL,0,-1,&result)==MOO2_V131_COLONY_DEFENSE_OK);
    must(result==0u);
    must(moo2_v131_derived_combat_planet_defenses(records,2,0,&result)==MOO2_V131_COLONY_DEFENSE_OK);
    must(result==0u);
    uint8_t *colony=records+0x169u;
    const size_t offsets[4]={0x150u,0x151u,0x160u,0x165u};
    for(int field=0;field<4;field++){
        for(int v=0;v<256;v++) {
            memset(colony,0,0x169u);
            colony[offsets[field]]=(uint8_t)v;
            must(moo2_v131_derived_combat_planet_defenses(records,2,1,&result)==MOO2_V131_COLONY_DEFENSE_OK);
            must(result==(uint32_t)v << field);
        }
    }
    /* OR is not equivalent to adding when nonbinary bytes overlap. */
    for(unsigned n=0;n<65536u;n++) {
        colony[0x150]=(uint8_t)n;
        colony[0x151]=(uint8_t)(n>>8);
        colony[0x160]=(uint8_t)((n*11u)>>3);
        colony[0x165]=(uint8_t)((n*7u)>>5);
        must(moo2_v131_derived_combat_planet_defenses(records,2,1,&result)==MOO2_V131_COLONY_DEFENSE_OK);
        uint32_t expected=independent(colony[0x150],colony[0x151],
                                      colony[0x160],colony[0x165]);
        must(result==expected);
    }
    result=777;
    must(moo2_v131_derived_combat_planet_defenses(records,2,-2,&result)==MOO2_V131_COLONY_DEFENSE_INVALID_INPUT);
    must(result==777);
    must(moo2_v131_derived_combat_planet_defenses(records,2,2,&result)==MOO2_V131_COLONY_DEFENSE_INVALID_INPUT);
    must(result==777);
    must(moo2_v131_derived_combat_planet_defenses(records,2,0,NULL)==MOO2_V131_COLONY_DEFENSE_INVALID_INPUT);
    puts("PASS: original 92-byte colony defense four-field packing, 66560 cases");
    return 0;
}
