/*
 * DERIVED complete original Watcom MOO2 v1.31 Assign_New_Home_Planet_.
 * Not original MicroProse source, nor original DOS ABI/run environment.
 * Original executable SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Original CODE 0xDCB65..0xDCBF6 (146 bytes),
 * original full-body SHA256
 * b246802362b4d87ded1ea4efca66c4adaa18aa67f3f8b0ba6ba79b34374efd05.
 *
 * Inputs: EAX original player ID, EDX excluded colony index;
 * _NUM_COLONIES: signed WORD DATA+0x21996.
 * Reverse-scan from N-1 to 0; ignore the excluded colony,
 * compare signed colony owner BYTE+0 with EAX owner;
 * choose candidate if unsigned population BYTE+0x0A >= current best,
 * initially 0. Because the scan is descending, tied population counts
 * select the LOWEST matching colony index. Store that colony's signed
 * planet ID WORD+0x02 (raw 16-bit) into player WORD+0x29, owner stride 0xEA9.
 * If none qualifies, store 0xFFFF.
 *
 * Host checks reject unsafe memory buffers and invalid signed inputs,
 * which the original DOS routine does not explicitly check.
 * Colony count is supplied from the authenticated _NUM_COLONIES value;
 * this helper makes exactly the identified original player WORD write.
 */
#include <stddef.h>
#include <stdint.h>
#include "assign_new_home_planet_v131.h"

Moo2V131AssignHomeStatus moo2_v131_derived_assign_new_home_planet(
    const uint8_t *colonies,size_t colony_count,
    uint8_t *players,size_t player_bytes,
    int32_t owner_id,int32_t excluded_colony_id,
    uint16_t *planet_word_written)
{
    if(!players || owner_id<0 || owner_id>127 ||
       colony_count>32767u || (colony_count && !colonies))
        return MOO2_V131_ASSIGN_HOME_INVALID;

    const size_t target=(size_t)owner_id*0xEA9u+0x29u;
    if(player_bytes<2u || target>player_bytes-2u)
        return MOO2_V131_ASSIGN_HOME_INVALID;

    size_t picked=colony_count;
    uint32_t best=0u;
    for(size_t p=colony_count;p>0;p--) {
        const size_t index=p-1u;
        if((int32_t)index==excluded_colony_id)
            continue;
        const uint8_t *record=colonies+index*0x169u;
        int32_t actual_owner=record[0]<128u
            ?(int32_t)record[0]:(int32_t)record[0]-256;
        if(actual_owner!=owner_id)
            continue;
        const uint32_t population=record[0x0Au];
        if(population>=best) {
            best=population;
            picked=index;
        }
    }
    uint16_t chosen=UINT16_C(0xFFFF);
    if(picked<colony_count) {
        const uint8_t *source=colonies+picked*0x169u+2u;
        chosen=(uint16_t)((uint16_t)source[0]|
                          ((uint16_t)source[1]<<8));
    }
    players[target]=(uint8_t)chosen;
    players[target+1u]=(uint8_t)(chosen>>8);
    if(planet_word_written)*planet_word_written=chosen;
    return MOO2_V131_ASSIGN_HOME_OK;
}
