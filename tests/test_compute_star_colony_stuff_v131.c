/* Full original 311-byte Compute_Star_Colony_Stuff_ source-derived C tests.
 * Independent state reference is a bitmask rule table, with explicit
 * preservation checks; no original DOS executable dynamically run.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/compute_star_colony_stuff_v131.c"

static void must(int ok){if(!ok){fputs("FAIL original star colony flags\n",stderr);exit(1);}}
static void put16(uint8_t *p,int16_t value) {
    uint16_t v=(uint16_t)value;p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
static const uint8_t positions[8]={0x38,0x39,0x3b,0x3c,0x3d,0x3e,0x3f,0x40};
static int is_output(unsigned idx) {
    for(unsigned i=0;i<8;i++)if(positions[i]==idx)return 1;
    return 0;
}
static void check_single(unsigned owner,unsigned flagmask,unsigned techmask)
{
    uint8_t colony[0x169]={0};
    uint8_t planet[0x11]={0};
    uint8_t players[8u*0xEA9u]={0};
    uint8_t star[0x71]={0};
    memset(star,0xA5,sizeof(star));
    colony[0]=(uint8_t)owner;
    colony[0x136u+45u]=(flagmask&1u)?9u:0u;
    colony[0x136u+40u]=(flagmask&2u)?1u:0u;
    colony[0x136u+8u]=(flagmask&4u)?255u:0u;
    colony[0x136u+41u]=(flagmask&8u)?2u:0u;
    colony[0x136u+3u]=(flagmask&16u)?1u:0u;
    colony[0x136u+14u]=(flagmask&32u)?42u:0u;
    uint8_t *p=players+(size_t)owner*0xEA9u;
    p[0x1cbu]=(techmask&1u)?3u:2u;
    p[0x1c7u]=(techmask&2u)?3u:4u;
    p[0x17au]=(techmask&4u)?3u:1u;
    p[0x1c1u]=(techmask&8u)?3u:0u;
    /* fifth original planet slot points at planet 0, others -1. */
    for(unsigned i=0;i<5u;i++)put16(star+0x4au+2u*i,-1);
    put16(star+0x4au+8u,0);
    put16(planet,0);
    uint8_t untouched[sizeof(star)];memcpy(untouched,star,sizeof(star));
    Moo2V131StarColonyContext ctx={planet,1,colony,1,players,8};
    must(moo2_v131_derived_compute_star_colony_stuff(
        &ctx,star,sizeof(star))==MOO2_V131_STAR_COLONY_OK);
    unsigned mask=1u<<owner;
    int tech_build=(flagmask&(2u|4u|8u))!=0;
    const uint8_t expected[8]={
      (uint8_t)mask,
      (uint8_t)((flagmask&1u)?mask:0u),
      (uint8_t)((tech_build && (techmask&1u))?mask:0u),
      (uint8_t)((tech_build && (techmask&2u))?mask:0u),
      (uint8_t)((techmask&8u)?mask:0u),
      (uint8_t)((techmask&4u)?mask:0u),
      (uint8_t)((flagmask&16u)?mask:0u),
      (uint8_t)((flagmask&32u)?mask:0u)
    };
    for(unsigned i=0;i<8u;i++)must(star[positions[i]]==expected[i]);
    for(unsigned i=0;i<sizeof(star);i++)
       if(!is_output(i))must(star[i]==untouched[i]);
}
int main(void)
{
    for(unsigned owner=0;owner<8u;owner++)
      for(unsigned flags=0;flags<64u;flags++)
        for(unsigned tech=0;tech<16u;tech++)
          check_single(owner,flags,tech);
    uint8_t colonies[5u*0x169u]={0};
    uint8_t planets[5u*0x11u]={0};
    uint8_t players[8u*0xEA9u]={0};
    uint8_t star[0x71u]={0};
    Moo2V131StarColonyContext ctx={planets,5,colonies,5,players,8};
    /* All five original planet slots, two colonies same owner
       and some distinct owners: OR bits, not add or overwrite. */
    for(unsigned i=0;i<5u;i++) {
        put16(star+0x4au+2u*i,(int16_t)i);
        put16(planets+i*0x11u,(int16_t)i);
        colonies[i*0x169u]=(uint8_t)(i==4u?1u:i);
        colonies[i*0x169u+0x136u+45u]=1u;
        colonies[i*0x169u+0x136u+3u]=1u;
        colonies[i*0x169u+0x136u+14u]=1u;
    }
    players[1u*0xEA9u+0x17Au]=3u;
    players[3u*0xEA9u+0x1C1u]=3u;
    must(moo2_v131_derived_compute_star_colony_stuff(
        &ctx,star,sizeof(star))==MOO2_V131_STAR_COLONY_OK);
    must(star[0x38u]==0x0Fu && star[0x39u]==0x0Fu);
    must(star[0x3Fu]==0x0Fu && star[0x40u]==0x0Fu);
    must(star[0x3Eu]==0x02u && star[0x3Du]==0x08u);
    must(star[0x3Bu]==0u && star[0x3Cu]==0u);
    /* Replace one planet with no colony and another empty planet slot. */
    put16(planets+4u*0x11u,-1);
    put16(star+0x4au+2u*3u,-1);
    must(moo2_v131_derived_compute_star_colony_stuff(
        &ctx,star,sizeof(star))==MOO2_V131_STAR_COLONY_OK);
    must(star[0x38u]==0x07u);
    /* Invalid field must be detected BEFORE clearing any prior flags. */
    uint8_t saved[sizeof(star)];memcpy(saved,star,sizeof(saved));
    put16(star+0x4au,6);
    memcpy(saved,star,sizeof(saved));
    must(moo2_v131_derived_compute_star_colony_stuff(
        &ctx,star,sizeof(star))==MOO2_V131_STAR_COLONY_INVALID);
    must(!memcmp(star,saved,sizeof(star)));
    put16(star+0x4au,0);
    put16(planets,6);
    memcpy(saved,star,sizeof(saved));
    must(moo2_v131_derived_compute_star_colony_stuff(
        &ctx,star,sizeof(star))==MOO2_V131_STAR_COLONY_INVALID);
    must(!memcmp(star,saved,sizeof(star)));
    put16(planets,0);
    colonies[0]=255u;
    memcpy(saved,star,sizeof(saved));
    must(moo2_v131_derived_compute_star_colony_stuff(
        &ctx,star,sizeof(star))==MOO2_V131_STAR_COLONY_INVALID);
    must(!memcmp(star,saved,sizeof(star)));
    colonies[0]=0u;
    must(moo2_v131_derived_compute_star_colony_stuff(
        &ctx,star,0x70u)==MOO2_V131_STAR_COLONY_INVALID);
    puts("PASS: 8192 exhaustive owner/building/technology mask cases, 5-slot OR, uncolonized cases and atomic host errors");
    return 0;
}
