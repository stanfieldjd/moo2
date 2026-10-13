/* Original-source-derived v1.31 building ID 9 branch regression.
 * Verifies first byte-clear occurs before Assign_New_Home_Planet_
 * callback with sign-extended colony owner BYTE for all 256 values.
 * Original home-planet helper side effects remain unimplemented.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/remove_building9_v131.c"

typedef struct {
    uint8_t *record;
    int32_t expected_owner;
    unsigned calls;
} TestHome;
static void must(int p) {
    if(!p){fputs("FAIL v1.31 Remove_Building_(9)\\n",stderr);exit(1);}
}
static void assign_home(void *opaque,int32_t owner) {
    TestHome *state=(TestHome *)opaque;
    must(state->record[0x13Fu]==0u);
    must(owner==state->expected_owner);
    state->calls++;
}
int main(void) {
    uint8_t colonies[3u*0x169u]={0};
    unsigned checked=0;
    for(int id=0;id<3;id++) {
        uint8_t *rec=colonies+(size_t)id*0x169u;
        for(unsigned owner_byte=0;owner_byte<256u;owner_byte++) {
            memset(colonies,0xA5u,sizeof(colonies));
            rec[0]=(uint8_t)owner_byte;
            rec[0x13Fu]=0xFFu;
            TestHome home={rec,owner_byte<128u?
                (int32_t)owner_byte:(int32_t)owner_byte-256,0u};
            must(moo2_v131_derived_remove_building9(
                colonies,3,(int16_t)id,assign_home,&home)
                ==MOO2_V131_REMOVE_BUILDING9_OK);
            must(home.calls==1u);
            must(rec[0x13Fu]==0u);
            /* No other original-format bytes changed in this bounded C. */
            for(size_t index=0;index<sizeof(colonies);index++) {
                if(&colonies[index]==rec+0x13Fu) {
                    must(colonies[index]==0u);
                } else if(&colonies[index]==rec) {
                    must(colonies[index]==(uint8_t)owner_byte);
                } else {
                    must(colonies[index]==0xA5u);
                }
            }
            checked++;
        }
    }
    memset(colonies,0xAAu,sizeof(colonies));
    uint8_t prior[sizeof(colonies)];
    memcpy(prior,colonies,sizeof(colonies));
    TestHome home={colonies,0,0};
    must(moo2_v131_derived_remove_building9(
        colonies,3,-1,assign_home,&home)==MOO2_V131_REMOVE_BUILDING9_INVALID);
    must(moo2_v131_derived_remove_building9(
        colonies,3,3,assign_home,&home)==MOO2_V131_REMOVE_BUILDING9_INVALID);
    must(moo2_v131_derived_remove_building9(
        colonies,3,0,NULL,&home)==MOO2_V131_REMOVE_BUILDING9_INVALID);
    must(moo2_v131_derived_remove_building9(
        NULL,3,0,assign_home,&home)==MOO2_V131_REMOVE_BUILDING9_INVALID);
    must(!memcmp(colonies,prior,sizeof(colonies)) && home.calls==0u);
    printf("PASS: %u original-owner/colony cases, flag clears before signed-owner assignment callback\\n",checked);
    return 0;
}
