#ifndef MOO2_V131_REMOVE_BUILDING_FIRST_WRITE_H
#define MOO2_V131_REMOVE_BUILDING_FIRST_WRITE_H
#include <stddef.h>
#include <stdint.h>
typedef enum {
    MOO2_V131_BUILDING_FIRST_WRITE_OK=0,
    MOO2_V131_BUILDING_FIRST_WRITE_INVALID=1
} Moo2V131BuildingFirstWriteStatus;
Moo2V131BuildingFirstWriteStatus
moo2_v131_derived_remove_building_first_write(
    uint8_t *colonies,size_t colony_count,int16_t colony_id,int16_t building_id);
#endif
