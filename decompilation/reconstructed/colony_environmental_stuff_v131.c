/*
 * Original Watcom v1.31 Colony_Environmental_Stuff_ 108 bytes
 * SOURCE DERIVED, not original MicroProse code.
 * ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Original CODE 0xD1CED..0xD1D58, 108 bytes.
 * Full original body SHA256:
 * 94c8b7df7075f34a74650d3dc72ff466c6d9e69d57afaaa2502679d16131a086
 *
 * Reads signed planet index colony WORD+0x02, original planet
 * record stride 17 and BYTE+0x08. Copies byte to colony+0xE2.
 * If that byte exactly 1, then either colony building BYTE+0x14D
 * or +0x14E being nonzero changes colony+0xE2 to 2.
 * The source path checking colony+0x152 includes CMP AL,AL;
 * its JNE can never be taken on real 32-bit x86. The byte+0x152
 * therefore has no effect in this observed function.
 *
 * Calls original Colony_Food2_Per_Farmer_ at 0xCE03E with
 * EAX=colony*, EDX=signed colony owner BYTE, EBX=0;
 * if low16 result==0 writes colony+0xE0=0, otherwise =255.
 *
 * Full function is reconstructed apart from actual food production
 * source logic, which is an explicitly typed callback.
 * Bounds checking is a host-only safety difference.
 */
#include <stddef.h>
#include <stdint.h>
#include "colony_environmental_stuff_v131.h"

Moo2V131ColonyEnvironmentResult moo2_v131_derived_colony_environmental(
    const Moo2V131ColonyEnvironmentContext *ctx,
    uint8_t *colony,size_t colony_bytes)
{
    if(!ctx || !ctx->planets || !ctx->food_per_farmer ||
       !colony || colony_bytes<0x169u)
        return MOO2_V131_COLONY_ENV_INVALID;

    uint16_t planet_bits=(uint16_t)(colony[2]|
                                    ((uint16_t)colony[3]<<8));
    int32_t planet_id=planet_bits<32768u ?
        (int32_t)planet_bits:(int32_t)planet_bits-65536;
    if(planet_id<0 || (size_t)planet_id>=ctx->planet_count)
        return MOO2_V131_COLONY_ENV_INVALID;

    const uint8_t *planet=ctx->planets+(size_t)planet_id*0x11u;
    uint8_t environmental=planet[0x08u];
    colony[0xE2u]=environmental;
    if(environmental==1u) {
        if(colony[0x14Du]!=0u || colony[0x14Eu]!=0u)
            colony[0xE2u]=2u;
    }
    int32_t owner=colony[0]<128u?(int32_t)colony[0] :
                  (int32_t)colony[0]-256;
    int16_t produced=ctx->food_per_farmer(ctx->opaque,colony,owner,0);
    colony[0xE0u]=(uint8_t)(produced==0 ? 0u:255u);
    return MOO2_V131_COLONY_ENV_OK;
}
