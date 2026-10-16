#ifndef MOO2_V131_COLONY_RACE_POP_LIMIT_H
#define MOO2_V131_COLONY_RACE_POP_LIMIT_H
#include <stddef.h>
#include <stdint.h>
typedef int (*Moo2V131SizeClimateLimit)(
    void *opaque,uint8_t planet_size,uint8_t environment,
    int16_t race_index,int32_t *base_result);
typedef struct {
    const uint8_t *planets;
    size_t planet_count;
    const uint8_t *players;
    size_t player_count;
    Moo2V131SizeClimateLimit size_and_climate_limit;
    void *opaque;
} Moo2V131RaceLimitContext;
typedef enum {
    MOO2_V131_RACELIMIT_OK=0,
    MOO2_V131_RACELIMIT_INVALID=1,
    MOO2_V131_RACELIMIT_CALLBACK_FAILED=2
} Moo2V131RaceLimitStatus;
Moo2V131RaceLimitStatus moo2_v131_derived_colony_race_pop_limit(
    const Moo2V131RaceLimitContext *ctx,
    const uint8_t *colony,size_t colony_bytes,
    int16_t race_index,int32_t *result);
#endif
