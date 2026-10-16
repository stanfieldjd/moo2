#ifndef MOO2_V131_COLONY_ENVIRONMENTAL_H
#define MOO2_V131_COLONY_ENVIRONMENTAL_H
#include <stddef.h>
#include <stdint.h>
typedef int16_t (*Moo2V131FoodPerFarmer)(
    void *opaque,uint8_t *colony,
    int32_t signed_owner,int32_t original_ebx_zero);
typedef struct {
    const uint8_t *planets;
    size_t planet_count;
    Moo2V131FoodPerFarmer food_per_farmer;
    void *opaque;
} Moo2V131ColonyEnvironmentContext;
typedef enum {
    MOO2_V131_COLONY_ENV_OK=0,
    MOO2_V131_COLONY_ENV_INVALID=1
} Moo2V131ColonyEnvironmentResult;
Moo2V131ColonyEnvironmentResult moo2_v131_derived_colony_environmental(
    const Moo2V131ColonyEnvironmentContext *ctx,
    uint8_t *colony,size_t colony_bytes);
#endif
