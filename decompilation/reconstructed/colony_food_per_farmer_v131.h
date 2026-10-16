#ifndef MOO2_V131_COLONY_FOOD_PER_FARMER_H
#define MOO2_V131_COLONY_FOOD_PER_FARMER_H
#include <stddef.h>
#include <stdint.h>
typedef enum {
    MOO2_V131_FOOD_OK=0,
    MOO2_V131_FOOD_INVALID=1
} Moo2V131FoodResult;
typedef struct {
    const uint8_t *planets;
    size_t planet_count;
    const uint8_t *players;
    size_t player_count;
} Moo2V131FoodContext;
/* Returns source EAX as uint32; caller may test low original WORD.
 * stats is optional EBX original pointer, 0x21e bytes if non-null. */
Moo2V131FoodResult moo2_v131_derived_colony_food_per_farmer(
    const Moo2V131FoodContext *ctx,
    const uint8_t *colony,size_t colony_bytes,
    int16_t source_owner,
    uint8_t *stats,size_t stats_bytes,
    uint32_t *source_eax_result);
#endif
