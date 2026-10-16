#ifndef MOO2_V131_SIZE_CLIMATE_POP_LIMIT_H
#define MOO2_V131_SIZE_CLIMATE_POP_LIMIT_H
#include <stdint.h>
#include <stddef.h>
typedef struct {
    const uint8_t *players;
    size_t player_count;
} Moo2V131SizeClimateContext;
typedef enum {
    MOO2_V131_SIZE_CLIMATE_OK=0,
    MOO2_V131_SIZE_CLIMATE_INVALID=1
} Moo2V131SizeClimateStatus;
Moo2V131SizeClimateStatus moo2_v131_derived_size_climate_max_population(
    uint8_t planet_size,uint8_t environment,
    uint8_t race_population_bonus,int32_t *result);
Moo2V131SizeClimateStatus moo2_v131_derived_size_climate_race_pop_limit(
    const Moo2V131SizeClimateContext *ctx,
    uint8_t planet_size,uint8_t environment,
    int16_t race_index,int32_t *result);
#endif
