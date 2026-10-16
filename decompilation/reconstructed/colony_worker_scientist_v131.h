#ifndef MOO2_V131_COLONY_WORKER_SCIENTIST_H
#define MOO2_V131_COLONY_WORKER_SCIENTIST_H
#include <stddef.h>
#include <stdint.h>
typedef struct {
    const uint8_t *planets;
    size_t planet_count;
    const uint8_t *players;
    size_t player_count;
} Moo2V131WorkerScientistContext;
typedef enum {
    MOO2_V131_WORKER_SCIENTIST_OK=0,
    MOO2_V131_WORKER_SCIENTIST_INVALID=1
} Moo2V131WorkerScientistStatus;
Moo2V131WorkerScientistStatus
moo2_v131_derived_industry_per_worker(
    const Moo2V131WorkerScientistContext *ctx,
    const uint8_t *colony,size_t colony_bytes,int16_t owner,
    uint8_t *contributions,size_t contribution_bytes,uint32_t *result);
Moo2V131WorkerScientistStatus
moo2_v131_derived_research_per_scientist(
    const Moo2V131WorkerScientistContext *ctx,
    const uint8_t *colony,size_t colony_bytes,
    uint8_t *contributions,size_t contribution_bytes,uint32_t *result);
#endif
