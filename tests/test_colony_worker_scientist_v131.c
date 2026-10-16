/* Source-derived original 178-byte worker + 177-byte scientist
 * exhaustive arithmetic/breakdown regression against independent
 * table and source flag expectations. Not DOS runtime differential.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/colony_worker_scientist_v131.c"
static void must(int yes) {
    if(!yes){fputs("FAIL original worker/scientist productivity\n",stderr);exit(1);}
}
static void put16(uint8_t *p,unsigned n){
    p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);
}
static uint32_t read32(const uint8_t *p){
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
       ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static const unsigned mineral_base[5]={1,2,3,5,8};
int main(void) {
    uint8_t colony[0x169u]={0},planets[2u*0x11u]={0};
    uint8_t players[8u*0xEA9u]={0},stats[0x22Au];
    Moo2V131WorkerScientistContext ctx={planets,2u,players,8u};
    put16(colony+2u,1u);
    unsigned worker_cases=0,science_cases=0;
    for(unsigned type=0;type<5;type++)
      for(unsigned flags=0;flags<32;flags++)
      for(unsigned owner=0;owner<8;owner++)
      for(unsigned with_stats=0;with_stats<2;with_stats++){
        memset(colony,0,sizeof(colony));
        put16(colony+2u,1);
        colony[0x13Au]=(uint8_t)(flags&1u);
        colony[0x13Du]=(uint8_t)(flags&2u);
        colony[0x15Au]=(uint8_t)(flags&4u);
        colony[0x142u]=(uint8_t)(flags&8u);
        players[(size_t)owner*0xEA9u+0x183u]=
            (uint8_t)((flags&16u)?3u:0u);
        planets[0x11u+0x0Au]=(uint8_t)type;
        memset(stats,0xA5,sizeof(stats));
        uint32_t actual=0u;
        must(moo2_v131_derived_industry_per_worker(
             &ctx,colony,sizeof(colony),(int16_t)owner,
             with_stats?stats:NULL,with_stats?sizeof(stats):0u,
             &actual)==MOO2_V131_WORKER_SCIENTIST_OK);
        const uint32_t want=(uint32_t)(mineral_base[type]+
               ((flags&1u)?1u:0u)+((flags&2u)?1u:0u)+
               ((flags&4u)?2u:0u)+((flags&8u)?3u:0u)+
               ((flags&16u)?1u:0u));
        must(actual==want);
        if(with_stats){
          must(read32(stats)==mineral_base[type]);
          const struct {unsigned bit;size_t at;unsigned amount;} b[]={
            {1,0x1c8u,1},{2,0x1ceu,1},{4,0x208u,2},
            {8,0x1d8u,3},{16,0xf0u,1}
          };
          uint8_t expected[sizeof(stats)];memset(expected,0xA5,sizeof(expected));
          expected[0]=(uint8_t)mineral_base[type];
          expected[1]=expected[2]=expected[3]=0;
          for(unsigned j=0;j<5;j++)if(flags&b[j].bit)
             put16(expected+b[j].at,b[j].amount);
          must(memcmp(stats,expected,sizeof(stats))==0);
        }else{
          for(size_t i=0;i<sizeof(stats);i++)
            must(stats[i]==0xa5u);
        }
        worker_cases++;
      }

    for(unsigned flags=0;flags<16;flags++)
      for(unsigned special=0;special<16;special++)
      for(unsigned with_stats=0;with_stats<2;with_stats++){
        memset(colony,0,sizeof(colony));
        put16(colony+2u,1);
        colony[0x13Au]=(uint8_t)(flags&1u);
        colony[0x154u]=(uint8_t)(flags&2u);
        colony[0x149u]=(uint8_t)(flags&4u);
        colony[0x159u]=(uint8_t)(flags&8u);
        planets[0x11u+0x0Fu]=(uint8_t)special;
        memset(stats,0,sizeof(stats));
        uint32_t actual=0u;
        must(moo2_v131_derived_research_per_scientist(
            &ctx,colony,sizeof(colony),with_stats?stats:NULL,
            with_stats?sizeof(stats):0u,&actual)
            ==MOO2_V131_WORKER_SCIENTIST_OK);
        unsigned extra=special==10?2u:special==11?5u:0u;
        unsigned want=3u+((flags&1u)?1u:0u)+((flags&2u)?2u:0u)+
           ((flags&4u)?3u:0u)+((flags&8u)?1u:0u)+extra;
        must(actual==want);
        if(with_stats){
          uint8_t expected[sizeof(stats)]={0};
          expected[0]=3u;
          if(flags&1u)put16(expected+0x1c8u,1);
          if(flags&2u)put16(expected+0x1fcu,2);
          if(flags&4u)put16(expected+0x1e6u,3);
          if(flags&8u)put16(expected+0x206u,1);
          if(extra)expected[0x226u]=(uint8_t)extra;
          must(memcmp(stats,expected,sizeof(stats))==0);
        }else for(size_t j=0;j<sizeof(stats);j++)
            must(stats[j]==0u);
        science_cases++;
      }
    /* Original worker MOVZX DX preserves upper EDX when signed
       planet ID creates a 17*planet index exceeding 65535. */
    static uint8_t large_planets[4001u*0x11u];
    ctx.planets=large_planets;ctx.planet_count=4001;
    memset(colony,0,sizeof(colony));put16(colony+2u,4000);
    players[0x183u]=0u; /* Reset owner0's earlier technology fixture. */
    large_planets[4000u*0x11u+0x0au]=4u;
    uint32_t actual=0;
    must(moo2_v131_derived_industry_per_worker(
         &ctx,colony,sizeof(colony),0,NULL,0,&actual)
        ==MOO2_V131_WORKER_SCIENTIST_OK);
    must(actual==UINT32_C(0x10008));
    /* Out of range mineral table (only 5 source values) rejected. */
    ctx.planets=planets;ctx.planet_count=2;
    put16(colony+2u,1);
    planets[0x11u+0x0Au]=7u;
    must(moo2_v131_derived_industry_per_worker(
        &ctx,colony,sizeof(colony),0,NULL,0,&actual)
        ==MOO2_V131_WORKER_SCIENTIST_INVALID);
    printf("PASS: %u source worker and %u source research cases incl original breakdown and EDX high16\n",
           worker_cases,science_cases);
}
