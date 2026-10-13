/*
 * DERIVED original v1.31 random-seed lifecycle and restore helper.
 * Not MicroProse source code or a complete save-game implementation.
 *
 * Original functions:
 *   Set_Game_Random_Seed_ @ CODE 0x0007CA (28 bytes)
 *   Random_With_Restore_ @ CODE 0x069F05 (33 bytes)
 *   Set_Random_Seed_ @ CODE 0x114820 (44 bytes)
 *   Get_Random_Seed_ @ CODE 0x11484C (44 bytes)
 *   Randomize_ @ CODE 0x114878 (51 bytes)
 *
 * Original DATA _random_seed at object-2 offset 0x41E34;
 * _cmd_line_seed at DATA offset 0x1B27C.
 *
 * Original Set_Game_Random_Seed_ calls Check_Release_Version_
 * first, then calls Randomize_ if _cmd_line_seed is ZERO, otherwise
 * tail-jumps to Set_Random_Seed_ with _cmd_line_seed.
 * Randomize_ calls time_(NULL), then Set_Random_Seed_ with its DWORD
 * result. Random_With_Restore_ saves seed, invokes Random_(bound),
 * restores seed and sign-extends the low 16 bits of result.
 *
 * Source-derived Random_ is in random_v131.c/.h.
 * Host callback boundaries explicitly stand in for the original
 * Check_Release_Version_ and time_ runtime side effects.
 */
#include <stdint.h>
#include "random_v131.h"

typedef enum {
    MOO2_V131_SEED_OK=0,
    MOO2_V131_SEED_BAD_ARGS=1,
    MOO2_V131_SEED_ZERO_BOUND=2
} Moo2V131SeedStatus;

typedef struct {
    void (*check_release_version)(void *opaque);
    uint32_t (*time_null)(void *opaque);
    void *opaque;
} Moo2V131SeedHooks;

Moo2V131SeedStatus moo2_v131_derived_set_random_seed(
    uint32_t *random_seed,uint32_t new_seed)
{
    if(!random_seed)return MOO2_V131_SEED_BAD_ARGS;
    *random_seed=new_seed;
    return MOO2_V131_SEED_OK;
}

Moo2V131SeedStatus moo2_v131_derived_get_random_seed(
    const uint32_t *random_seed,uint32_t *result)
{
    if(!random_seed || !result)return MOO2_V131_SEED_BAD_ARGS;
    *result=*random_seed;
    return MOO2_V131_SEED_OK;
}

Moo2V131SeedStatus moo2_v131_derived_randomize_seed(
    uint32_t *random_seed,const Moo2V131SeedHooks *hooks)
{
    if(!random_seed || !hooks || !hooks->time_null)
        return MOO2_V131_SEED_BAD_ARGS;
    return moo2_v131_derived_set_random_seed(
        random_seed,hooks->time_null(hooks->opaque));
}

Moo2V131SeedStatus moo2_v131_derived_set_game_random_seed(
    uint32_t *random_seed,uint32_t command_line_seed,
    const Moo2V131SeedHooks *hooks)
{
    if(!random_seed || !hooks || !hooks->check_release_version ||
       !hooks->time_null)return MOO2_V131_SEED_BAD_ARGS;
    hooks->check_release_version(hooks->opaque);
    if(command_line_seed!=0u)
        return moo2_v131_derived_set_random_seed(
            random_seed,command_line_seed);
    return moo2_v131_derived_randomize_seed(random_seed,hooks);
}

/*
 * Result is SIGNED 16-bit (MOVSX EAX,BX) even though original Random_
 * returns a full-width 32-bit result. Seed is restored by
 * Set_Random_Seed_ after the call; original concurrent effects are
 * not reproduced in this single-state host function.
 */
Moo2V131SeedStatus moo2_v131_derived_random_with_restore(
    uint32_t *random_seed,uint32_t maximum,int32_t *result)
{
    if(!random_seed || !result)return MOO2_V131_SEED_BAD_ARGS;
    uint32_t before=*random_seed;
    uint32_t draw=0;
    Moo2V131RandomStatus status=
        moo2_v131_derived_random(random_seed,maximum,&draw);
    if(status!=MOO2_V131_RANDOM_OK) {
        *random_seed=before;
        return status==MOO2_V131_RANDOM_ZERO_MAXIMUM
          ? MOO2_V131_SEED_ZERO_BOUND:MOO2_V131_SEED_BAD_ARGS;
    }
    *random_seed=before;
    uint16_t low16=(uint16_t)draw;
    *result=low16<32768u ? (int32_t)low16:((int32_t)low16-65536);
    return MOO2_V131_SEED_OK;
}
