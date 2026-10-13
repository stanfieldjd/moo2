/* Test derived, callback-bounded original MOO2 v1.31 Fire_Bomb_.
 * Does not establish DOS random generator or actual planet damage effects.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "../decompilation/reconstructed/fire_bomb_v131.c"

typedef struct {
    uint8_t *shot_count_byte;
    int set_shots_to;
    int random_index;
    int apply_calls;
    int random_calls;
    int16_t observed_effect;
    int16_t random_seq[3];
    int32_t apply_adjust;
} TestCallbacks;
static void require(int p){if(!p){fputs("FAIL derived Fire_Bomb case\n",stderr);exit(1);}}
static void le16(uint8_t *ptr,uint16_t v){ptr[0]=(uint8_t)v;ptr[1]=(uint8_t)(v>>8);}
static uint16_t random100(void *opaque) {
    TestCallbacks *t=(TestCallbacks *)opaque;
    uint16_t value=(uint16_t)t->random_seq[t->random_index++%3];
    t->random_calls++;
    return value;
}
static void apply(void *opaque,int32_t *damage,int16_t effect) {
    TestCallbacks *t=(TestCallbacks *)opaque;
    require(effect==t->observed_effect);
    t->apply_calls++;
    *damage+=t->apply_adjust;
    if(t->set_shots_to>=0 && t->apply_calls==1 && t->shot_count_byte)
        *t->shot_count_byte=(uint8_t)t->set_shots_to;
}

int main(void){
    uint8_t ship[2*313]={0};
    uint8_t weapons[32*28]={0};
    uint8_t ordnance[256*2]={0};
    TestCallbacks callbacks={
        NULL,-1,0,0,0,7,{0,50,99},2
    };
    Moo2V131BombContext ctx={
       ship,2,weapons,32,ordnance,256,random100,apply,&callbacks
    };
    /* Ship #1, owner index 3, weapon slot #4 -> weapon definition ID 9. */
    uint8_t *p=ship+313; p[0x20]=3;
    const unsigned slot=4;
    uint8_t *item=p+0x52u+slot*11u;
    callbacks.shot_count_byte=item+9;
    le16(item,9);
    le16(ordnance+3*2,150);
    uint8_t *def=weapons+9*28;
    le16(def+0x12,7); /* passed as signed effect callback argument */
    le16(def+0x14,10);
    le16(def+0x16,30);
    uint32_t output=999;

    item[9]=3;
    require(moo2_v131_derived_fire_bomb(&ctx,1,(int16_t)slot,&output)==MOO2_V131_BOMB_OK);
    /* Scaled min15, scaled max45, spread30.
       Random 0/50/99 -> 15/30/44 then apply adds +2 => 17+32+46=95 */
    require(output==95 && callbacks.random_calls==3 && callbacks.apply_calls==3);

    /* Exhaustive low-byte firing count 0..255 with deterministic rolls. */
    callbacks.random_seq[0]=0;
    callbacks.random_seq[1]=0;
    callbacks.random_seq[2]=0;
    for(unsigned n=0;n<256;n++) {
        item[9]=(uint8_t)n;
        callbacks.random_index=callbacks.apply_calls=callbacks.random_calls=0;
        output=0xa5a5a5a5u;
        require(moo2_v131_derived_fire_bomb(&ctx,1,(int16_t)slot,&output)==MOO2_V131_BOMB_OK);
        require(output==n*17u);
        require((unsigned)callbacks.random_calls==n);
        require((unsigned)callbacks.apply_calls==n);
    }

    /* The original re-reads the count byte after each planet callback. */
    item[9]=20;
    callbacks.set_shots_to=2;
    callbacks.random_index=callbacks.apply_calls=callbacks.random_calls=0;
    require(moo2_v131_derived_fire_bomb(&ctx,1,(int16_t)slot,&output)==MOO2_V131_BOMB_OK);
    require(output==34 && callbacks.apply_calls==2 && item[9]==2);
    callbacks.set_shots_to=-1;

    /* For negative original WORDs the division truncates toward zero. */
    le16(def+0x14,(uint16_t)-20);
    le16(def+0x16,(uint16_t)-10);
    callbacks.random_index=callbacks.apply_calls=callbacks.random_calls=0;
    item[9]=1;
    require(moo2_v131_derived_fire_bomb(&ctx,1,(int16_t)slot,&output)==MOO2_V131_BOMB_OK);
    /* ordnance bonus 150%; minimum -30, apply +2 -> -28 modulo 2^32. */
    require(output==(uint32_t)-28 && callbacks.apply_calls==1);

    /* Validate original-format host pointer/index guards. */
    require(moo2_v131_derived_fire_bomb(&ctx,-1,0,&output)==MOO2_V131_BOMB_INVALID_INPUT);
    require(moo2_v131_derived_fire_bomb(&ctx,2,0,&output)==MOO2_V131_BOMB_INVALID_INPUT);
    require(moo2_v131_derived_fire_bomb(&ctx,0,8,&output)==MOO2_V131_BOMB_INVALID_INPUT);
    le16(item,0xffffu);
    require(moo2_v131_derived_fire_bomb(&ctx,1,(int16_t)slot,&output)==MOO2_V131_BOMB_INVALID_INPUT);
    le16(item,9);
    ctx.ordnance_bonus_count=2;
    require(moo2_v131_derived_fire_bomb(&ctx,1,(int16_t)slot,&output)==MOO2_V131_BOMB_INVALID_INPUT);

    puts("PASS: derived Fire_Bomb arithmetic, 256 firing counts, callback effects and host bounds");
    return 0;
}
