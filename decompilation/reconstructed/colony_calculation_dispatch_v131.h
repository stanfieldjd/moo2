#ifndef MOO2_V131_COLONY_CALCULATION_H
#define MOO2_V131_COLONY_CALCULATION_H
#include <stddef.h>
#include <stdint.h>
typedef int (*Moo2V131PreImportCall)(void *opaque,uint8_t *colony);
typedef int (*Moo2V131PassOutImportsCall)(void *opaque,
                                          int8_t colony_owner,
                                          uint8_t *colony);
typedef int (*Moo2V131UpdatePlayerStatsCall)(void *opaque,uint8_t *player);
typedef struct {
    uint8_t *colonies;
    size_t colony_count;
    uint8_t *players;
    size_t player_count;
    Moo2V131PreImportCall pre_import;
    Moo2V131PassOutImportsCall pass_out_imports;
    Moo2V131UpdatePlayerStatsCall update_player_stats;
    void *opaque;
} Moo2V131ColonyCalculationContext;
typedef enum {
    MOO2_V131_COLONYCALC_OK=0,
    MOO2_V131_COLONYCALC_INVALID=1,
    MOO2_V131_COLONYCALC_CALLEE_FAILED=2
} Moo2V131ColonyCalculationStatus;
Moo2V131ColonyCalculationStatus moo2_v131_derived_colony_calculation(
    const Moo2V131ColonyCalculationContext *ctx,
    int16_t colony_index);
#endif
