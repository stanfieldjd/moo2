/*
 * Original v1.31 source-derived integration:
 * Remove_Building_(ID8/22/40/41) queue scan
 * -> Delete_From_Colony_Queue_ (94 bytes)
 * -> anonymous colony queue compaction (0xA20ED..0xA214F),
 * plus star recomputation callback for IDs 8/40/41.
 * No actual DOS execution or Compute_Star_Colony_Stuff_ effects.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/remove_building_queue_cleanup_v131.c"
#include "../decompilation/reconstructed/delete_colony_queue_slot_v131.c"

static void verify(int ok) {
    if(!ok){fputs("FAIL source linked queue deletion\n",stderr);exit(1);}
}
static void put16(uint8_t *p,int32_t x) {
    uint16_t bits=(uint16_t)x;p[0]=(uint8_t)bits;p[1]=(uint8_t)(bits>>8);
}
typedef struct {
    uint8_t *colonies,*ships,*star;
    int16_t original_building;
    unsigned removal_count;
    unsigned compute_count;
} Fixture;
static int delete_slot(void *opaque,int16_t colony_id,int16_t slot) {
    Fixture *f=(Fixture *)opaque;
    verify(f->colonies[0x169u+0x136u+(unsigned)f->original_building]==0u);
    verify(colony_id==1 && slot>=0 && slot<7);
    Moo2V131QueueDeleteStatus state=moo2_v131_derived_delete_colony_queue_slot(
        f->colonies,2,f->ships,4,colony_id,slot);
    if(state!=MOO2_V131_QUEUE_DELETE_OK)return 0;
    f->removal_count++;
    return 1;
}
static void compute(void *opaque,uint8_t *star) {
    Fixture *f=(Fixture *)opaque;
    verify(star==f->star);
    verify(f->removal_count==3u);
    f->compute_count++;
}
static void init(uint8_t *colony) {
    const int32_t words[7]={-100,-101,-102,-103,2,-1,-1};
    for(unsigned i=0;i<7u;i++)put16(colony+0x115u+2u*i,words[i]);
}
int main(void) {
    uint8_t colonies[2u*0x169u]={0},ships[4u*0x81u]={0};
    uint8_t planets[2u*0x11u]={0},stars[4u*0x71u]={0};
    uint8_t *colony=colonies+0x169u;
    Fixture f={colonies,ships,stars+3u*0x71u,0,0,0};
    Moo2V131QueueBuildingContext ctx={
        colonies,2,ships,4,planets,2,stars,4,
        delete_slot,compute,&f,16
    };
    put16(colony+2u,1);planets[0x11u+2u]=3u;
    ships[0u*0x81u+0x10u]=2u; ships[0u*0x81u+0x11u]=2u;
    ships[1u*0x81u+0x10u]=1u; ships[1u*0x81u+0x11u]=2u;
    ships[2u*0x81u+0x10u]=3u; ships[2u*0x81u+0x11u]=1u;
    ships[3u*0x81u+0x10u]=2u; ships[3u*0x81u+0x11u]=2u;
    const int building_ids[]={8,22,40,41};
    for(unsigned variant=0;variant<4;variant++) {
        int building=building_ids[variant];
        memset(ships+0x64,0,3); /* harmless; individual states below */
        for(unsigned i=0;i<4u;i++){
            ships[i*0x81u+0x64u]=0u;
            put16(ships+i*0x81u+0x65u,0u);
        }
        init(colony);
        colony[0x136u+(unsigned)building]=1u;
        f.original_building=(int16_t)building;
        f.removal_count=f.compute_count=0u;
        size_t deleted=999;
        verify(moo2_v131_derived_remove_building_queue(
            &ctx,1,(int16_t)building,&deleted)==MOO2_V131_QUEUE_BUILDING_OK);
        verify(deleted==3u && f.removal_count==3u);
        verify(f.compute_count==(unsigned)(building!=22));
        verify(colony[0x136u+(unsigned)building]==0u);
        const unsigned removed_ids[4][3]={
            {0,2,3},{0,1,3},{0,2,3},{0,2,3}
        };
        for(unsigned i=0;i<4u;i++) {
            int expected=0;
            for(unsigned j=0;j<3u;j++)if(removed_ids[variant][j]==i)expected=1;
            verify(ships[i*0x81u+0x64u]==(unsigned)(expected?5:0));
            int32_t owner=moo2_v131_delete_queue_s16(ships+i*0x81u+0x65u);
            verify(owner==(expected?-1:0));
        }
        const int32_t surviving=moo2_v131_delete_queue_s16(colony+0x115u);
        verify(surviving==(building==22?-102:-101));
        verify(moo2_v131_delete_queue_s16(colony+0x117u)==2);
    }
    puts("PASS original 4 building-ID queue paths integrated with full 94-byte deletion and anonymous queue compaction subset");
    return 0;
}
