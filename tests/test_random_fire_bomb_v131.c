/* Original-source-derived integration: v1.31 Random_ -> Fire_Bomb_.
 * Only Apply_Damage_To_Planet_ is a stubbed effect callback.
 * No original DOS dynamic execution or copyrighted assets.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/random_v131.c"
#include "../decompilation/reconstructed/fire_bomb_v131.c"

typedef struct {
    uint32_t seed;
    unsigned rolls;
    unsigned applies;
    int16_t required_type;
    int32_t adjustment;
} CallbackContext;
static void require(int p){if(!p){fputs("FAIL source-derived bomb RNG integration\n",stderr);exit(1);}}
static void wr16(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static uint16_t source_rng100(void *opaque) {
    CallbackContext *s=(CallbackContext *)opaque;
    uint32_t r=0;
    require(moo2_v131_derived_random(&s->seed,100u,&r)==MOO2_V131_RANDOM_OK);
    require(r>=1u && r<=100u);
    s->rolls++;
    return (uint16_t)r;
}
static void apply_damage(void *opaque,int32_t *damage,int16_t effect) {
    CallbackContext *s=(CallbackContext *)opaque;
    require(effect==s->required_type);
    s->applies++;
    *damage+=s->adjustment;
}
int main(void) {
    uint8_t ships[313]={0};
    uint8_t definitions[16*28]={0};
    uint8_t bonus[16*2]={0};
    const int slot=3,weapon_id=9;
    CallbackContext callback={0,0,0,7,2};
    Moo2V131BombContext ctx={
        ships,1,definitions,16,bonus,16,source_rng100,apply_damage,&callback
    };
    ships[0x20]=2;
    wr16(bonus+2u*2u,150);
    uint8_t *item=ships+0x52u+(size_t)slot*11u;
    wr16(item,weapon_id);item[9]=3;
    uint8_t *weapon=definitions+weapon_id*28u;
    wr16(weapon+0x12,7);
    wr16(weapon+0x14,10);
    wr16(weapon+0x16,30);
    uint32_t result=0;
    require(moo2_v131_derived_fire_bomb(&ctx,0,slot,&result)==MOO2_V131_BOMB_OK);
    /* Original Random_(100) from seed zero: outputs 1,83,66.
       Min15, Max45, spread30; damage before callback 15,39,34.
       Callback adds +2 each -> 17+41+36 = 94. */
    require(result==94u);
    require(callback.seed==2802067423u && callback.rolls==3 && callback.applies==3);

    /* Identical seed and data must produce identical output and final state. */
    callback.seed=0;callback.rolls=callback.applies=0;
    require(moo2_v131_derived_fire_bomb(&ctx,0,slot,&result)==MOO2_V131_BOMB_OK);
    require(result==94u && callback.seed==2802067423u);

    /* No firing-count iterations must not advance the original seed. */
    item[9]=0;
    callback.seed=0x12345678u;callback.rolls=callback.applies=0;
    require(moo2_v131_derived_fire_bomb(&ctx,0,slot,&result)==MOO2_V131_BOMB_OK);
    require(result==0u && callback.seed==0x12345678u);
    require(callback.rolls==0 && callback.applies==0);

    puts("PASS: exact original v1.31 seed-driven Random_(100) feeds bomb loop and preserves RNG state");
    return 0;
}
