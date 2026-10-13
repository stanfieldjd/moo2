/*
 * DERIVED Master of Orion II v1.31 Apply_Bomb_Hits_ callback-bounded loop.
 * Not original MicroProse C. Does NOT implement Resolve_Bomb_Hit_ or
 * Resolve_Biological_Hit_ effects, game state, graphics or save systems.
 *
 * Original CODE: Apply_Bomb_Hits_ 0xCD2F2..0xCD350, 95 bytes.
 * Original shared epilogue: 0xCCDA5..0xCCDAB outside named function.
 * This is valid shared Watcom LEAVE/POPs/RET (not a self-contained
 * 95-byte RET path).
 *
 * Original input EAX -> 73-byte+ combat bomb result/event struct.
 *   BYTE  at event+0x01: original colony record index (unsigned)
 *   WORD  at event+0x03: signed ordinary hit count
 *   WORD  at event+0x06: signed biological hit count
 *   DWORD at event+0x45: hit resolver returned-value accumulator
 * Original colony pointer _colony (DATA +0x1AB18), record stride 0x169.
 *
 * While (normal_count + bio_count)>0:
 *   if bio_count !=0:
 *     Resolve_Biological_Hit_(colony_ptr, event_ptr); --bio_count
 *   else:
 *     consumed=Resolve_Bomb_Hit_(colony_ptr, normal_count,event_ptr)
 *     if consumed !=0:
 *       normal_count-=consumed
 *       event->DWORD[0x45]+=consumed
 *     else normal_count=0
 * Shared epilogue returns final EAX value (signed local sum at loop exit).
 *
 * This derived code uses explicit callbacks and host allocation checks.
 * Safety iteration cap and rejection of invalid memory are deliberate
 * departures from DOS behavior. No resolver result sign is assumed.
 */
#include <stddef.h>
#include <stdint.h>

typedef int32_t (*Moo2V131ResolveBombHit)(
    void *opaque,uint8_t *colony_record,int32_t remaining_normal,
    uint8_t *event);
typedef void (*Moo2V131ResolveBiologicalHit)(
    void *opaque,uint8_t *colony_record,uint8_t *event);

typedef struct {
    uint8_t *colony_records;
    size_t colony_record_count;
    Moo2V131ResolveBombHit resolve_bomb;
    Moo2V131ResolveBiologicalHit resolve_biological;
    void *opaque;
} Moo2V131ApplyBombHitsContext;

typedef enum {
    MOO2_V131_APPLY_BOMB_HITS_OK=0,
    MOO2_V131_APPLY_BOMB_HITS_INVALID=1,
    MOO2_V131_APPLY_BOMB_HITS_ITERATION_LIMIT=2
} Moo2V131ApplyBombHitsStatus;

static uint16_t moo2_v131_bomb_hits_u16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0]|(uint16_t)((uint16_t)p[1]<<8));
}
static int32_t moo2_v131_bomb_hits_s16(const uint8_t *p)
{
    const uint16_t v=moo2_v131_bomb_hits_u16(p);
    return v<UINT16_C(0x8000)?(int32_t)v:((int32_t)v-65536);
}
static uint32_t moo2_v131_bomb_hits_u32(const uint8_t *p)
{
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}
static void moo2_v131_bomb_hits_write32(uint8_t *p,uint32_t x)
{
    p[0]=(uint8_t)x;p[1]=(uint8_t)(x>>8);
    p[2]=(uint8_t)(x>>16);p[3]=(uint8_t)(x>>24);
}

Moo2V131ApplyBombHitsStatus moo2_v131_derived_apply_bomb_hits(
    const Moo2V131ApplyBombHitsContext *ctx,
    uint8_t *event,size_t event_bytes,size_t max_callback_iterations,
    int32_t *original_eax_return)
{
    if (!ctx || !event || event_bytes<0x49u ||
        !original_eax_return || !ctx->colony_records ||
        !ctx->resolve_bomb || !ctx->resolve_biological ||
        !max_callback_iterations ||
        (size_t)event[1]>=ctx->colony_record_count)
        return MOO2_V131_APPLY_BOMB_HITS_INVALID;

    uint8_t *colony=ctx->colony_records+(size_t)event[1]*0x169u;
    int32_t normal=moo2_v131_bomb_hits_s16(event+3u);
    int32_t biological=moo2_v131_bomb_hits_s16(event+6u);
    size_t iterations=0;
    for(;;) {
        /* Original LEA EAX,[ESI+EDI] tests the signed 32-bit sum.
           Use int64_t to avoid signed C overflow on abnormal callbacks,
           then retain the low 32-bit pattern as original x86 behavior. */
        uint32_t sum_bits=(uint32_t)normal+(uint32_t)biological;
        int64_t signed_sum=(sum_bits<UINT32_C(0x80000000))
            ?(int64_t)sum_bits:((int64_t)sum_bits-4294967296LL);
        if(signed_sum<=0) {
            *original_eax_return=(int32_t)signed_sum;
            return MOO2_V131_APPLY_BOMB_HITS_OK;
        }
        if(iterations++ >= max_callback_iterations)
            return MOO2_V131_APPLY_BOMB_HITS_ITERATION_LIMIT;
        if(biological!=0) {
            ctx->resolve_biological(ctx->opaque,colony,event);
            biological=(int32_t)((uint32_t)biological-1u);
        } else {
            int32_t resolved=ctx->resolve_bomb(
                ctx->opaque,colony,normal,event);
            if(resolved!=0) {
                normal=(int32_t)((uint32_t)normal-(uint32_t)resolved);
                uint32_t total=moo2_v131_bomb_hits_u32(event+0x45u);
                moo2_v131_bomb_hits_write32(event+0x45u,
                                            total+(uint32_t)resolved);
            } else {
                normal=0;
            }
        }
    }
}
