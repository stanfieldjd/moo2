/*
 * Derived original Master of Orion II v1.31 Update_Ship_ETAs_.
 * Original authenticated local ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Original CODE 0xF041C..0xF0518, 253 bytes; original body SHA256:
 * 5a1ebf719a02098beadf2b344252ce74850a8f6fc2c978dbb0f21910b603e78b.
 *
 * This translates the full SOURCE LOOP, not original movement effects:
 * - EAX argument is comparison owner (16-bit low word), source
 *   excludes ship+0x63 owner matching this EAX; yes, != is intentional.
 * - _NUM_SHIPS signed WORD at DATA 0x21994; ship stride 129.
 * - reverse-scan ship states BYTE+0x64 equal to 1 or 2.
 * - ship WORD+0x65 encodes destination star+500 for state1 or +1000
 *   for state2 (16-bit signed result); star stride 113.
 * - star signed coordinate WORDs at +0x0F, +0x11; ship current x,y
 *   signed WORDs +0x67,+0x69 are copied to 16-bit local coordinates,
 *   NOT modified in the original ship record.
 * - if coordinates already equal target, source writes ETA byte +0x6D=0.
 * - else repeated original Move_Player_1_Turn_To_Star_ CALL 0xDBB0C
 *   (owner signed byte, dest star, signed x/y, ship BYTE+0x6C,
 *   optional pointer when ship BYTE+0x6B==0 and mandatory status ptr);
 *   each movement iteration increments a local WORD counter;
 *   on arrival ship BYTE+0x6D gets LOW BYTE of the counter.
 *
 * Actual original Move_Player_1_Turn_To_Star_ is 422 bytes plus
 * additional callees, not replaced by guessed straight-line movement.
 * A host callback carries observable inputs and mutable local
 * x/y pointers. Pointer validation and max-turn cap are deliberate
 * non-DOS protections. If callback fails the current ship ETA
 * remains unchanged, but earlier ships may already have been updated.
 */
#include <stddef.h>
#include <stdint.h>

typedef int (*Moo2V131MoveOneTurn)(
    void *opaque,int32_t ship_owner,int32_t target_star_index,
    uint8_t source_parameter_6c,
    int16_t *current_x,int16_t *current_y,
    uint8_t *optional_out_when_ship_6b_zero,
    uint8_t *required_status_out);

typedef enum {
    MOO2_V131_ETA_OK=0,
    MOO2_V131_ETA_INVALID=1,
    MOO2_V131_ETA_ITERATION_LIMIT=2,
    MOO2_V131_ETA_CALLBACK_FAILED=3
} Moo2V131EtaResult;

typedef struct {
    uint8_t *ships;
    size_t ship_count;      /* original signed WORD _NUM_SHIPS */
    const uint8_t *stars;
    size_t star_count;
    Moo2V131MoveOneTurn move_one_turn;
    void *opaque;
    size_t max_steps_per_ship; /* host-only infinite-loop guard */
} Moo2V131EtaContext;

static int32_t moo2_v131_eta_s16(const uint8_t *p)
{
    uint16_t bits=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return bits<UINT16_C(0x8000)?(int32_t)bits:(int32_t)bits-65536;
}
static int32_t moo2_v131_eta_s8(uint8_t bits)
{
    return bits<128u?(int32_t)bits:(int32_t)bits-256;
}

Moo2V131EtaResult moo2_v131_derived_update_ship_etas(
    Moo2V131EtaContext *ctx,int16_t original_owner_argument,
    size_t *processed_ship_count)
{
    if(!ctx || !ctx->ships || !ctx->stars || !ctx->move_one_turn ||
       !ctx->max_steps_per_ship || ctx->ship_count>32767u)
        return MOO2_V131_ETA_INVALID;
    size_t processed=0;
    for(size_t p=ctx->ship_count;p>0;p--) {
        uint8_t *ship=ctx->ships+(p-1u)*0x81u;
        unsigned state=ship[0x64u];
        if(state!=1u && state!=2u)
            continue;
        int32_t ship_owner=moo2_v131_eta_s8(ship[0x63u]);
        if(ship_owner==(int32_t)original_owner_argument)
            continue;
        /* Source subtracts state-dependent offset from low 16 bits,
           then MOVSX EDI, AX. Explicit 16-bit wrap for DOS semantics. */
        uint16_t original_word=(uint16_t)((uint16_t)ship[0x65u]|
                                          ((uint16_t)ship[0x66u]<<8));
        uint16_t star_bits=(uint16_t)(original_word-
                                      (state==1u?500u:1000u));
        int32_t star_id=star_bits<UINT16_C(0x8000)?
            (int32_t)star_bits:(int32_t)star_bits-65536;
        if(star_id<0 || (size_t)star_id>=ctx->star_count)
            return MOO2_V131_ETA_INVALID;
        const uint8_t *star=ctx->stars+(size_t)star_id*0x71u;
        int16_t x=(int16_t)moo2_v131_eta_s16(ship+0x67u);
        int16_t y=(int16_t)moo2_v131_eta_s16(ship+0x69u);
        const int16_t target_x=(int16_t)moo2_v131_eta_s16(star+0x0Fu);
        const int16_t target_y=(int16_t)moo2_v131_eta_s16(star+0x11u);
        uint16_t turns=0u;
        while(x!=target_x || y!=target_y) {
            if((size_t)turns>=ctx->max_steps_per_ship) {
                if(processed_ship_count)*processed_ship_count=processed;
                return MOO2_V131_ETA_ITERATION_LIMIT;
            }
            /* Watcom passes pointer to an optional byte slot when
               ship[0x6B]==0; otherwise NULL. Callee can set statuses
               and must update original-style local x/y coordinates. */
            uint8_t optional_byte=0u;
            uint8_t required_byte=0u;
            uint8_t *optional=ship[0x6Bu]==0u?&optional_byte:NULL;
            turns=(uint16_t)(turns+1u);
            if(!ctx->move_one_turn(ctx->opaque,ship_owner,star_id,
                                   ship[0x6Cu],&x,&y,optional,&required_byte)) {
                if(processed_ship_count)*processed_ship_count=processed;
                return MOO2_V131_ETA_CALLBACK_FAILED;
            }
        }
        ship[0x6Du]=(uint8_t)turns;
        processed++;
    }
    if(processed_ship_count)*processed_ship_count=processed;
    return MOO2_V131_ETA_OK;
}
