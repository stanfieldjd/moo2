#ifndef MOO2_V131_COMPUTE_STAR_COLONY_STUFF_H
#define MOO2_V131_COMPUTE_STAR_COLONY_STUFF_H
#include <stddef.h>
#include <stdint.h>
typedef enum {
    MOO2_V131_STAR_COLONY_OK=0,
    MOO2_V131_STAR_COLONY_INVALID=1
} Moo2V131StarColonyStatus;
typedef struct {
    const uint8_t *planets;
    size_t planet_count;
    const uint8_t *colonies;
    size_t colony_count;
    const uint8_t *players;
    size_t player_count;
} Moo2V131StarColonyContext;
Moo2V131StarColonyStatus moo2_v131_derived_compute_star_colony_stuff(
    const Moo2V131StarColonyContext *ctx,
    uint8_t *original_star_record,size_t star_record_bytes);
#endif
