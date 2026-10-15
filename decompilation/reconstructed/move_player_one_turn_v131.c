/*
 * Source-derived full original 422-byte v1.31 Watcom
 * Move_Player_1_Turn_To_Star_ (original CODE 0xDBB0C..0xDBCB1).
 * Original complete CODE SHA256:
 * 01baaeca994622f9d2d56541ef9b5a5463ffdd619a20054c34c4230e8e2c64cb
 * Original ORION2.EXE:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Source protocol: EAX owner, EDX old X, EBX old Y, ECX star;
 * 5 stack args: speed, X-output ptr, Y-output ptr, optional nebula-byte
 * output ptr, required warp-field byte output ptr.
 *
 * The original source calculates signed dx/dy from WORD coordinates,
 * computes sqrt((uint32)(dx*dx+dy*dy)) with original isqrt_,
 * then tries t=1...speed 30-unit coordinate steps:
 * if (t*t*900 >= signed squared distance), X,Y become destination;
 * else rounded step = (t*30*abs(delta)+sqrt-1)/sqrt,
 * coordinates = initial +/- rounded step (WORD truncation).
 *
 * Each candidate coordinate may trigger the original named nebula
 * query (ONLY if optional output pointer is not NULL). On nebula hit,
 * stop, set optional output to 1 at exit. The warp helper ALWAYS runs
 * when nebula does not abort, and sets required byte on interdictor hit.
 * Initial required byte becomes 0. The other return is via RET 0x14.
 *
 * Important source detail: on direct arrival candidate CODE 0xDBBA8
 * writes WORD 0 to stack local that initially held owner EAX.
 * Hence warp check on the arrival candidate receives excluded owner 0,
 * while intermediate candidates receive low WORD of original owner.
 *
 * Host safety guards for byte-array bounds, finite speed, and status
 * propagation are not DOS behavior. No approximate movement callbacks
 * are used: integer math, nebula cell tests and warp-radius checks are
 * supplied by the previously independently source-recovered C helpers.
 */
#include <stddef.h>
#include <stdint.h>
#include "isqrt_v131.h"
#include "point_in_nebula_v131.h"
#include "point_in_warp_field_v131.h"

typedef struct {
    const uint8_t *stars;
    size_t star_count;
    const Moo2V131NebulaContext *nebulas;
} Moo2V131MoveContext;
typedef enum {
    MOO2_V131_MOVE_OK=0,
    MOO2_V131_MOVE_INVALID=1
} Moo2V131MoveResult;

static int32_t moo2_v131_move_s16(uint16_t n) {
    return n<32768u?(int32_t)n:(int32_t)n-65536;
}
static uint16_t moo2_v131_move_read_word(const uint8_t *p) {
    return (uint16_t)(p[0]|((uint16_t)p[1]<<8));
}
static int32_t moo2_v131_move_signed32(uint32_t n) {
    return n<=INT32_MAX?(int32_t)n:(int32_t)((int64_t)n-INT64_C(4294967296));
}
Moo2V131MoveResult moo2_v131_derived_move_player_one_turn(
    const Moo2V131MoveContext *ctx,
    int32_t owner_id,int32_t star_id,
    int16_t starting_x,int16_t starting_y,
    uint32_t original_speed,
    int16_t *x_out,int16_t *y_out,
    uint8_t *optional_nebula_hit,uint8_t *required_warp_hit)
{
    if(!ctx || !ctx->stars || !x_out || !y_out ||
       !required_warp_hit || !ctx->nebulas ||
       star_id<0 || (size_t)star_id>=ctx->star_count ||
       owner_id<0 || owner_id>7 || original_speed>255u)
        return MOO2_V131_MOVE_INVALID;
    const uint8_t *star=ctx->stars+(size_t)star_id*0x71u;
    int32_t tx=moo2_v131_move_s16(
        moo2_v131_move_read_word(star+0x0fu));
    int32_t ty=moo2_v131_move_s16(
        moo2_v131_move_read_word(star+0x11u));
    int32_t dx=tx-starting_x,dy=ty-starting_y;
    uint32_t dist2_bits=(uint32_t)
        ((uint64_t)((int64_t)dx*dx)+(uint64_t)((int64_t)dy*dy));
    int32_t signed_dist2=moo2_v131_move_signed32(dist2_bits);
    uint32_t original_sqrt=moo2_v131_derived_isqrt(dist2_bits);
    uint32_t speed=original_speed?original_speed:1u;

    /* Original source performs no mutable x,y input write until
       the first candidate. The compulsory status BYTE is zeroed
       before beginning the t=1 loop. */
    *required_warp_hit=0u;
    uint8_t nebula_encountered=0u;
    int16_t last_x=starting_x,last_y=starting_y;
    for(uint32_t t=1u;t<=speed;t++) {
        int32_t step=(int32_t)(uint16_t)t;
        uint32_t square_bits=(uint32_t)((uint64_t)step*step*900u);
        int arrived=moo2_v131_move_signed32(square_bits)>=signed_dist2;
        int32_t candidate_x,candidate_y;
        if(arrived) {
            candidate_x=tx;
            candidate_y=ty;
        } else {
            if(original_sqrt==0u)
                return MOO2_V131_MOVE_INVALID;
            uint64_t rounds_x=(uint64_t)t*30u*
                    (uint32_t)(dx<0?-dx:dx)+original_sqrt-1u;
            uint64_t rounds_y=(uint64_t)t*30u*
                    (uint32_t)(dy<0?-dy:dy)+original_sqrt-1u;
            int32_t inc_x=(int32_t)(rounds_x/original_sqrt);
            int32_t inc_y=(int32_t)(rounds_y/original_sqrt);
            candidate_x=starting_x+(dx<0?-inc_x:inc_x);
            candidate_y=starting_y+(dy<0?-inc_y:inc_y);
        }
        uint16_t xb=(uint16_t)candidate_x;
        uint16_t yb=(uint16_t)candidate_y;
        last_x=(int16_t)moo2_v131_move_s16(xb);
        last_y=(int16_t)moo2_v131_move_s16(yb);
        *x_out=last_x;
        *y_out=last_y;

        if(optional_nebula_hit) {
            uint8_t found=0;
            if(moo2_v131_derived_point_in_some_nebula(
                ctx->nebulas,last_x,last_y,&found)!=MOO2_V131_NEBULA_OK)
                return MOO2_V131_MOVE_INVALID;
            if(found) {
                nebula_encountered=1u;
                break;
            }
        }
        /* CODE 0xDBBA8 clears owner low WORD on arrival candidate. */
        const uint8_t effective_owner=(uint8_t)(arrived?0u:(uint32_t)owner_id);
        uint8_t in_warp=0u;
        if(moo2_v131_derived_is_in_warp_field(
            star,0x71u,last_x,last_y,effective_owner,
            &in_warp)!=MOO2_V131_WARP_OK)
            return MOO2_V131_MOVE_INVALID;
        if(in_warp) {
            *required_warp_hit=1u;
            break;
        }
        if(arrived)
            break;
    }
    if(nebula_encountered && optional_nebula_hit)
        *optional_nebula_hit=1u;
    return MOO2_V131_MOVE_OK;
}
