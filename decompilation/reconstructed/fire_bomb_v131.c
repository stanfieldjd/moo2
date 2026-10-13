/*
 * DERIVED MOO2 v1.31 Fire_Bomb_ arithmetic/loop shape, not original source.
 * Authenticated ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Original CODE 0x2A6CA..0x2A7A9, 224 bytes:
 *  - EAX/AX combat ship index; EBX/BX weapon slot index
 *  - _combat_data -> 313-byte combat records; 11-byte weapon slots
 *  - signed 16-bit weapon ID at slot+0, firing-count BYTE at slot+9
 *  - _ordnance_bonus[ship+0x20] signed WORD at DATA+0x21224
 *  - _weapons: 28-byte definitions, signed WORD +0x14, +0x16, +0x12
 *  - Random_ (CODE 0x1147A0) called with EAX=100
 *  - Apply_Damage_To_Planet_ (0x2A3C3) called with EAX=&damage,
 *    EDX=0, EBX=signext WORD definition+0x12
 *
 * The helpers are left as CALLBACKS. This reconstruction does not
 * pretend to emulate the original random-state machine, planet damage,
 * record lifetime, or original Watcom fastcall ABI. All host checks and
 * explicit unsigned accumulation are modern safe-API differences.
 */
#include <stddef.h>
#include <stdint.h>

typedef uint16_t (*Moo2V131BombRandom100)(void *opaque);
typedef void (*Moo2V131BombApplyPlanetDamage)(
    void *opaque,int32_t *inout_damage,int16_t definition_field_12);

typedef struct {
    const uint8_t *combat_records;
    size_t combat_record_count;
    const uint8_t *weapon_definitions;
    size_t weapon_definition_count;
    const uint8_t *ordnance_bonus_le_words;
    size_t ordnance_bonus_count;
    Moo2V131BombRandom100 random100;
    Moo2V131BombApplyPlanetDamage apply_damage;
    void *callbacks_context;
} Moo2V131BombContext;

typedef enum {
    MOO2_V131_BOMB_OK=0,
    MOO2_V131_BOMB_INVALID_INPUT=1
} Moo2V131BombStatus;

static uint16_t moo2_v131_bomb_le16(const uint8_t *bytes) {
    return (uint16_t)((uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8));
}
static int32_t moo2_v131_bomb_s16_bits(uint16_t value) {
    return value<UINT16_C(0x8000) ? (int32_t)value : ((int32_t)value - 65536);
}
static int32_t moo2_v131_bomb_s16(const uint8_t *bytes) {
    return moo2_v131_bomb_s16_bits(moo2_v131_bomb_le16(bytes));
}

/*
 * Source-derived EAX return is ECX, a 32-bit accumulator. Two external
 * callbacks replace Random_(100) and Apply_Damage_To_Planet_.
 * Original call to Random_ returns a value whose LOW AX is sign-extended
 * by CWDE, so callback returns bits of AX (not a host float).
 * The initial unmodified 8-bit firing count is read at the end of each
 * iteration, as in the original machine code, not captured once.
 */
Moo2V131BombStatus moo2_v131_derived_fire_bomb(
    const Moo2V131BombContext *ctx,int16_t ship_index,int16_t slot,
    uint32_t *total_damage)
{
    if(!ctx || !total_damage || !ctx->combat_records ||
       !ctx->weapon_definitions || !ctx->ordnance_bonus_le_words ||
       !ctx->random100 || !ctx->apply_damage || ship_index<0 ||
       slot<0 || slot>=8 || (size_t)ship_index>=ctx->combat_record_count)
        return MOO2_V131_BOMB_INVALID_INPUT;

    const uint8_t *ship=ctx->combat_records+
                         (size_t)ship_index*313u;
    const uint8_t *weapon_slot=ship+0x52u+(size_t)slot*11u;
    const int32_t weapon_id=moo2_v131_bomb_s16(weapon_slot);
    if (weapon_id<0 || (size_t)weapon_id>=ctx->weapon_definition_count)
        return MOO2_V131_BOMB_INVALID_INPUT;

    const uint8_t owner=ship[0x20];
    if((size_t)owner>=ctx->ordnance_bonus_count)
        return MOO2_V131_BOMB_INVALID_INPUT;

    const int32_t bonus=moo2_v131_bomb_s16(
        ctx->ordnance_bonus_le_words+2u*(size_t)owner);
    const uint8_t *def=ctx->weapon_definitions+(size_t)weapon_id*28u;
    const int32_t base_min=moo2_v131_bomb_s16(def+0x14u);
    const int32_t base_max=moo2_v131_bomb_s16(def+0x16u);
    const int32_t min_scaled=(base_min*bonus)/100;
    const int32_t max_scaled=(base_max*bonus)/100;
    const int32_t spread=max_scaled-min_scaled;

    uint32_t total=0;
    /* Original loop starts by testing count byte against 0, then invokes
       the body while count > executed iterations (signed WORD comparison).
       As a byte count, this yields at most 255 iterations when unchanged.
       Callback may change combat data, so reread each loop condition.
       Safety cap 255 is a host guard; not a claim about malicious callbacks
       mutating the count in the original DOS memory model. */
    for(unsigned i=0; i<255u && i<(unsigned)weapon_slot[9];i++) {
        const int32_t random16=moo2_v131_bomb_s16_bits(
            ctx->random100(ctx->callbacks_context));
        const int32_t weighted=(random16*
            moo2_v131_bomb_s16_bits((uint16_t)spread))/100;
        int32_t damage=weighted+
            moo2_v131_bomb_s16_bits((uint16_t)min_scaled);
        ctx->apply_damage(ctx->callbacks_context,&damage,
                          (int16_t)moo2_v131_bomb_s16(def+0x12u));
        total+=(uint32_t)damage;
    }
    *total_damage=total;
    return MOO2_V131_BOMB_OK;
}
