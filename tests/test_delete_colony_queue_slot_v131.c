/* Original v1.31 Delete_From_Colony_Queue_ with anonymous CODE 0xA20ED
 * queue shift; tests do not run DOS original. Source-only states:
 * signed <=-100 ship encoding, ship status+0x64=5, owner+0x65=-1,
 * seven queue slots with -10 placeholders removed from selected slot.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/delete_colony_queue_slot_v131.c"

static void must(int value) {
    if(!value){fputs("FAIL original queue deletion and compaction\n",stderr);exit(1);}
}
static void put16(uint8_t *p,int32_t v) {
    uint16_t b=(uint16_t)v;p[0]=(uint8_t)b;p[1]=(uint8_t)(b>>8);
}
static int32_t get16(const uint8_t *p) {
    uint16_t b=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return b<32768u?(int32_t)b:(int32_t)b-65536;
}
static void fill_queue(uint8_t *colony,const int32_t original[7]) {
    for(unsigned i=0;i<7u;i++)put16(colony+0x115u+2u*i,original[i]);
}
int main(void) {
    uint8_t colonies[3u*0x169u]={0};
    uint8_t ships[16u*0x81u]={0};
    for(int colony_id=0;colony_id<3;colony_id++)
      for(int index=0;index<7;index++)
      for(int ship_id=0;ship_id<16;ship_id++) {
        memset(colonies,0xA5,sizeof(colonies));
        memset(ships,0xB6,sizeof(ships));
        uint8_t *colony=colonies+(size_t)colony_id*0x169u;
        int32_t original[7]={13,14,15,16,17,18,19};
        original[index]=-100-ship_id;
        fill_queue(colony,original);
        must(moo2_v131_derived_delete_colony_queue_slot(
           colonies,3,ships,16,(int16_t)colony_id,(int16_t)index)
           ==MOO2_V131_QUEUE_DELETE_OK);
        for(int i=0;i<7;i++) {
            int expected=i<index?original[i]:(i==6?-1:original[i+1]);
            must(get16(colony+0x115u+2u*(unsigned)i)==expected);
        }
        uint8_t *ship=ships+(size_t)ship_id*0x81u;
        must(ship[0x64u]==5u && get16(ship+0x65u)==-1);
        for(int j=0;j<16;j++)if(j!=ship_id) {
            const uint8_t *other=ships+(size_t)j*0x81u;
            must(other[0x64u]==0xB6u && other[0x65u]==0xB6u);
        }
      }
    /* a21? If a shifted-in position is -10, source JEs back to
       compactor and removes -10 from that same original slot. */
    uint8_t *colony=colonies+0x169u;
    memset(colonies,0,sizeof(colonies));
    memset(ships,0,sizeof(ships));
    const int32_t gaps[7]={-100,-10,-10,-101,-1,-1,-1};
    fill_queue(colony,gaps);
    must(moo2_v131_derived_delete_colony_queue_slot(
        colonies,3,ships,16,1,0)==MOO2_V131_QUEUE_DELETE_OK);
    must(get16(colony+0x115u)==-101);
    must(get16(colony+0x117u)==-1);
    /* Clearing a non-ship queue slot changes queue but not ships. */
    const int32_t plain[7]={2,3,4,-1,-1,-1,-1};
    fill_queue(colony,plain);
    memset(ships,0xBD,sizeof(ships));
    must(moo2_v131_derived_delete_colony_queue_slot(
        colonies,3,ships,16,1,0)==MOO2_V131_QUEUE_DELETE_OK);
    must(get16(colony+0x115u)==3);
    for(size_t i=0;i<sizeof(ships);i++)must(ships[i]==0xBDu);

    /* Original source special -1 index reads out of bounds before its
       guard. Modern C intentionally rejects it instead. */
    uint8_t before[sizeof(colonies)];memcpy(before,colonies,sizeof(colonies));
    must(moo2_v131_derived_delete_colony_queue_slot(
        colonies,3,ships,16,1,-1)==MOO2_V131_QUEUE_DELETE_INVALID);
    must(moo2_v131_derived_delete_colony_queue_slot(
        colonies,3,ships,16,1,7)==MOO2_V131_QUEUE_DELETE_INVALID);
    must(!memcmp(before,colonies,sizeof(colonies)));
    fill_queue(colony,gaps);
    must(moo2_v131_derived_delete_colony_queue_slot(
        colonies,3,ships,0,1,0)==MOO2_V131_QUEUE_DELETE_INVALID);
    must(get16(colony+0x115u)==-100);
    puts("PASS original queue delete: 336 source ship/index/colony cases, sentinel -10 compaction, host guards");
    return 0;
}
