#ifndef MOO2_V131_POINT_WARP_H
#define MOO2_V131_POINT_WARP_H
#include <stddef.h>
#include <stdint.h>
typedef enum {
    MOO2_V131_WARP_OK=0,
    MOO2_V131_WARP_INVALID=1
} Moo2V131WarpStatus;
Moo2V131WarpStatus moo2_v131_derived_is_in_warp_field(
    const uint8_t *star,size_t star_size,
    int32_t x,int32_t y,uint8_t excluded_owner,
    uint8_t *result);
#endif
