#ifndef MOO2_V131_RANDOM_SHUFFLE_H
#define MOO2_V131_RANDOM_SHUFFLE_H
#include <stddef.h>
#include <stdint.h>
typedef enum {
    MOO2_V131_SHUFFLE_OK=0,
    MOO2_V131_SHUFFLE_INVALID=1,
    MOO2_V131_SHUFFLE_RNG_FAILED=2
} Moo2V131ShuffleResult;
Moo2V131ShuffleResult moo2_v131_derived_random(
    uint32_t *original_seed,uint32_t inclusive_upper,uint32_t *result);
Moo2V131ShuffleResult moo2_v131_derived_shuffle_int(
    uint32_t *original_seed,uint8_t *records,
    size_t count,size_t record_stride);
#endif
