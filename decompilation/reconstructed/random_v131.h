#ifndef MOO2_V131_DERIVED_RANDOM_H
#define MOO2_V131_DERIVED_RANDOM_H
#include <stdint.h>

/* Derived original MOO2 v1.31 Watcom Random_ host interface. */
typedef enum {
    MOO2_V131_RANDOM_OK=0,
    MOO2_V131_RANDOM_ZERO_MAXIMUM=1,
    MOO2_V131_RANDOM_INVALID_POINTER=2
} Moo2V131RandomStatus;

Moo2V131RandomStatus moo2_v131_derived_random(
    uint32_t *random_seed,uint32_t maximum,uint32_t *result);
#endif
