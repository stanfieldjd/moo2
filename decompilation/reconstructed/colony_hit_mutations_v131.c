/*
 * ISOLATED v1.31 MOO2 colony-hit state mutations; NOT complete resolvers.
 * Derived from previously authenticated ORION2.EXE v1.31
 * SHA256 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f.
 * Original CODE sites:
 * Resolve_Bomb_Hit_:
 *   0xCD07B DEC WORD colony+0x130; 0xCD082 event+0x41=1;
 *   0xCD086 INC WORD event+0x08
 *   0xCD0CB DEC WORD colony+0x132; 0xCD0D2 event+0x41=1;
 *   0xCD0D6 INC WORD event+0x0A
 *   0xCD0EC/0xCD0F3 transfer WORD colony+0x125 -> event+0x43;
 *   0xCD0F7 clear WORD colony+0x125; 0xCD135 event+0x41=1
 * Resolve_Biological_Hit_:
 *   0xCD18B event+0x41=1 on selected-hit paths
 *   0xCD217 DEC colony WORD+0x130; 0xCD21E INC event WORD+0x08
 *   0xCD227 DEC colony WORD+0x132; 0xCD22E INC event WORD+0x0A
 *   0xCD1B9/0xCD1BD INC event WORDs +0x0C/+0x3F;
 *   0xCD1C1 DEC population BYTE+0x0A;
 *   0xCD1CB/0xCD1CF overwrite selected DWORD with last entry DWORD
 *   0xCD2E4 SUB colony defense WORD+0xB4+2*index, 100.
 *
 * Only these writes are modeled. The caller must already have selected
 * the ORIGINAL source branch: this does not autonomously resolve hits.
 * Player statistics, building effects, other colony/global modifications,
 * original RNG and all unreconstructed side effects are omitted.
 * Host buffer validation is an intentional non-DOS safety difference.
 */
#include <stddef.h>
#include <stdint.h>
typedef enum {
    MOO2_V131_HIT_WRITE_OK=0,MOO2_V131_HIT_WRITE_INVALID=1
} Moo2V131HitWriteStatus;
typedef enum {
    MOO2_V131_BOMB_WRITE_POP_130=1,
    MOO2_V131_BOMB_WRITE_POP_132=2,
    MOO2_V131_BOMB_WRITE_STATUS_125=3
} Moo2V131BombWrite;
typedef enum {
    MOO2_V131_BIO_WRITE_POP_130=1,
    MOO2_V131_BIO_WRITE_POP_132=2,
    MOO2_V131_BIO_WRITE_REMOVE_ENTRY=3,
    MOO2_V131_BIO_WRITE_REDUCE_DEFENSE_100=4
} Moo2V131BioWrite;
static uint16_t moo2_v131_hit_read16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8));
}
static void moo2_v131_hit_write16(uint8_t *p,uint16_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);
}
static void moo2_v131_hit_incr16(uint8_t *p) {
    moo2_v131_hit_write16(p,(uint16_t)(moo2_v131_hit_read16(p)+1u));
}
static void moo2_v131_hit_decr16(uint8_t *p) {
    moo2_v131_hit_write16(p,(uint16_t)(moo2_v131_hit_read16(p)-1u));
}
Moo2V131HitWriteStatus moo2_v131_derived_bomb_hit_write(
    uint8_t *colony,size_t colony_bytes,
    uint8_t *event,size_t event_bytes,Moo2V131BombWrite operation)
{
    if(!colony || !event || colony_bytes<0x169u || event_bytes<0x45u)
        return MOO2_V131_HIT_WRITE_INVALID;
    switch(operation) {
        case MOO2_V131_BOMB_WRITE_POP_130:
            moo2_v131_hit_decr16(colony+0x130u);
            event[0x41u]=1u;
            moo2_v131_hit_incr16(event+0x08u);
            return MOO2_V131_HIT_WRITE_OK;
        case MOO2_V131_BOMB_WRITE_POP_132:
            moo2_v131_hit_decr16(colony+0x132u);
            event[0x41u]=1u;
            moo2_v131_hit_incr16(event+0x0Au);
            return MOO2_V131_HIT_WRITE_OK;
        case MOO2_V131_BOMB_WRITE_STATUS_125:
            moo2_v131_hit_write16(event+0x43u,
                                  moo2_v131_hit_read16(colony+0x125u));
            moo2_v131_hit_write16(colony+0x125u,0u);
            event[0x41u]=1u;
            return MOO2_V131_HIT_WRITE_OK;
        default:
            return MOO2_V131_HIT_WRITE_INVALID;
    }
}
Moo2V131HitWriteStatus moo2_v131_derived_bio_hit_write(
    uint8_t *colony,size_t colony_bytes,
    uint8_t *event,size_t event_bytes,Moo2V131BioWrite operation,
    unsigned selected_entry,unsigned defense_index,int set_prior_hit_flag)
{
    if(!colony || !event || colony_bytes<0x169u || event_bytes<0x45u)
        return MOO2_V131_HIT_WRITE_INVALID;
    if(operation!=MOO2_V131_BIO_WRITE_POP_130 &&
       operation!=MOO2_V131_BIO_WRITE_POP_132 &&
       operation!=MOO2_V131_BIO_WRITE_REMOVE_ENTRY &&
       operation!=MOO2_V131_BIO_WRITE_REDUCE_DEFENSE_100)
        return MOO2_V131_HIT_WRITE_INVALID;
    if(operation==MOO2_V131_BIO_WRITE_REMOVE_ENTRY) {
        const unsigned count=colony[0x0Au];
        if(count==0u || selected_entry>=count ||
           0x0Cu+4u*(size_t)count>colony_bytes)
            return MOO2_V131_HIT_WRITE_INVALID;
    }
    if(operation==MOO2_V131_BIO_WRITE_REDUCE_DEFENSE_100) {
        if(defense_index>=16u || 0xB4u+2u*(size_t)defense_index+2u>colony_bytes)
            return MOO2_V131_HIT_WRITE_INVALID;
        /* Original entry to 0xCD2E4 guarded by signed WORD >100. */
        uint16_t bits=moo2_v131_hit_read16(colony+0xB4u+2u*defense_index);
        if(bits<=100u || bits>=0x8000u)
            return MOO2_V131_HIT_WRITE_INVALID;
    }
    if(set_prior_hit_flag)event[0x41u]=1u;
    switch(operation) {
        case MOO2_V131_BIO_WRITE_POP_130:
            moo2_v131_hit_decr16(colony+0x130u);
            moo2_v131_hit_incr16(event+0x08u);
            return MOO2_V131_HIT_WRITE_OK;
        case MOO2_V131_BIO_WRITE_POP_132:
            moo2_v131_hit_decr16(colony+0x132u);
            moo2_v131_hit_incr16(event+0x0Au);
            return MOO2_V131_HIT_WRITE_OK;
        case MOO2_V131_BIO_WRITE_REMOVE_ENTRY: {
            const unsigned count=colony[0x0Au];
            const size_t to=0x0Cu+4u*(size_t)selected_entry;
            const size_t from=0x0Cu+4u*(size_t)(count-1u);
            moo2_v131_hit_incr16(event+0x0Cu);
            moo2_v131_hit_incr16(event+0x3Fu);
            colony[0x0Au]=(uint8_t)(count-1u);
            for(unsigned i=0;i<4u;i++)colony[to+i]=colony[from+i];
            /* Original subsequent player-statistics write omitted. */
            return MOO2_V131_HIT_WRITE_OK;
        }
        case MOO2_V131_BIO_WRITE_REDUCE_DEFENSE_100: {
            uint8_t *ptr=colony+0xB4u+2u*(size_t)defense_index;
            moo2_v131_hit_write16(ptr,
                                  (uint16_t)(moo2_v131_hit_read16(ptr)-100u));
            return MOO2_V131_HIT_WRITE_OK;
        }
        default:
            return MOO2_V131_HIT_WRITE_INVALID;
    }
}
