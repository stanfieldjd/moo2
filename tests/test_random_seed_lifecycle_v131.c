/* Source-derived seed-management regression; not DOS execution.
 * Uses deterministic stand-ins for Check_Release_Version_ and time_(NULL).
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "../decompilation/reconstructed/random_v131.c"
#include "../decompilation/reconstructed/random_seed_lifecycle_v131.c"

typedef struct {
    unsigned preflight_count;
    unsigned time_count;
    uint32_t time_result;
} Fixture;
static void check(int ok){if(!ok){fputs("FAIL seed lifecycle regression\n",stderr);exit(1);}}
static void preflight(void *opaque) {
    Fixture *p=(Fixture *)opaque;p->preflight_count++;
}
static uint32_t timed(void *opaque) {
    Fixture *p=(Fixture *)opaque;p->time_count++;return p->time_result;
}
int main(void) {
    uint32_t seed=0,got=0;
    Fixture fixture={0,0,0x12345678u};
    Moo2V131SeedHooks h={preflight,timed,&fixture};
    check(moo2_v131_derived_set_random_seed(&seed,0xDEADBEEFu)==MOO2_V131_SEED_OK);
    check(moo2_v131_derived_get_random_seed(&seed,&got)==MOO2_V131_SEED_OK);
    check(got==0xDEADBEEFu);
    check(moo2_v131_derived_set_game_random_seed(
        &seed,0xABCDEF01u,&h)==MOO2_V131_SEED_OK);
    check(seed==0xABCDEF01u && fixture.preflight_count==1 && fixture.time_count==0);
    check(moo2_v131_derived_set_game_random_seed(
        &seed,0u,&h)==MOO2_V131_SEED_OK);
    check(seed==0x12345678u && fixture.preflight_count==2 && fixture.time_count==1);
    fixture.time_result=0xA5A5A5A5u;
    check(moo2_v131_derived_randomize_seed(&seed,&h)==MOO2_V131_SEED_OK);
    check(seed==0xA5A5A5A5u && fixture.time_count==2);
    seed=0;
    int32_t result=-99;
    for(int i=0;i<10;i++){
        check(moo2_v131_derived_random_with_restore(
            &seed,100u,&result)==MOO2_V131_SEED_OK);
        check(result==1 && seed==0);
    }
    seed=1;
    check(moo2_v131_derived_random_with_restore(
        &seed,100u,&result)==MOO2_V131_SEED_OK);
    check(result==26 && seed==1);
    seed=0;
    check(moo2_v131_derived_random_with_restore(
        &seed,UINT32_MAX,&result)==MOO2_V131_SEED_OK);
    check(result==12346 && seed==0);
    seed=0x10203040u;
    result=77;
    check(moo2_v131_derived_random_with_restore(
        &seed,0u,&result)==MOO2_V131_SEED_ZERO_BOUND);
    check(seed==0x10203040u && result==77);
    check(moo2_v131_derived_set_random_seed(NULL,10u)==MOO2_V131_SEED_BAD_ARGS);
    check(moo2_v131_derived_get_random_seed(NULL,&got)==MOO2_V131_SEED_BAD_ARGS);
    check(moo2_v131_derived_set_game_random_seed(
        &seed,3u,NULL)==MOO2_V131_SEED_BAD_ARGS);
    puts("PASS: seed get/set, cmd-line override, time path, Random_With_Restore preserve state");
    return 0;
}
