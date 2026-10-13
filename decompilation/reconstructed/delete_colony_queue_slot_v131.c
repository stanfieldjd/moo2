/*
 * DERIVED original Watcom v1.31 Delete_From_Colony_Queue_
 * and an anonymous 99-byte colony-queue compaction routine. NOT original MicroProse C.
 *
 * Source executable SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Delete_From_Colony_Queue_ original CODE 0xA1E19..0xA1E76
 * is 94 source bytes, input AX colony index / DX queue index.
 * original at 0xA1E32 reads signed queue WORD+0x115+2*index.
 * if index == -1 returns (source performs read first).
 * if queue WORD <= -100, ship_id = -(word + 100), then
 * _ship[ship_id*0x81 +0x64] BYTE = 5;
 * _ship[ship_id*0x81 +0x65] WORD = 0xFFFF.
 * original CALL 0xA20ED at CODE 0xA1E6E (anonymous colony queue shift).
 *
 * Anonymous original CODE 0xA20ED..0xA214F (99 bytes):
 * queue[index..5] = queue[index+1..6]; queue[6] = -1.
 * If queue[index] == -10, repeat compaction from SAME slot,
 * skipping consecutive -10 entries (original JE 0xA20F2).
 *
 * Source-based host implementation requires in-range pointers/indices.
 * It does not emulate undefined original memory access for index -1.
 */
#include <stddef.h>
#include <stdint.h>

typedef enum {
    MOO2_V131_QUEUE_DELETE_OK=0,
    MOO2_V131_QUEUE_DELETE_INVALID=1
} Moo2V131QueueDeleteStatus;

static int32_t moo2_v131_delete_queue_s16(const uint8_t *p) {
    uint16_t bits=(uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
    return bits<UINT16_C(0x8000)?(int32_t)bits:(int32_t)bits-65536;
}
static void moo2_v131_delete_queue_w16(uint8_t *p,uint16_t val) {
    p[0]=(uint8_t)val;p[1]=(uint8_t)(val>>8);
}

Moo2V131QueueDeleteStatus moo2_v131_derived_delete_colony_queue_slot(
    uint8_t *colonies,size_t colony_count,
    uint8_t *ships,size_t ship_count,
    int16_t colony_id,int16_t original_slot)
{
    if(!colonies || !ships || colony_id<0 ||
       (size_t)colony_id>=colony_count || original_slot<0 ||
       original_slot>=7)
        return MOO2_V131_QUEUE_DELETE_INVALID;
    uint8_t *colony=colonies+(size_t)colony_id*0x169u;
    uint8_t *slot=colony+0x115u+2u*(size_t)original_slot;
    int32_t value=moo2_v131_delete_queue_s16(slot);
    if(value<=-100) {
        int32_t ship_index=-(value+100);
        if(ship_index<0 || (size_t)ship_index>=ship_count)
            return MOO2_V131_QUEUE_DELETE_INVALID;
        uint8_t *ship=ships+(size_t)ship_index*0x81u;
        ship[0x64u]=5u;
        moo2_v131_delete_queue_w16(ship+0x65u,UINT16_MAX);
    }
    /* Source anonymous 0xA20ED routine: skip -10 placeholders if they become
       the queue value at the removed position. At most 7-index passes
       can be needed for original seven queue WORDs. */
    for(;;) {
        for(unsigned index=(unsigned)original_slot;index<6u;index++) {
            uint8_t *dst=colony+0x115u+2u*index;
            const uint8_t *src=dst+2u;
            dst[0]=src[0];dst[1]=src[1];
        }
        moo2_v131_delete_queue_w16(colony+0x121u,UINT16_MAX);
        if(moo2_v131_delete_queue_s16(
              colony+0x115u+2u*(unsigned)original_slot)!=-10)
            break;
    }
    return MOO2_V131_QUEUE_DELETE_OK;
}
