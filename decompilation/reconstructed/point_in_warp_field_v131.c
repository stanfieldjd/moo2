/*
 * Source-derived full original MOO2 v1.31
 * Point_Is_In_Warp_Field_Interdictor_Of_Star_ (73 CODE bytes).
 *
 * Original function CODE offset 0xDBAC3, full function SHA256:
 * c9c753a493dd59543b8929aadcc4ea4e02bdfad1ca32c227074b91a22dbfb305
 * Original ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Original inputs: EAX X, EDX Y, EBX owner bit, ECX star pointer.
 * The original code masks a one-byte star owner bitmap (+0x39) with
 *   (uint8_t)~(1u << (owner_bit & 31))
 * and returns 1 when any other set owner bit remains and the signed
 * squared distance to the star's signed WORD coords (+0x0f,+0x11)
 * is <=8100 (0x1fa4).
 *
 * For source-consistent actual in-game owner indices 0..7 this
 * implements exactly that 8-bit bitmask. Out-of-range owner bits
 * produce a zero shifted DL and hence an all-ones inverted mask;
 * host API accepts only 0..7 to avoid ambiguous malformed owners.
 */
#include <stddef.h>
#include <stdint.h>

typedef enum {
    MOO2_V131_WARP_OK=0,
    MOO2_V131_WARP_INVALID=1
} Moo2V131WarpStatus;

Moo2V131WarpStatus moo2_v131_derived_is_in_warp_field(
    const uint8_t *star,size_t star_size,
    int32_t x,int32_t y,uint8_t excluded_owner,
    uint8_t *result)
{
    if(!star || star_size<0x71u || !result || excluded_owner>=8u)
        return MOO2_V131_WARP_INVALID;
    uint8_t bitmap=star[0x39u];
    uint8_t own_bit=(uint8_t)(1u<<excluded_owner);
    if((uint8_t)(bitmap & (uint8_t)~own_bit)==0u) {
        *result=0u;
        return MOO2_V131_WARP_OK;
    }
    /* Source sign-extends low WORDs of input coordinates (SI, DI),
       then subtracts star WORDs and squares in signed 32-bit EAX/EDX.
       Guarding full ranges is a host-only safety decision. */
    int32_t sx=(int32_t)(uint16_t)((uint16_t)star[0x0fu]|
                       ((uint16_t)star[0x10u]<<8));
    int32_t sy=(int32_t)(uint16_t)((uint16_t)star[0x11u]|
                       ((uint16_t)star[0x12u]<<8));
    if(sx>=32768)sx-=65536;
    if(sy>=32768)sy-=65536;
    int32_t xx=(int32_t)(uint16_t)x;
    int32_t yy=(int32_t)(uint16_t)y;
    if(xx>=32768)xx-=65536;
    if(yy>=32768)yy-=65536;
    int64_t dx=(int64_t)xx-sx;
    int64_t dy=(int64_t)yy-sy;
    /* The game uses 32-bit IMUL and signed JG; for bounded map
       coordinates the mathematical sum fits signed 32-bit. */
    uint32_t bits=(uint32_t)((uint64_t)(dx*dx)+(uint64_t)(dy*dy));
    int64_t signed_squared=bits<=INT32_MAX ?
        (int64_t)bits:(int64_t)bits-INT64_C(4294967296);
    *result=(uint8_t)(signed_squared<=8100);
    return MOO2_V131_WARP_OK;
}
