#ifndef MOO2_V131_PRE_IMPORT_COMPUTING_H
#define MOO2_V131_PRE_IMPORT_COMPUTING_H
#include <stddef.h>
#include <stdint.h>
typedef enum {
    MOO2_V131_PRE_MORALE=0,
    MOO2_V131_PRE_INDUSTRY_MAINTENANCE=1,
    MOO2_V131_PRE_INDUSTRY_PRODUCTION=2,
    MOO2_V131_PRE_FOOD_PRODUCTION=3,
    MOO2_V131_PRE_FOOD_MAINTENANCE=4,
    MOO2_V131_PRE_REPLICATORS=5,
    MOO2_V131_PRE_RESEARCH_PRODUCTION=6,
    MOO2_V131_PRE_INDUSTRY_TO_TAX=7,
    MOO2_V131_PRE_BC_PRODUCTION=8,
    MOO2_V131_PRE_BC_MAINTENANCE=9
} Moo2V131PreImportStage;
typedef int (*Moo2V131PreImportDependency)(
    void *opaque,Moo2V131PreImportStage original_callee,
    uint8_t *colony);
typedef struct {
    const uint8_t *planets;
    size_t planet_count;
    const uint8_t *players;
    size_t player_count;
    Moo2V131PreImportDependency pending_callee;
    void *opaque;
} Moo2V131PreImportContext;
typedef enum {
    MOO2_V131_PREIMPORT_OK=0,
    MOO2_V131_PREIMPORT_INVALID=1,
    MOO2_V131_PREIMPORT_PENDING_CALLEE_FAILED=2
} Moo2V131PreImportStatus;
Moo2V131PreImportStatus moo2_v131_derived_pre_import_computing(
    const Moo2V131PreImportContext *ctx,
    uint8_t *colony,size_t colony_bytes);
#endif
