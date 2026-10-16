#ifndef MOO2_V131_COLONY_INDUSTRY_TAX_H
#define MOO2_V131_COLONY_INDUSTRY_TAX_H
#include <stddef.h>
#include <stdint.h>
typedef enum {
    MOO2_V131_INDUSTRY_TAX_OK=0,
    MOO2_V131_INDUSTRY_TAX_INVALID=1
} Moo2V131IndustryTaxStatus;
typedef struct {
    const uint8_t *players;
    size_t player_count;
} Moo2V131IndustryTaxContext;
Moo2V131IndustryTaxStatus moo2_v131_derived_colony_industry_to_tax(
    const Moo2V131IndustryTaxContext *ctx,
    uint8_t *colony,size_t colony_bytes);
#endif
