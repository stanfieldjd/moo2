/*
 * Complete source-derived nebula membership helpers from
 * Master of Orion II v1.31 Watcom LE CODE.
 *
 * 0xDB9C8..0xDBA39 (114 bytes) is an anonymous per-nebula point test.
 * 0xDBA3A..0xDBA7B (66 bytes) is named Point_Is_In_Some_Nebula_.
 * Original executable:
 * SHA256 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Body hashes:
 * 0xDB9C8: 4cc37fb9b315c032a08140ed6bb70828d18cbab39d92f13629297a5ffc7e34a8
 * 0xDBA3A: 78203712436446f44a76e139d6b3a899fda9595d48ad58a0d415441ba558f307
 *
 * Original _nebula DATA+0x1B068 pointer -> 5-byte records.
 * The per-nebula image pointer from
 * _nebula_pict_seg DATA+0x18298 + 16*index+12
 * points at a grid image: signed WORD width +0, height +2,
 * cell pixels start at +16. The source x/y are signed low
 * 16 bits and offset from signed nebula base WORDs+0/+2,
 * dividing both differences by 3 using truncation toward 0.
 * When 0<=cellX<width and 0<=cellY<height, source returns
 * (unsigned image[16+cellY*width+cellX] > 5).
 *
 * The wrapper visits nebulas 0.._NUM_NEBULAS-1 and returns true
 * on the first matched cell. Original NUM_NEBULAS is unsigned BYTE.
 * The DOS code has no host array/pointer guards; those here are
 * intentional. Original specific nebula imagery remains user-local.
 */
#include <stddef.h>
#include <stdint.h>

typedef struct {
    const uint8_t *data;
    size_t size;
} Moo2V131NebulaBitmap;
typedef struct {
    const uint8_t *nebula_records; /* count*5 bytes */
    size_t nebula_count;           /* original unsigned _NUM_NEBULAS */
    const Moo2V131NebulaBitmap *images; /* count image pointers */
} Moo2V131NebulaContext;
typedef enum {
    MOO2_V131_NEBULA_OK=0,
    MOO2_V131_NEBULA_INVALID=1
} Moo2V131NebulaStatus;

static int32_t moo2_v131_nebula_s16(const uint8_t *ptr) {
    uint16_t v=(uint16_t)(ptr[0]|((uint16_t)ptr[1]<<8));
    return v<32768u?(int32_t)v:(int32_t)v-65536;
}
static int32_t moo2_v131_nebula_coord(int32_t n) {
    uint16_t bits=(uint16_t)n;
    return bits<32768u?(int32_t)bits:(int32_t)bits-65536;
}
Moo2V131NebulaStatus moo2_v131_derived_point_in_one_nebula(
    const Moo2V131NebulaContext *ctx,size_t index,
    int32_t x,int32_t y,uint8_t *hit)
{
    if(!ctx || !hit || !ctx->nebula_records || !ctx->images ||
       ctx->nebula_count>255u || index>=ctx->nebula_count)
        return MOO2_V131_NEBULA_INVALID;
    const uint8_t *record=ctx->nebula_records+5u*index;
    const Moo2V131NebulaBitmap *bitmap=&ctx->images[index];
    if(!bitmap->data || bitmap->size<16u)
        return MOO2_V131_NEBULA_INVALID;
    const int32_t low_x=moo2_v131_nebula_s16(record);
    const int32_t low_y=moo2_v131_nebula_s16(record+2);
    const int32_t grid_x=(moo2_v131_nebula_coord(x)-low_x)/3;
    const int32_t grid_y=(moo2_v131_nebula_coord(y)-low_y)/3;
    if(grid_x<0 || grid_y<0) {
        *hit=0u;
        return MOO2_V131_NEBULA_OK;
    }
    int32_t width=moo2_v131_nebula_s16(bitmap->data);
    int32_t height=moo2_v131_nebula_s16(bitmap->data+2);
    if(width<0 || height<0)
        return MOO2_V131_NEBULA_INVALID;
    if(grid_x>=width || grid_y>=height) {
        *hit=0u;
        return MOO2_V131_NEBULA_OK;
    }
    const size_t offset=16u+(size_t)grid_y*(size_t)width+(size_t)grid_x;
    if(offset>=bitmap->size)
        return MOO2_V131_NEBULA_INVALID;
    *hit=(uint8_t)(bitmap->data[offset]>5u);
    return MOO2_V131_NEBULA_OK;
}
Moo2V131NebulaStatus moo2_v131_derived_point_in_some_nebula(
    const Moo2V131NebulaContext *ctx,
    int32_t x,int32_t y,uint8_t *hit)
{
    if(!ctx || !hit || ctx->nebula_count>255u ||
       (ctx->nebula_count && (!ctx->nebula_records || !ctx->images)))
        return MOO2_V131_NEBULA_INVALID;
    for(size_t i=0;i<ctx->nebula_count;i++) {
        uint8_t found=0u;
        Moo2V131NebulaStatus status=moo2_v131_derived_point_in_one_nebula(
            ctx,i,x,y,&found);
        if(status!=MOO2_V131_NEBULA_OK)
            return status;
        if(found) {
            *hit=1u;
            return MOO2_V131_NEBULA_OK;
        }
    }
    *hit=0u;
    return MOO2_V131_NEBULA_OK;
}
