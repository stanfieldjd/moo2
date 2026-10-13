/*
 * DERIVED ORIGINAL MOO2 v1.31 Does_Combat_Planet_Have_Defenses_.
 * Entire original routine CODE 0x2A142..0x2A19D, 92 bytes.
 * Not original MicroProse source, not the full combat system.
 *
 * Original DATA globals:
 *   _cmbt_colony_id at object2 +0x21878 (signed WORD)
 *   _colony at object2 +0x1AB18 (pointer to colony records)
 *
 * Original colony record stride 0x169 (361).
 * Read colony record bytes +0x150,+0x151,+0x160,+0x165.
 * Result EAX = b150 | (b151 << 1) | (b160 << 2) | (b165 << 3).
 * Original -1 colony ID returns zero.
 *
 * The source uses OR, not ADD; bytes are not assumed boolean.
 * Introduced host checks avoid original out-of-bounds accesses.
 */
#include <stddef.h>
#include <stdint.h>

typedef enum {
    MOO2_V131_COLONY_DEFENSE_OK=0,
    MOO2_V131_COLONY_DEFENSE_INVALID_INPUT=1
} Moo2V131ColonyDefenseStatus;

Moo2V131ColonyDefenseStatus
moo2_v131_derived_combat_planet_defenses(
    const uint8_t *colony_records,size_t colony_record_count,
    int16_t combat_colony_id,uint32_t *packed_result)
{
    if(!packed_result) return MOO2_V131_COLONY_DEFENSE_INVALID_INPUT;
    if(combat_colony_id==(int16_t)-1) {
        *packed_result=0u;
        return MOO2_V131_COLONY_DEFENSE_OK;
    }
    if(!colony_records || combat_colony_id<0 ||
       (size_t)combat_colony_id>=colony_record_count)
        return MOO2_V131_COLONY_DEFENSE_INVALID_INPUT;

    const uint8_t *colony=colony_records+
                           (size_t)combat_colony_id*0x169u;
    *packed_result=(uint32_t)colony[0x150u]
                 | ((uint32_t)colony[0x151u]<<1)
                 | ((uint32_t)colony[0x160u]<<2)
                 | ((uint32_t)colony[0x165u]<<3);
    return MOO2_V131_COLONY_DEFENSE_OK;
}
