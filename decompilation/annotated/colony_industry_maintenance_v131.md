# Colony_Industry_Maintenance_ — MOO2 v1.31 source-verified reconstruction

## Provenance and boundaries

- Canonical executable: official local `ORION2.EXE` v1.31, SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
- Original Watcom LE CODE object SHA-256: `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`.
- Complete original named body: CODE `0xCF546–0xCF66E`, 297 bytes, SHA-256 `a3d24386fbaa9dfe229d88dcb34c2c661f3dc2169cdec44481c558542e0fb0ed`.
- Direct callee: `Event_Check_Space_Anomaly_`, CODE `0x1341E`, 80 bytes, SHA-256 `dd82062b1a3404b5917ee04dceea3459291b8f96f1fda2b0b9ded5e7041932b4`.
- Symbol sources: `decompilation/functions.csv`, `decompilation/symbols.csv`. Regenerate verification with `tools/audit_colony_industry_maintenance_v131.py`.
- The complete analyzed named body ends in a branch to a **shared tail** at CODE `0xD1F97`. That tail is verified separately, not incorrectly included in the contiguous 297-byte named extent.

## Reconstructed machine-observed algorithm

The example below is an annotated algorithm, not source code recovered from MicroProse. The names `category` and `player_flag` are neutral placeholders: gameplay semantics of these bytes are **not verified**.

```c
void Colony_Industry_Maintenance_(Colony *c) {
    int16_t owner = (int8_t)c->byte_00;
    int32_t colony_index = ((char *)c - *_colony) / 0x169;

    if (Event_Check_Space_Anomaly_((int16_t)colony_index)) {
        c->byte_F0 = 0;
        return;  // +0x100..+0x103 and +0x10C..+0x113 are NOT cleared here
    }

    c->category_100 = 0;
    c->category_101 = 0;
    c->category_102 = 0;
    c->category_103 = 0;
    memset(c->per_player_10C, 0, 8);

    for (int i = 0; i < (uint8_t)c->byte_0A; ++i) {
        uint32_t value = c->dword_0C[i];
        unsigned tag = value & 15;
        unsigned bit10 = (value >> 10) & 1;

        if (tag < 8) {
            uint8_t counted = (_player[tag].byte_8B0 != 0) ? 1 : 0;
            if (tag == owner)
                c->category_100 += counted;
            else if (bit10)
                c->category_103 += counted;
            else
                c->category_102 += counted;
            c->per_player_10C[tag] += counted;
        } else if (tag == 8) {
            c->category_101 += 2;
        }
        // Values 9..15 contribute nothing in the observed loop.
    }

    int32_t n = (uint8_t)c->category_100
              + (uint8_t)c->category_101
              + (uint8_t)c->category_103
              + (uint8_t)c->category_102;
    c->byte_F0 = (uint8_t)((n + 1) / 2);
}
```

The source uses BYTE additions with potential modulo-256 wrap, then sign-extension and signed arithmetic to produce the final low BYTE. The simplified `(n+1)/2` form is valid for the verified nonnegative, non-overflowing counter domain. It does not establish allowable original game-state ranges.

## Source offsets and side effects

- `0xCF551–0xCF569`: sign-extend colony owner BYTE, derive colony index using DATA global `_colony` and record size `0x169`, call `Event_Check_Space_Anomaly_`.
- `0xCF56E–0xCF57A`: on nonzero return, set BYTE `+0xF0` to zero and jump immediately to the common epilogue **without clearing any other fields**.
- `0xCF57F–0xCF5B2`: call `memset_` with eight bytes at `+0x10C`; clear the four independent category BYTE fields `+0x100`, `+0x101`, `+0x102`, `+0x103`; set loop index to zero.
- `0xCF5B7–0xCF5CC`: read consecutive DWORD entries beginning at `+0x0C`, with stride four; low nibble gives tag `0..15`, original shifts `SHL 21; SHR 31` extract bit 10, and compare tag to 8.
- `0xCF5D2–0xCF61D`: tags 0..7 index DATA global `_player` with Watcom record stride `0xEA9`; count one only if byte `+0x8B0` in that player's record is nonzero. Update one category BYTE and the per-player array BYTE at `+0x10C+tag`.
- `0xCF61F–0xCF626`: tag exactly 8 adds two to BYTE `+0x101`, independent of the player flag test. Tags 9..15 do not enter either category.
- `0xCF62C–0xCF635`: iterate while 16-bit loop index is less than zero-extended unsigned BYTE `+0x0A`.
- `0xCF637–0xCF66A`: zero-extend and sum four category BYTEs, round upward by half for nonnegative counters, store low BYTE at `+0xF0`, jump to shared return CODE `0xD1F97`.

## Unknowns and acceptance boundary

The observed code does not identify the gameplay meaning of `_player[tag].byte_8B0`, the four separate category fields, or the source format and valid length of the DWORD list without additional cross-references. These remain unresolved rather than being named as established gameplay facts.

This reconstruction is **static**, with a complete original named-body digest, exact opcode anchors, original symbol-address checks and controlled arithmetic fixtures. No original DOS runtime differential check or native remaster equivalence is claimed. No game executable or proprietary assets are included in the repository.
