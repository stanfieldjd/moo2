/*
 * DERIVED Master of Orion II v1.31 combat-ammunition decisions.
 * Not original MicroProse source code. Not the entire combat subsystem.
 *
 * Authentic ORION2.EXE SHA-256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Observed Watcom CODE:
 *   Check_For_Launched_Fighters_ @ 0x19480, 95 bytes
 *   Is_Ship_Out_Of_Ammo_       @ 0x194DF, 241 bytes
 *   Does_Combat_Ship_Have_Special_ @ 0x3B0D3 (delegated callback)
 *
 * Source data:
 *   _combat_data (DATA object 2 @ 0x1A864) -> combat ship records,
 *   0x139 bytes/record; 8 weapon slots of 11 bytes starting at +0x52.
 *   _missile (DATA @ 0x1AB14) -> missile records of 26 bytes; scan 300.
 *   _weapons (DATA @ 0x7803): definitions of 28 bytes; category +0x0C.
 *   unrelated unnamed DATA word @ 0x218AC -> comparison with ship +0x20.
 *
 * This isolation uses checked host memory bounds and explicit callbacks.
 * Invalid-memory results are NOT original DOS gameplay outcomes;
 * the original code assumes valid indices and can read out-of-bounds.
 */
#include <stddef.h>
#include <stdint.h>

enum {
    MOO2_V131_COMBAT_SHIP_STRIDE = 0x139,
    MOO2_V131_COMBAT_WEAPON_SLOTS = 8,
    MOO2_V131_COMBAT_WEAPON_SLOT_STRIDE = 11,
    MOO2_V131_WEAPON_DEFINITION_STRIDE = 28,
    MOO2_V131_MISSILE_STRIDE = 26,
    MOO2_V131_ORIGINAL_MISSILE_SLOTS = 300
};

/* Native reproduction of the *external* Watcom helper is not included. */
typedef uint16_t (*Moo2V131SpecialQuery)(void *context,
                                         int16_t combat_ship_index,
                                         uint16_t special_id);

typedef struct {
    const uint8_t *combat_ship_records; /* original _combat_data pointer */
    size_t combat_ship_count;
    const uint8_t *weapon_definitions; /* original _weapons data records */
    size_t weapon_definition_count;
    const uint8_t *missile_records; /* original _missile pointer */
    size_t missile_record_count;  /* at least 300 if supplied */
    uint16_t unnamed_comparison_word; /* original DATA+0x218AC */
    Moo2V131SpecialQuery has_special;
    void *special_context;
} Moo2V131CombatAmmoContext;

typedef enum {
    MOO2_V131_COMBAT_AMMO_OK = 0,
    MOO2_V131_COMBAT_AMMO_INVALID_INPUT = 1
} Moo2V131CombatAmmoStatus;

static uint16_t moo2_v131_ammo_le_u16(const uint8_t *p)
{
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

static int32_t moo2_v131_ammo_s16(const uint8_t *p)
{
    uint16_t n = moo2_v131_ammo_le_u16(p);
    return n < 32768u ? (int32_t)n : (int32_t)n-65536;
}

static int moo2_v131_ammo_valid_ship(const Moo2V131CombatAmmoContext *ctx,
                                    int16_t id)
{
    return ctx && ctx->combat_ship_records &&
           id >= 0 && (size_t)id < ctx->combat_ship_count;
}

static int moo2_v131_ammo_valid_weapon(const Moo2V131CombatAmmoContext *ctx,
                                      int32_t index)
{
    return ctx && ctx->weapon_definitions && index >= 0 &&
           (size_t)index < ctx->weapon_definition_count;
}

static uint8_t moo2_v131_ammo_category(const Moo2V131CombatAmmoContext *ctx,
                                       int32_t weapon_id)
{
    return ctx->weapon_definitions[
        (size_t)weapon_id * MOO2_V131_WEAPON_DEFINITION_STRIDE + 0x0Cu];
}

/*
 * Observed Check_For_Launched_Fighters_:
 * scan exactly 300 original _missile records; if a record owner at +4
 * equals the requested combat ship and its weapon-ID category is 4,
 * return 1, otherwise return 0. Original return is via EAX.
 */
Moo2V131CombatAmmoStatus moo2_v131_derived_launched_fighter_check(
    const Moo2V131CombatAmmoContext *ctx, int16_t ship_id,
    uint16_t *found)
{
    if (!found || !ctx || !ctx->missile_records ||
        ctx->missile_record_count < MOO2_V131_ORIGINAL_MISSILE_SLOTS)
        return MOO2_V131_COMBAT_AMMO_INVALID_INPUT;
    *found = 0;
    for (size_t i = 0; i < MOO2_V131_ORIGINAL_MISSILE_SLOTS; ++i) {
        const uint8_t *m = ctx->missile_records
                         + i * MOO2_V131_MISSILE_STRIDE;
        if (moo2_v131_ammo_s16(m+4) != ship_id)
            continue;
        int32_t weapon_id = moo2_v131_ammo_s16(m);
        if (!moo2_v131_ammo_valid_weapon(ctx,weapon_id))
            return MOO2_V131_COMBAT_AMMO_INVALID_INPUT;
        if (moo2_v131_ammo_category(ctx,weapon_id) == 4u) {
            *found = 1;
            break;
        }
    }
    return MOO2_V131_COMBAT_AMMO_OK;
}

/*
 * Observed Is_Ship_Out_Of_Ammo_:
 * Return 1 while no qualifying usable attack is found, otherwise 0.
 * Does_Combat_Ship_Have_Special_ for 0x25/0x26 short-circuits to 0.
 * Weapon-category switch from original CODE table 0x194C7:
 * category 0 -> 0x1959A; 1 -> 0x1957C; 2 -> 0x1959A;
 * category 3 -> 0x19585; 4 -> 0x1959E; 5 -> 0x19575.
 */
Moo2V131CombatAmmoStatus moo2_v131_derived_ship_out_of_ammo(
    const Moo2V131CombatAmmoContext *ctx, int16_t ship_id,
    uint16_t *out_of_ammo)
{
    if (!out_of_ammo || !moo2_v131_ammo_valid_ship(ctx,ship_id) ||
        !ctx->has_special || !ctx->weapon_definitions)
        return MOO2_V131_COMBAT_AMMO_INVALID_INPUT;

    /* Original: special 0x25 OR 0x26 means immediate EAX=0. */
    if (ctx->has_special(ctx->special_context,ship_id,0x25u) != 0u ||
        ctx->has_special(ctx->special_context,ship_id,0x26u) != 0u) {
        *out_of_ammo=0;
        return MOO2_V131_COMBAT_AMMO_OK;
    }

    const uint8_t *ship=ctx->combat_ship_records +
        (size_t)ship_id * MOO2_V131_COMBAT_SHIP_STRIDE;
    uint16_t out=1;
    for (unsigned slot=0;slot<MOO2_V131_COMBAT_WEAPON_SLOTS && out; ++slot) {
        const uint8_t *item=ship+0x52u +
                            slot*MOO2_V131_COMBAT_WEAPON_SLOT_STRIDE;
        int32_t weapon_id=moo2_v131_ammo_s16(item);
        if (weapon_id==0 || item[2]==0)
            continue;

        if (!moo2_v131_ammo_valid_weapon(ctx,weapon_id))
            return MOO2_V131_COMBAT_AMMO_INVALID_INPUT;
        uint8_t category=moo2_v131_ammo_category(ctx,weapon_id);
        if (category>5u) continue;

        /* Original CODE +0x19575/7C/85/9A/9E use [item+6]. */
        int32_t stock=moo2_v131_ammo_s16(item+6);
        switch (category) {
        case 0:
        case 2:
            out=0;
            break;
        case 1:
            if (stock>0) out=0;
            break;
        case 3:
            if (stock>0 &&
                (uint16_t)ship[0x20] == ctx->unnamed_comparison_word)
                out=0;
            break;
        case 4:
            if (stock>0) {
                out=0;
            } else {
                uint16_t launched;
                Moo2V131CombatAmmoStatus status =
                    moo2_v131_derived_launched_fighter_check(
                        ctx,ship_id,&launched);
                if (status!=MOO2_V131_COMBAT_AMMO_OK) return status;
                out=(uint16_t)(launched==0u);
            }
            break;
        case 5:
            if (weapon_id!=0x21 || stock>0) out=0;
            break;
        }
    }
    *out_of_ammo=out;
    return MOO2_V131_COMBAT_AMMO_OK;
}
