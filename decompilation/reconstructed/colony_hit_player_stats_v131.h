#ifndef MOO2_V131_HIT_OWNER_STATS_H
#define MOO2_V131_HIT_OWNER_STATS_H
#include <stddef.h>
#include <stdint.h>
typedef enum {
    MOO2_V131_OWNER_STAT_OK=0,
    MOO2_V131_OWNER_STAT_INVALID=1
} Moo2V131OwnerStatStatus;
typedef enum {
    MOO2_V131_OWNER_STAT_INCREMENT_ONE=1,
    MOO2_V131_OWNER_STAT_INCREMENT_TEN=10
} Moo2V131OwnerStatDelta;
Moo2V131OwnerStatStatus moo2_v131_derived_colony_hit_owner_stat(
    uint8_t *players,size_t player_buffer_bytes,
    const uint8_t *colony,size_t colony_buffer_bytes,
    const uint8_t *event,size_t event_buffer_bytes,
    Moo2V131OwnerStatDelta original_branch_increment);
#endif
