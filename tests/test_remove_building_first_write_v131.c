/* v1.31 Remove_Building_ first source-byte-mutation regression.
 * Does not claim to implement 493-byte original routine's side effects.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"

static void must(int yes){if(!yes){fputs("FAIL original Remove_Building_ first write\n",stderr);exit(1);}}
int main(void){
    uint8_t colonies[3u*0x169u]={0};
    for(int colony=0;colony<3;colony++) {
        for(int building=0;building<49;building++) {
            for(unsigned v=0;v<=255u;v++) {
                memset(colonies,0xA5u,sizeof(colonies));
                uint8_t *p=colonies+(size_t)colony*0x169u+
                           0x136u+(size_t)building;
                *p=(uint8_t)v;
                must(moo2_v131_derived_remove_building_first_write(
                    colonies,3,(int16_t)colony,(int16_t)building)
                     ==MOO2_V131_BUILDING_FIRST_WRITE_OK);
                must(*p==0u);
                for(size_t k=0;k<sizeof(colonies);k++) {
                    if(&colonies[k]==p)continue;
                    must(colonies[k]==0xA5u);
                }
            }
        }
    }
    uint8_t before[sizeof(colonies)];
    memcpy(before,colonies,sizeof(colonies));
    must(moo2_v131_derived_remove_building_first_write(
        colonies,3,-1,9)==MOO2_V131_BUILDING_FIRST_WRITE_INVALID);
    must(moo2_v131_derived_remove_building_first_write(
        colonies,3,3,9)==MOO2_V131_BUILDING_FIRST_WRITE_INVALID);
    must(moo2_v131_derived_remove_building_first_write(
        colonies,3,0,-1)==MOO2_V131_BUILDING_FIRST_WRITE_INVALID);
    must(moo2_v131_derived_remove_building_first_write(
        colonies,3,0,49)==MOO2_V131_BUILDING_FIRST_WRITE_INVALID);
    must(moo2_v131_derived_remove_building_first_write(
        NULL,3,0,9)==MOO2_V131_BUILDING_FIRST_WRITE_INVALID);
    must(memcmp(before,colonies,sizeof(colonies))==0);
    puts("PASS 3 colony IDs x 49 building slots x 256 source bytes, original clear-only mutation");
    return 0;
}
