/*
 * Original v1.31 Pre_Import_Computing_ CODE 0xD1D59,
 * 198 original Watcom bytes, full source body SHA256
 * 7aa1ea0d54d5e89f82905724eb7fc1609c1e2b9a715c828f557fb4a9224d6628
 * Original ORION2.EXE SHA256
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Complete outer control, exact field writes, full source-derived
 * Food2_Per_Farmer_, Colony_Environmental_Stuff_,
 * Industry_Per_Worker_ and Research_Per_Scientist_ math.
 * Ten remaining original named economy callees are explicit
 * callbacks, not guessed gameplay state changes.
 *
 * The 15 exact original call-sites include four recovered
 * calculations, ten remaining named functions, and memset_.
 *
 * ABI EAX=colony pointer, internal original ECX stores pointer.
 * WATCOM CODE 0xD1D63 memset(colony+0xEF,0,4);
 * Food low AL saved colony+0xDD; Industry low AL saved +0xDE;
 * Research low AL saved +0xDF; environmental updates +0xE0,+0xE2.
 * After source original Colony_Replicators_ call, store signed
 * min(zeroextend BYTE+0xF0, WORD+0xE9) as WORD+0xF5.
 *
 * Source invocation order:
 * Food2, Environmental, Industry_Per_Worker, Research_Per_Scientist,
 * Morale, Industry_Maintenance, Industry_Production, Food_Production,
 * Food_Maintenance, Replicators, [calculate min f0,e9],
 * Research_Production, Industry_To_Tax, BC_Production, BC_Maintenance.
 *
 * Host bounds/callback failure errors are modern safety additions;
 * already-applied state changes are NOT rolled back on failure.
 */
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "pre_import_computing_v131.h"
#include "colony_food_per_farmer_v131.h"
#include "colony_environmental_stuff_v131.h"
#include "colony_worker_scientist_v131.h"

static int32_t moo2_v131_pre_s16(const uint8_t *p) {
    uint16_t val=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return val<32768u?(int32_t)val:(int32_t)val-65536;
}
static void moo2_v131_pre_store16(uint8_t *p,int32_t value){
    uint16_t n=(uint16_t)value;
    p[0]=(uint8_t)n;
    p[1]=(uint8_t)(n>>8);
}
static int16_t moo2_v131_pre_environment_food_adapter(
    void *opaque,uint8_t *colony,int32_t signed_owner,int32_t ebx_zero)
{
    const Moo2V131FoodContext *f=(const Moo2V131FoodContext *)opaque;
    uint32_t output=0u;
    if(ebx_zero!=0 || signed_owner<0 ||
       signed_owner>INT16_MAX ||
       moo2_v131_derived_colony_food_per_farmer(
         f,colony,0x169u,(int16_t)signed_owner,NULL,0u,&output)
         !=MOO2_V131_FOOD_OK)
        return 0;
    return (int16_t)(uint16_t)output;
}
static int moo2_v131_pre_call(const Moo2V131PreImportContext *ctx,
                             Moo2V131PreImportStage stage,uint8_t *colony){
    return ctx->pending_callee(ctx->opaque,stage,colony);
}
Moo2V131PreImportStatus moo2_v131_derived_pre_import_computing(
    const Moo2V131PreImportContext *ctx,
    uint8_t *colony,size_t colony_bytes)
{
    if(!ctx || !ctx->planets || !ctx->players || !colony ||
       colony_bytes<0x169u || !ctx->pending_callee ||
       (int8_t)colony[0]<0 ||
       (size_t)colony[0]>=ctx->player_count)
        return MOO2_V131_PREIMPORT_INVALID;
    int32_t planet_index=moo2_v131_pre_s16(colony+2u);
    if(planet_index<0 || (size_t)planet_index>=ctx->planet_count ||
       ctx->planets[(size_t)planet_index*0x11u+0x0Au]>=5u)
        return MOO2_V131_PREIMPORT_INVALID;

    Moo2V131FoodContext food={
       ctx->planets,ctx->planet_count,ctx->players,ctx->player_count
    };
    Moo2V131WorkerScientistContext worker={
       ctx->planets,ctx->planet_count,ctx->players,ctx->player_count
    };
    Moo2V131ColonyEnvironmentContext environment={
       ctx->planets,ctx->planet_count,
       moo2_v131_pre_environment_food_adapter,&food
    };

    /* Original memset_ CODE 0xD1D6A length4 and zero argument. */
    memset(colony+0xEFu,0,4u);
    uint32_t production=0u;
    const int16_t owner=(int16_t)(int8_t)colony[0u];
    if(moo2_v131_derived_colony_food_per_farmer(
         &food,colony,colony_bytes,owner,NULL,0u,&production)
       !=MOO2_V131_FOOD_OK)
        return MOO2_V131_PREIMPORT_INVALID;
    colony[0xDDu]=(uint8_t)production;
    if(moo2_v131_derived_colony_environmental(
         &environment,colony,colony_bytes)!=MOO2_V131_COLONY_ENV_OK)
        return MOO2_V131_PREIMPORT_INVALID;
    if(moo2_v131_derived_industry_per_worker(
         &worker,colony,colony_bytes,owner,NULL,0u,&production)
       !=MOO2_V131_WORKER_SCIENTIST_OK)
        return MOO2_V131_PREIMPORT_INVALID;
    colony[0xDEu]=(uint8_t)production;
    if(moo2_v131_derived_research_per_scientist(
         &worker,colony,colony_bytes,NULL,0u,&production)
       !=MOO2_V131_WORKER_SCIENTIST_OK)
        return MOO2_V131_PREIMPORT_INVALID;
    colony[0xDFu]=(uint8_t)production;

    for(int stage=MOO2_V131_PRE_MORALE;
        stage<=MOO2_V131_PRE_REPLICATORS;stage++)
        if(!moo2_v131_pre_call(ctx,(Moo2V131PreImportStage)stage,colony))
            return MOO2_V131_PREIMPORT_PENDING_CALLEE_FAILED;
    /* Original MOVZX AX BYTE+F0 and signed JL compare to WORD+E9. */
    int32_t a=(int32_t)colony[0xF0u];
    int32_t b=moo2_v131_pre_s16(colony+0xE9u);
    moo2_v131_pre_store16(colony+0xF5u,a<b?a:b);
    for(int stage=MOO2_V131_PRE_RESEARCH_PRODUCTION;
        stage<=MOO2_V131_PRE_BC_MAINTENANCE;stage++)
        if(!moo2_v131_pre_call(ctx,(Moo2V131PreImportStage)stage,colony))
            return MOO2_V131_PREIMPORT_PENDING_CALLEE_FAILED;
    return MOO2_V131_PREIMPORT_OK;
}
