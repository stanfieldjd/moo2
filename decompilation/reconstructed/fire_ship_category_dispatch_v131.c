/*
 * DERIVED v1.31 Fire_Ship_ category dispatch, not the original source.
 * Authenticated ORION2.EXE:
 * SHA256 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 *
 * Original Fire_Ship_ 0x28B5E, 2216 bytes:
 * 0x28CA4 MOVSX EAX,WORD PTR [ESI] (selected weapon slot)
 * 0x28CA7 IMUL EAX,EAX,0x1C (weapon-definition stride 28)
 * 0x28CAA MOVZX AX,BYTE PTR [EAX+0x780F] (original _weapons+0x0C)
 * 0x28CB2 MOV [EBP-0x14],EAX (later reads as WORD)
 * 0x28F53 CMP WORD PTR [EBP-0x14],5; JA 0x29143
 * 0x28F5E MOVZX EAX,WORD PTR [EBP-0x14]
 * 0x28F62 JMP DWORD PTR CS:[EAX*4+0x28B46]
 *
 * The 6 original case addresses lead to named Fire_Beam_Weapon_,
 * Fire_Missile_, Fire_Bomb_ and Fire_Special_Weapon_.
 * This isolates ONLY the category route selection, not game action/effects.
 * Extra host-side validation is deliberate, not original Watcom behavior.
 */
#include <stddef.h>
#include <stdint.h>

typedef enum {
    MOO2_V131_FIRE_ROUTE_BEAM = 0,
    MOO2_V131_FIRE_ROUTE_MISSILE = 1,
    MOO2_V131_FIRE_ROUTE_BOMB = 2,
    MOO2_V131_FIRE_ROUTE_SPECIAL = 3,
    MOO2_V131_FIRE_ROUTE_NONE_IN_SIX_CASE_TABLE = 4
} Moo2V131FireRoute;

typedef enum {
    MOO2_V131_FIRE_ROUTE_OK = 0,
    MOO2_V131_FIRE_ROUTE_INVALID_INPUT = 1
} Moo2V131FireRouteStatus;

typedef struct {
    uint8_t weapon_category;
    Moo2V131FireRoute path;
    uint8_t replace_counter_after_missile; /* category exactly 2 */
    uint32_t original_code_case_target; /* zero if category exceeds 5 */
} Moo2V131FireCategoryDispatch;

static int32_t moo2_v131_fire_category_s16(const uint8_t *p)
{
    const uint16_t v=(uint16_t)p[0] | (uint16_t)((uint16_t)p[1]<<8);
    return v < UINT16_C(0x8000) ? (int32_t)v : ((int32_t)v-65536);
}

Moo2V131FireRouteStatus moo2_v131_derived_fire_ship_category(
    const uint8_t *combat_ship,size_t ship_size,int16_t slot,
    const uint8_t *weapons,size_t weapon_definition_count,
    Moo2V131FireCategoryDispatch *out)
{
    static const Moo2V131FireRoute routes[]={
        MOO2_V131_FIRE_ROUTE_BEAM,    /* 0x28FD1 */
        MOO2_V131_FIRE_ROUTE_MISSILE, /* 0x28F6A */
        MOO2_V131_FIRE_ROUTE_MISSILE, /* 0x28F6A, category-2 counter rewrite */
        MOO2_V131_FIRE_ROUTE_BOMB,    /* 0x290E2 */
        MOO2_V131_FIRE_ROUTE_MISSILE, /* 0x28F6A */
        MOO2_V131_FIRE_ROUTE_SPECIAL  /* 0x29113 */
    };
    static const uint32_t original_targets[]={
        UINT32_C(0x28FD1),UINT32_C(0x28F6A),UINT32_C(0x28F6A),
        UINT32_C(0x290E2),UINT32_C(0x28F6A),UINT32_C(0x29113)
    };
    if (!combat_ship || !weapons || !out || ship_size<313u ||
        slot<0 || slot>=8)
        return MOO2_V131_FIRE_ROUTE_INVALID_INPUT;

    const uint8_t *item=combat_ship+0x52u+(size_t)slot*11u;
    const int32_t id=moo2_v131_fire_category_s16(item);
    if (id<0 || (size_t)id>=weapon_definition_count)
        return MOO2_V131_FIRE_ROUTE_INVALID_INPUT;

    const uint8_t category=weapons[(size_t)id*28u+12u];
    out->weapon_category=category;
    out->path=category<=5u
        ?routes[category]
        :MOO2_V131_FIRE_ROUTE_NONE_IN_SIX_CASE_TABLE;
    out->replace_counter_after_missile=(uint8_t)(category==2u);
    out->original_code_case_target=category<=5u
        ?original_targets[category]:UINT32_C(0);
    return MOO2_V131_FIRE_ROUTE_OK;
}
