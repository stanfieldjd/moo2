/*
 * Original Watcom MOO2 v1.31 Colony_Industry_To_Tax_ full 89 bytes
 * at CODE 0xD08F6. Authenticated original ORION2.EXE SHA256:
 * 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f
 * Full body SHA256:
 * 0801f833e5ad497d8d59d069ee8b40e532829f85bedbeeb7ad4d28ca4805cd84
 *
 * EAX=colony record pointer, originally preserves EBX ECX EDX.
 * Original tax basis is signed WORD colony+0xE9 minus unsigned
 * BYTE colony+0xF0 (replicator use).
 * If basis <=0: set WORD colony+0x127=0 and return, WITHOUT
 * changing signed remaining-industry WORD+0xE9.
 * If basis >0: read owner signed BYTE+0; owner player record
 * stride0xEA9, tax fraction unsigned BYTE player+0x31;
 * convert floor((basis*tax)/100) by source signed IDIV,
 * store low WORD colony+0x127, subtract that low WORD from
 * original colony+0xE9 using original modulo16 word arithmetic.
 *
 * Invalid host owner indexes safely rejected. This does not
 * implement other BC/income logic or original DOS differential.
 */
#include <stddef.h>
#include <stdint.h>
#include "colony_industry_to_tax_v131.h"

static int32_t moo2_v131_tax_s16(const uint8_t *p){
    uint16_t b=(uint16_t)(p[0]|((uint16_t)p[1]<<8));
    return b<32768u?(int32_t)b:(int32_t)b-65536;
}
static void moo2_v131_tax_w16(uint8_t *p,int32_t n) {
    uint16_t w=(uint16_t)n;
    p[0]=(uint8_t)w;p[1]=(uint8_t)(w>>8);
}
Moo2V131IndustryTaxStatus moo2_v131_derived_colony_industry_to_tax(
    const Moo2V131IndustryTaxContext *ctx,
    uint8_t *colony,size_t colony_bytes)
{
    if(!ctx || !ctx->players || !colony || colony_bytes<0x169u)
        return MOO2_V131_INDUSTRY_TAX_INVALID;
    int32_t available=moo2_v131_tax_s16(colony+0xE9u);
    int32_t basis=available-(int32_t)colony[0xF0u];
    if(basis<=0) {
        moo2_v131_tax_w16(colony+0x127u,0);
        return MOO2_V131_INDUSTRY_TAX_OK;
    }
    int32_t owner=(int32_t)(int8_t)colony[0u];
    if(owner<0 || (size_t)owner>=ctx->player_count)
        return MOO2_V131_INDUSTRY_TAX_INVALID;
    const uint8_t *player=ctx->players+(size_t)owner*0xEA9u;
    int32_t tax=(int32_t)player[0x31u];
    int32_t amount=(basis*tax)/100;
    moo2_v131_tax_w16(colony+0x127u,amount);
    moo2_v131_tax_w16(colony+0xE9u,available-(int16_t)(uint16_t)amount);
    return MOO2_V131_INDUSTRY_TAX_OK;
}
