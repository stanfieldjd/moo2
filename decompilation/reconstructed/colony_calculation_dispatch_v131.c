/*
 * Full dispatcher/control reconstruction of original MOO2 v1.31
 * Colony_Calculation_ CODE 0xD2A70, 65 bytes.
 * Original executable SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Original complete function SHA256:
 * e667850010cdc8cb620bb98fcc6fe0c2b12971f572a8c48930c88833b940d63d
 *
 * Original EAX low16 signed colony index (CWDE), colony stride
 * 0x169 (361). Colony BYTE+6 !=0 skips production. Otherwise:
 *  0xD2A89 CALL Pre_Import_Computing_ CODE 0xD1D59, EAX=colony*
 *  0xD2A93 CALL Pass_Out_Imports_ CODE 0xCF8F0,
 *          EAX=SIGNED owner BYTE+0, EDX=colony*
 * Then always:
 *  0xD2AA9 CALL Update_Player_Stats_ CODE 0xD2710,
 *          EAX=_player+SIGNED owner BYTE+0 * 0xEA9.
 *
 * The source loads owner separately after production and again
 * before stats, so callbacks that change owner can affect routing.
 * Original 198-byte Pre_Import_Computing_, 1238-byte
 * Pass_Out_Imports_ and 864-byte Update_Player_Stats_ remain
 * explicit named callbacks; do not substitute invented economy.
 *
 * Host rejects invalid indexes, callback errors and corrupted owner,
 * unlike original DOS unbounded reads. State already mutated by a
 * callback is not rolled back on failure.
 */
#include <stddef.h>
#include <stdint.h>
#include "colony_calculation_dispatch_v131.h"

Moo2V131ColonyCalculationStatus moo2_v131_derived_colony_calculation(
    const Moo2V131ColonyCalculationContext *ctx,
    int16_t colony_index)
{
    if(!ctx || !ctx->colonies || !ctx->players ||
       !ctx->pre_import || !ctx->pass_out_imports ||
       !ctx->update_player_stats || colony_index<0 ||
       (size_t)colony_index>=ctx->colony_count)
        return MOO2_V131_COLONYCALC_INVALID;
    uint8_t *colony=ctx->colonies+(size_t)colony_index*0x169u;
    if(colony[6u]==0u) {
        if(!ctx->pre_import(ctx->opaque,colony))
            return MOO2_V131_COLONYCALC_CALLEE_FAILED;
        int8_t owner=(int8_t)colony[0u];
        if(owner<0 || (size_t)owner>=ctx->player_count)
            return MOO2_V131_COLONYCALC_INVALID;
        if(!ctx->pass_out_imports(ctx->opaque,owner,colony))
            return MOO2_V131_COLONYCALC_CALLEE_FAILED;
    }
    int8_t owner=(int8_t)colony[0u];
    if(owner<0 || (size_t)owner>=ctx->player_count)
        return MOO2_V131_COLONYCALC_INVALID;
    uint8_t *player=ctx->players+(size_t)owner*0xEA9u;
    if(!ctx->update_player_stats(ctx->opaque,player))
        return MOO2_V131_COLONYCALC_CALLEE_FAILED;
    return MOO2_V131_COLONYCALC_OK;
}
