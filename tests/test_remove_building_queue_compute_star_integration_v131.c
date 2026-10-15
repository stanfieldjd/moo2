/*
 * Full source-backed integration:
 * Remove_Building_ IDs8/40/41 queue scan ->
 * Delete_From_Colony_Queue_ ship-state and anonymous compactor ->
 * actual Compute_Star_Colony_Stuff_ 311-byte derived C.
 * Building22 deletes its queue entry without recalculating star fields.
 * Original DOS behavior not dynamically executed.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/remove_building_queue_cleanup_v131.c"
#include "../decompilation/reconstructed/delete_colony_queue_slot_v131.c"
#include "../decompilation/reconstructed/compute_star_colony_stuff_v131.c"

static void need(int yes){
    if(!yes){fputs("FAIL queue removal real star flag rebuild\n",stderr);exit(1);}
}
static void w16(uint8_t *p,int16_t v) {
    uint16_t n=(uint16_t)v;p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);
}
typedef struct {
    uint8_t *colony;
    uint8_t *colonies;
    uint8_t *ships;
    uint8_t *star;
    Moo2V131StarColonyContext calc;
    unsigned deletes;
    unsigned recalcs;
} Harness;
static int remove_queue(void *opaque,int16_t colony_id,int16_t slot) {
    Harness *h=(Harness*)opaque;
    need(colony_id==0 && slot==0);
    need(moo2_v131_derived_delete_colony_queue_slot(
        h->colonies,1,h->ships,1,colony_id,slot)
        ==MOO2_V131_QUEUE_DELETE_OK);
    h->deletes++;
    return 1;
}
static void recompute(void *opaque,uint8_t *star) {
    Harness *h=(Harness*)opaque;
    need(star==h->star);
    need(h->deletes==1u);
    need(moo2_v131_derived_compute_star_colony_stuff(
        &h->calc,star,0x71u)==MOO2_V131_STAR_COLONY_OK);
    h->recalcs++;
}
int main(void) {
    uint8_t colonies[0x169u]={0};
    uint8_t ships[0x81u]={0};
    uint8_t planets[0x11u]={0};
    uint8_t stars[0x71u]={0};
    uint8_t players[8u*0xEA9u]={0};
    w16(colonies+2u,0);
    w16(planets,0);
    for(unsigned i=0;i<5u;i++)w16(stars+0x4au+2u*i,-1);
    w16(stars+0x4au,0);
    Harness h={colonies,colonies,ships,stars,
        {planets,1,colonies,1,players,8},0,0};
    Moo2V131QueueBuildingContext ctx={
        colonies,1,ships,1,planets,1,stars,1,
        remove_queue,recompute,&h,7
    };
    for(unsigned owner=0;owner<8u;owner++) {
        memset(players,0,sizeof(players));
        colonies[0]=(uint8_t)owner;
        uint8_t *player=players+(size_t)owner*0xEA9u;
        player[0x1cbu]=3u;
        player[0x1c7u]=3u;
        colonies[0x136u+8u]=1u;
        colonies[0x136u+40u]=1u;
        colonies[0x136u+41u]=1u;
        colonies[0x136u+22u]=1u;
        ships[0x10u]=2u;
        ships[0x11u]=2u;
        uint8_t bit=(uint8_t)(1u<<owner);
        need(moo2_v131_derived_compute_star_colony_stuff(
            &h.calc,stars,sizeof(stars))==MOO2_V131_STAR_COLONY_OK);
        need(stars[0x38u]==bit && stars[0x3bu]==bit &&
             stars[0x3cu]==bit);

        const int building_ids[4]={8,40,41,22};
        for(unsigned j=0;j<4u;j++) {
            const int id=building_ids[j];
            h.deletes=h.recalcs=0u;
            w16(colonies+0x115u,-100);
            for(unsigned k=1;k<7u;k++)
                w16(colonies+0x115u+2u*k,-1);
            size_t deletion_count=99u;
            need(moo2_v131_derived_remove_building_queue(
                &ctx,0,(int16_t)id,&deletion_count)
                 ==MOO2_V131_QUEUE_BUILDING_OK);
            need(deletion_count==1u && h.deletes==1u);
            need(h.recalcs==(id==22?0u:1u));
            need(colonies[0x136u+(unsigned)id]==0u);
            need(moo2_v131_queue_read_signed_word(
                colonies+0x115u)==-1);
            need(ships[0x64u]==5u);
            need(moo2_v131_delete_queue_s16(ships+0x65u)==-1);
            need(stars[0x38u]==bit);
            const uint8_t expected_flags=id==41?0u:bit;
            need(stars[0x3bu]==expected_flags);
            need(stars[0x3cu]==expected_flags);
        }
    }
    puts("PASS: 8 owners x 4 queue-building deletions; real ship reset/compaction and source star flags");
    return 0;
}
