# Colony_Food_Maintenance_ — authenticated v1.31 machine-code reconstruction

## Evidence, identity, scope

- Primary source: official locally supplied `ORION2.EXE` v1.31, SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. The executable is **not** committed.
- Decoded Watcom LE CODE image, SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`; the derived binary is **not** committed.
- Complete named original body `Colony_Food_Maintenance_`: CODE `0xCEB4B..0xCEC94` inclusive (330 bytes), SHA-256 `005961c516ea2f30e4534b7e7c5eb4ede279dc9c53d89a49fd2f5214b5f84030`. Named extent verified against `decompilation/functions.csv`.
- Complete original callee `Event_Check_Space_Anomaly_`: CODE `0x1341E`, 80 bytes, SHA-256 `dd82062b1a3404b5917ee04dceea3459291b8f96f1fda2b0b9ded5e7041932b4`. The shared epilogue is located at `0xD1F97` **outside** the 330-byte named body.
- Named global DATA pointers `_colony` at `0x1AB18` and `_player` at `0x1FF98`; verified with original `decompilation/symbols.csv`. Note that Watcom CODE and DATA address spaces are distinct.
- Deterministic audit `tools/audit_colony_food_maintenance_v131.py`, JSON report `decompilation/reports/colony_food_maintenance_v131_2026-10-16.json`.

## Machine-observed control flow

This pseudocode is a read-only **analyst reconstruction** of the original machine instructions, not an original MicroProse source file, and not a DOS runtime equivalence claim. Uninterpreted field names intentionally avoid inventing gameplay meanings.

```c
// Source uses Watcom registers; this is a simplified structural depiction.
void Colony_Food_Maintenance_(Colony *colony) {
    int16_t owner = (int8_t)colony->byte_00;
    int16_t colony_number = (int16_t)(((char *)colony - *_colony) / 0x169);

    if (Event_Check_Space_Anomaly_(colony_number)) {
        colony->byte_EF = 0;
        return;  // counter bytes remain unchanged
    }

    memset(colony->bytes_104, 0, 8);
    colony->byte_FC = 0;
    colony->byte_FF = 0;
    colony->byte_FE = 0;
    colony->byte_FD = 0;

    for (int i = 0; i < (uint8_t)colony->byte_0A; ++i) {
        uint32_t entry = colony->dword_0C[i];
        int tag = entry & 0xF;
        int bit10 = (entry >> 10) & 1;
        if (tag < 8) {
            int value;
            if (_player[tag].byte_8B0 != 0)
                value = 1;
            else if (_player[tag].byte_8B1 != 0)
                value = 0;
            else
                value = 2;

            if (tag == owner)
                colony->byte_FC += value;
            else if (bit10)
                colony->byte_FE += value;
            else
                colony->byte_FD += value;
            colony->bytes_104[tag] += value;
        } else if (tag == 9) {
            colony->byte_FF += 2;
        }
        // Tags 8 and 10..15 have no increment in this observed loop.
    }

    // Four counters are BYTE fields, so each increment wraps modulo 256.
    int total = (uint8_t)colony->byte_FC
              + (uint8_t)colony->byte_FF
              + (uint8_t)colony->byte_FE
              + (uint8_t)colony->byte_FD;
    colony->byte_EF = (uint8_t)((total + 1) / 2);
}
```

The sum from four zero-extended counters is between 0 and 1020, so the positive-domain ceiling formula here is faithful to the observed `CWDE; INC EAX; CDQ; SUB EAX,EDX; SAR EAX,1` arithmetic when the named routine reaches the normal exit. This does **not** establish that the memory layout is always valid for arbitrary corrupt or unexpected inputs.

## Original instruction checkpoints

- `0xCEB56..0xCEB6E`: sign-extend the owner BYTE, subtract the DATA global `_colony` base, divide by stride `0x169` with signed `IDIV`, pass AX index to `Event_Check_Space_Anomaly_`.
- `0xCEB73..0xCEB7F`: a nonzero anomaly predicate sets `+0xEF` to zero and takes the shared tail **without clearing** the counter bytes.
- `0xCEB84..0xCEBB7`: zero exactly 8 bytes at `+0x104` using `memset_` at CODE `0x119C70`; separately clear `+0xFC`, `+0xFF`, `+0xFE`, `+0xFD`.
- `0xCEBBC..0xCEBD5`: read 4-byte records starting at colony `+0x0C` with DWORD stride; isolate low nibble `entry & 0xF` and bit 10 `(entry >> 10) & 1`; take player path for tags 0..7.
- `0xCEBDB..0xCEC09`: look up DATA `_player` using stride `0xEA9`. For a player tag, flag BYTE `+0x8B0` nonzero yields 1; otherwise `+0x8B1` nonzero yields 0; otherwise yields 2. Prioritized first-flag check cannot be reversed.
- `0xCEC0E..0xCEC34`: compare the 16-bit entry tag against signed owner BYTE. Increment `+0xFC` for ownership equality, `+0xFE` for nonowner with bit 10 set, or `+0xFD` otherwise, and always update tag-indexed byte at `+0x104`.
- `0xCEC3D..0xCEC48`: among tags 8..15, only tag **9** increments `+0xFF` by **two**.
- `0xCEC4E..0xCEC57`: loop with 16-bit index against zero-extended count BYTE at colony `+0x0A`.
- `0xCEC5D..0xCEC90`: sum four zero-extended BYTE category counters and round upward by half for nonnegative totals; store low result BYTE to `+0xEF`, jump to common epilogue `0xD1F97`.
- `0xD1F97..0xD1F9D`: return tail is `leave; pop edi; pop esi; pop edx; pop ecx; pop ebx; ret`.

## Verification and limitations

The audit checks the complete original 330-byte body, 80-byte event callee, source hashes, original Watcom symbol identities, 73 exact instruction anchors, and ten synthetic input fixtures covering owner/nonowner, both flag paths, bit 10, tags 8/9/10..15, BYTE wrap and anomaly short-circuit state preservation. The fixture model is useful for regression of this **static decoding**, not proof of full native-game behavior.

The internal meaning of player flags at `+0x8B0` and `+0x8B1`, the 4-byte entries, categories, and permissible runtime memory bounds is unverified. No executable game, asset, engine, or DOS runtime dynamic differential result is produced.

This function directly corresponds to the named `Colony_Food_Maintenance_` call site at CODE `0xD1DD0` in the authenticated `Pre_Import_Computing_` audit. The separate `Colony_Industry_Maintenance_` and `Colony_BC_Maintenance_` audits establish similar *but not identical* loops and must not be substituted for this source's actual decision tree.
