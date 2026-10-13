#ifndef MOO2_V131_ASSIGN_NEW_HOME_PLANET_H
#define MOO2_V131_ASSIGN_NEW_HOME_PLANET_H
#include <stddef.h>
#include <stdint.h>
typedef enum {
    MOO2_V131_ASSIGN_HOME_OK=0,
    MOO2_V131_ASSIGN_HOME_INVALID=1
} Moo2V131AssignHomeStatus;
/* Source-derived v1.31 whole 146-byte Assign_New_Home_Planet_.
 * owner EAX, colony-to-exclude EDX, _NUM_COLONIES signed WORD.
 * Select greatest colony+0x0A population, tie: smallest index.
 * Store star WORD (colony+2) in player+owner*0xEA9+0x29, else 0xFFFF.
 */
Moo2V131AssignHomeStatus moo2_v131_derived_assign_new_home_planet(
    const uint8_t *colonies,size_t colony_count,
    uint8_t *players,size_t player_bytes,
    int32_t owner_id,int32_t excluded_colony_id,
    uint16_t *star_word_written);
#endif
