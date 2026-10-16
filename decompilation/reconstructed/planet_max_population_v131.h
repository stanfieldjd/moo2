#ifndef MOO2_V131_PLANET_MAX_POPULATION_H
#define MOO2_V131_PLANET_MAX_POPULATION_H
#include <stddef.h>
#include <stdint.h>
typedef struct {
    const uint8_t *planets;
    size_t planet_count;
    const uint8_t *colonies;
    size_t colony_count;
    const uint8_t *players;
    size_t player_count;
} Moo2V131PlanetMaxPopulationContext;
typedef enum {
    MOO2_V131_PLANET_MAX_OK=0,
    MOO2_V131_PLANET_MAX_INVALID=1
} Moo2V131PlanetMaxPopulationStatus;
Moo2V131PlanetMaxPopulationStatus
moo2_v131_derived_planet_max_population_for_player(
    const Moo2V131PlanetMaxPopulationContext *ctx,
    size_t planet_id,int16_t player_id,int32_t *result);
#endif
