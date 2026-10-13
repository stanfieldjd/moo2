/* Source-derived original MOO2 v1.31 biological threshold + seeded RNG.
 * This verifies the probability gate only; no colony or biological damage
 * effect is simulated, and no original DOS binary is executed.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "../decompilation/reconstructed/random_v131.c"
#include "../decompilation/reconstructed/planet_bio_threshold_v131.c"

static void ensure(int v){if(!v){fputs("FAIL original biological RNG gate\n",stderr);exit(1);}}

int main(void)
{
    uint32_t seed=0,random=0;
    const uint32_t expected_rolls[]={1u,83u,66u};
    const uint32_t expected_seeds[]={12345u,3554416254u,2802067423u};
    for(int i=0;i<3;i++) {
        uint16_t chance=100u; /* Original biological candidate WORD. */
        ensure(moo2_v131_derived_bio_threshold_adjust(&chance,3u,0u)
               ==MOO2_V131_BIO_THRESHOLD_OK);
        ensure(chance==50u);
        ensure(moo2_v131_derived_random(&seed,100u,&random)
               ==MOO2_V131_RANDOM_OK);
        ensure(random==expected_rolls[i] && seed==expected_seeds[i]);
        ensure(moo2_v131_derived_bio_roll_passes(chance,random)==(i==0));
    }
    /* Second player byte => quarter threshold; first takes precedence
       if both are exactly 3. */
    seed=0;
    uint16_t chance=100u;
    ensure(moo2_v131_derived_bio_threshold_adjust(&chance,0u,3u)
           ==MOO2_V131_BIO_THRESHOLD_OK);
    ensure(chance==25u);
    ensure(moo2_v131_derived_random(&seed,100u,&random)
           ==MOO2_V131_RANDOM_OK);
    ensure(random==1u && moo2_v131_derived_bio_roll_passes(chance,random));

    chance=100u;
    ensure(moo2_v131_derived_bio_threshold_adjust(&chance,3u,3u)
           ==MOO2_V131_BIO_THRESHOLD_OK);
    ensure(chance==50u);
    puts("PASS: seeded original Random_(100) integrates with biological threshold and branch precedence");
    return 0;
}
