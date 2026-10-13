/*
 * Derived v1.31 original building queue branches:
 * IDs 8,40,41: 7 queue slots, referenced ship status BYTE+0x10>=2,
 * repeated same slot on deletion, then star recomputation.
 * ID22: ship BYTE+0x11==2, no star recomputation.
 * Queue deletion test stub shifts original WORDs one slot left,
 * not claimed to implement original Delete_From_Colony_Queue_.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/remove_building_first_write_v131.c"
#include "../decompilation/reconstructed/remove_building_queue_cleanup_v131.c"

static void require(int p){if(!p){fputs("FAIL original Remove_Building_ queue filtering\n",stderr);exit(1);}}
static void put16(uint8_t *p,int16_t v) {
    uint16_t bits=(uint16_t)v;
    p[0]=(uint8_t)bits;p[1]=(uint8_t)(bits>>8);
}
typedef struct {
    uint8_t *colony;
    uint8_t *star_record;
    int building;
    unsigned deletion_calls;
    unsigned recompute_calls;
    unsigned positions[16];
    int fail_callback;
} Fixture;
static int erase(void *opaque,int16_t colony_id,int16_t slot) {
    Fixture *f=(Fixture*)opaque;
    require(colony_id==1 && slot>=0 && slot<7);
    require(f->colony[0x136u+(unsigned)f->building]==0u);
    if(f->fail_callback)return 0;
    require(f->deletion_calls<16u);
    f->positions[f->deletion_calls++]=(unsigned)slot;
    for(unsigned i=(unsigned)slot;i<6u;i++) {
        f->colony[0x115u+2u*i]=f->colony[0x115u+2u*(i+1u)];
        f->colony[0x116u+2u*i]=f->colony[0x116u+2u*(i+1u)];
    }
    put16(f->colony+0x115u+12u,-1);
    return 1;
}
static void recalc(void *opaque,uint8_t *star_record) {
    Fixture *f=(Fixture*)opaque;
    require(star_record==f->star_record);
    require(f->deletion_calls==3u);
    f->recompute_calls++;
}
static void init_queue(uint8_t *colony) {
    const int16_t original[7]={-100,-101,-102,-103,2,-1,-1};
    for(unsigned i=0;i<7u;i++)put16(colony+0x115u+2u*i,original[i]);
}
int main(void) {
    uint8_t colonies[2u*0x169u]={0};
    uint8_t ships[4u*0x81u]={0};
    uint8_t planets[2u*0x11u]={0};
    uint8_t stars[256u*0x71u]={0};
    uint8_t *colony=colonies+0x169u;
    Fixture fixture={0};
    fixture.colony=colony;
    Moo2V131QueueBuildingContext ctx={
        colonies,2u,ships,4u,planets,2u,stars,256u,
        erase,recalc,&fixture,16u
    };
    /* Ship flag identities derive from original two distinct checks. */
    ships[0u*0x81u+0x10u]=2u;ships[0u*0x81u+0x11u]=2u;
    ships[1u*0x81u+0x10u]=1u;ships[1u*0x81u+0x11u]=2u;
    ships[2u*0x81u+0x10u]=3u;ships[2u*0x81u+0x11u]=1u;
    ships[3u*0x81u+0x10u]=2u;ships[3u*0x81u+0x11u]=2u;
    put16(colony+2u,1);
    size_t removed=999u;
    for(unsigned variant=0;variant<4u;variant++) {
        int16_t building=(int16_t)(variant==0?8:variant==1?22:variant==2?40:41);
        fixture.building=building;
        for(unsigned star_index=0;star_index<(building==22?1u:256u);star_index++) {
            init_queue(colony);
            colony[0x136u+(unsigned)building]=0xB5u;
            planets[0x11u+2u]=(uint8_t)star_index;
            fixture.star_record=stars+(size_t)star_index*0x71u;
            fixture.deletion_calls=fixture.recompute_calls=0u;
            fixture.fail_callback=0;
            require(moo2_v131_derived_remove_building_queue(
                &ctx,1,building,&removed)==MOO2_V131_QUEUE_BUILDING_OK);
            require(removed==3u && fixture.deletion_calls==3u);
            require(fixture.recompute_calls==(unsigned)(building!=22));
            require(colony[0x136u+(unsigned)building]==0u);
            if(building==22) {
                require(moo2_v131_queue_read_signed_word(colony+0x115u)==-102);
                require(fixture.positions[0]==0 && fixture.positions[1]==0 &&
                        fixture.positions[2]==1);
            } else {
                require(moo2_v131_queue_read_signed_word(colony+0x115u)==-101);
                require(fixture.positions[0]==0 && fixture.positions[1]==1 &&
                        fixture.positions[2]==1);
            }
            require(moo2_v131_queue_read_signed_word(colony+0x117u)==2);
        }
    }
    fixture.building=8;
    init_queue(colony);
    colony[0x136u+8u]=0xDDu;
    fixture.deletion_calls=fixture.recompute_calls=0u;
    ctx.max_deletions=1u;
    require(moo2_v131_derived_remove_building_queue(
        &ctx,1,8,&removed)==MOO2_V131_QUEUE_BUILDING_ITERATION_LIMIT);
    require(removed==1u && fixture.deletion_calls==1u);
    ctx.max_deletions=16u;
    init_queue(colony);
    fixture.fail_callback=1;
    require(moo2_v131_derived_remove_building_queue(
        &ctx,1,8,&removed)==MOO2_V131_QUEUE_BUILDING_CALLBACK_FAILED);
    fixture.fail_callback=0;
    for(int bad=0;bad<3;bad++) {
        colony[0x136u+8u]=0xE3u;
        require(moo2_v131_derived_remove_building_queue(
            &ctx,1,(int16_t)(bad==0?3:bad==1?9:45),&removed)
            ==MOO2_V131_QUEUE_BUILDING_UNSUPPORTED_ID);
        require(colony[0x136u+8u]==0xE3u);
    }
    ctx.delete_queue=NULL;
    require(moo2_v131_derived_remove_building_queue(
        &ctx,1,22,&removed)==MOO2_V131_QUEUE_BUILDING_INVALID);
    puts("PASS: original IDs 8/22/40/41 queue source filters, slot revisit, 769 parent-star paths and safety limits");
    return 0;
}
