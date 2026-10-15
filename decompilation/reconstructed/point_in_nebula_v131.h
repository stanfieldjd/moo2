#ifndef MOO2_V131_POINT_NEBULA_H
#define MOO2_V131_POINT_NEBULA_H
#include <stddef.h>
#include <stdint.h>
typedef struct {
    const uint8_t *data;
    size_t size;
} Moo2V131NebulaBitmap;
typedef struct {
    const uint8_t *nebula_records;
    size_t nebula_count;
    const Moo2V131NebulaBitmap *images;
} Moo2V131NebulaContext;
typedef enum {
    MOO2_V131_NEBULA_OK=0,
    MOO2_V131_NEBULA_INVALID=1
} Moo2V131NebulaStatus;
Moo2V131NebulaStatus moo2_v131_derived_point_in_one_nebula(
    const Moo2V131NebulaContext *ctx,size_t index,
    int32_t x,int32_t y,uint8_t *hit);
Moo2V131NebulaStatus moo2_v131_derived_point_in_some_nebula(
    const Moo2V131NebulaContext *ctx,int32_t x,int32_t y,uint8_t *hit);
#endif
