/*
 * Complete arithmetic reconstruction of original MOO2 v1.31 isqrt_.
 * Original executable SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Original Watcom CODE 0x124C92, 155 bytes,
 * original full-body SHA256:
 * 712fab862da65b98b408b6bcaf4da8352fdb00306b0e40dfeeae616211d6c1b8.
 *
 * Original input EAX as unsigned 32-bit integer. The numeric result
 * is floor(sqrt(value)); top 32-bit region (>=0xFFFE0001) saturates
 * to 65535, the largest unsigned-16 square root.
 *
 * Original starts with stack-probe call to support CODE 0x12F1E0,
 * then chooses original low/high search bounds [0,256] when
 * input<=65535, or [256,65535] otherwise. Midpoint floor
 * and unsigned comparisons choose the final greatest integer
 * whose unsigned 32-bit square is <= input. The DOS support stack
 * probe is unnecessary in this bounded portable C function.
 */
#include <stdint.h>

uint32_t moo2_v131_derived_isqrt(uint32_t source_value)
{
    if(source_value>=UINT32_C(0xFFFE0001))
        return UINT32_C(65535);
    uint32_t low=source_value<=UINT32_C(65535)?0u:256u;
    uint32_t high=source_value<=UINT32_C(65535)?256u:65535u;
    while(low+1u<high) {
        uint32_t middle=(low+high)/2u;
        uint32_t squared=middle*middle;
        if(squared<=source_value)
            low=middle;
        else
            high=middle;
    }
    return low;
}
