/*
 * Exhaustive signed source and original WORD-wrap tests for full
 * 89-byte v1.31 Colony_Industry_To_Tax_. Differential to known
 * original x86 arithmetic, not runtime DOS execution.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../decompilation/reconstructed/colony_industry_to_tax_v131.c"
static void must(int yes){
    if(!yes){fputs("FAIL original industry-to-tax source\n",stderr);exit(1);}
}
static void w16(uint8_t *p,int32_t v){
    uint16_t n=(uint16_t)v;p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);
}
static uint16_t r16(const uint8_t *p){
    return (uint16_t)(p[0]|((uint16_t)p[1]<<8));
}
int main(void){
    uint8_t colony[0x169u]={0},players[8u*0xEA9u]={0};
    Moo2V131IndustryTaxContext ctx={players,8u};
    unsigned cases=0u;
    const int amounts[]={-32768,-300,-1,0,1,3,100,254,255,256,
        500,999,4096,20000,32767};
    const unsigned rates[]={0,1,15,25,50,75,100,150,200,255};
    for(unsigned owner=0;owner<8u;owner++)
    for(unsigned a=0;a<sizeof(amounts)/sizeof(amounts[0]);a++)
    for(unsigned usage=0;usage<256u;usage+=17u)
    for(unsigned r=0;r<sizeof(rates)/sizeof(rates[0]);r++){
        memset(colony,0,sizeof(colony));
        colony[0]=(uint8_t)owner;
        w16(colony+0xE9u,amounts[a]);
        colony[0xF0u]=(uint8_t)usage;
        w16(colony+0x127u,0xBEEF);
        players[(size_t)owner*0xEA9u+0x31u]=(uint8_t)rates[r];
        int32_t basis=amounts[a]-(int32_t)usage;
        int32_t expect=basis>0?basis*(int32_t)rates[r]/100:0;
        must(moo2_v131_derived_colony_industry_to_tax(
             &ctx,colony,sizeof(colony))==MOO2_V131_INDUSTRY_TAX_OK);
        must(r16(colony+0x127u)==(uint16_t)expect);
        uint16_t remaining=(uint16_t)amounts[a];
        if(basis>0)remaining=(uint16_t)(remaining-(uint16_t)expect);
        must(r16(colony+0xE9u)==remaining);
        must(colony[0xF0u]==(uint8_t)usage);
        cases++;
    }
    /* Source nonpositive tax base never accesses owner/player. */
    colony[0]=255u;w16(colony+0xE9u,0);colony[0xF0u]=255u;
    must(moo2_v131_derived_colony_industry_to_tax(
        &ctx,colony,sizeof(colony))==MOO2_V131_INDUSTRY_TAX_OK);
    /* With positive tax base, source owner must be valid host player. */
    w16(colony+0xE9u,5);colony[0xF0u]=0u;
    must(moo2_v131_derived_colony_industry_to_tax(
        &ctx,colony,sizeof(colony))==MOO2_V131_INDUSTRY_TAX_INVALID);
    printf("PASS %u original industry/replicator/owner/tax combinations with exact signed division and 16-bit state\n",cases);
}
