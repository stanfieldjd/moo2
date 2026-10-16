#ifndef MOO2_V131_POPULATION_LIMITS_H
#define MOO2_V131_POPULATION_LIMITS_H
#include <stddef.h>
#include <stdint.h>
typedef enum {
    MOO2_V131_POPLIMIT_OK=0,
    MOO2_V131_POPLIMIT_INVALID=1,
    MOO2_V131_POPLIMIT_CALLBACK_FAILED=2
} Moo2V131PopLimitResult;
typedef int (*Moo2V131PopCap)(
    void *opaque,const uint8_t *colony,uint8_t type,int16_t *limit);
typedef int (*Moo2V131PopShuffle)(
    void *opaque,uint8_t *population,size_t n,size_t stride);
typedef int (*Moo2V131PopFood)(
    void *opaque,uint8_t *colony,int8_t signed_owner,int16_t *produced);
typedef struct {
    Moo2V131PopCap race_capacity;
    Moo2V131PopShuffle shuffle;
    Moo2V131PopFood food_per_farmer;
    void *opaque;
} Moo2V131PopLimitContext;
Moo2V131PopLimitResult moo2_v131_derived_enforce_population_limits(
    const Moo2V131PopLimitContext *ctx,uint8_t *colony,size_t colony_bytes);
#endif
