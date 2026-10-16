# Original v1.31 worker-rebalancing input field provenance

## Source identity and audited original bodies

Official locally supplied original MicroProse v1.31 `ORION2.EXE` SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Original Watcom LE CODE SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. The original executable and proprietary assets are used locally for verification only and are not committed.

The reproducible original-source audit `tools/audit_homeworld_rebalance_field_producers_v131.py`, with JSON output `decompilation/reports/homeworld_rebalance_field_producers_v131_2026-10-16.json`, verifies **seven complete named original procedures** (hash, named boundaries and fully contiguous original x86 decode). Together these cover **1,774 original machine instructions**, **54 exact opcode anchors**, **13 original direct CALL sites**, and **4,099 bounded signed-minimum assertions**.

| Original source function | Watcom CODE | Original bytes |
|---|---|---:|
| `Pre_Import_Computing_` | `0xD1D59` | 198 |
| `Pass_Out_Imports_` | `0xCF8F0` | 1,238 |
| `Colony_Food2_Per_Farmer_` | `0xCE03E` | 136 |
| `Colony_Food_Production_` | `0xCE664` | 1,209 |
| `Colony_Industry_Production_` | `0xCEE1B` | 1,789 |
| `Colony_Research_Production_` | `0xCFF74` | 1,103 |
| `Twiddle_Initial_Homeworld_` | `0xD55BE` | 530 |

All source opcode/byte proofs use original CODE memory offsets, not relative DOS file offsets or inferred C labels. The full-body SHA hashes are included in the audit script and JSON report.

## Verified food, industry, research and balancing fields

The previously audited original home-world worker-redistribution routine `Twiddle_Initial_Homeworld_` reads several mutable colony-output fields. This follow-on audit traces their original producers and consumers, without guessing unused field names or assuming side-effect-free calls.

- **Colony BYTE +0xDD:** `Pre_Import_Computing_` CALLs `Colony_Food2_Per_Farmer_` at CODE `0xD1D76`, then writes the returned low BYTE AL to colony `+0xDD` at `0xD1D7B`. Original `Colony_Food_Production_` checks this same BYTE at `0xCE6C9`, and the home-world rebalance tests it at `0xD5659`. Thus it is a calculated food-output factor reused by both routines, not an arbitrary boolean test.
- **Colony WORD +0xE7:** `Colony_Food_Production_` writes the 16-bit food result through original CODE `0xCE676`, `0xCE69D`, `0xCE727`, and `0xCEAE4`. The rebalancer compares that WORD against a zero-extended food BYTE `+0xEF` at CODE `0xD566E`. `Pass_Out_Imports_` reads the same `+0xEF` and `+0xE7` fields at CODE `0xCF978` and `0xCF980` and updates its import balance record `+0xF3` through multiple guarded source pathways.
- **Colony WORD +0xE9:** `Colony_Industry_Production_` writes or adjusts original WORD `+0xE9` at CODE `0xCEE3C`, `0xCEE63`, `0xCF0F0`, `0xCF4A3`, and `0xCF4D9`. The rebalancer reads this same WORD for its first industry comparison (`0xD5637`) and both industry/research balancing conditions (`0xD569D`, `0xD56CB`).
- **Colony WORD +0xEB:** `Colony_Research_Production_` initializes/updates WORD `+0xEB` at CODE `0xCFF86`, `0xCFFAD`, and `0xD0050`. The rebalancer tests it against industry `+0xE9`; the same research value was shown earlier to be recalculated by the on-screen research-production display path.

Original `Pre_Import_Computing_` begins by zeroing four BYTEs at `colony+0xEF..+0xF2` (CODE `0xD1D5E–0xD1D6A`), then invokes the named food-per-farmer function and writes `+0xDD`; it similarly writes BYTE `+0xDE` from `Colony_Industry_Per_Worker_` and BYTE `+0xDF` from `Colony_Research_Per_Scientist_`. It next CALLs original industry production at `0xD1DC0` and food production at `0xD1DC9` (alongside additional intermediate calls), and later CALLs research production at `0xD1DFF` **with EDX explicitly zero**, i.e. no optional reporting buffer.

## Original industry cap WORD +0xF5 and signed comparison

Original `Pre_Import_Computing_` CODE `0xD1DDC` zero-extends colony BYTE `+0xF0` into 16-bit AX. CODE `0xD1DE4` compares it with colony WORD `+0xE9`, and CODE `0xD1DEB` uses **signed JL** to preserve AX when the BYTE value is numerically lower. Otherwise CODE `0xD1DED` loads the original WORD `+0xE9`. CODE `0xD1DF4` stores the chosen 16-bit result into colony WORD `+0xF5`.

Therefore the result is the original signed-16 minimum:

```text
WORD colony+0xF5 = (uint16_t)min((int16_t)(uint8_t)colony[+0xF0],
                               (int16_t)WORD colony[+0xE9])
```

The audit exercises all 256 possible original source BYTE values of `+0xF0` against eight representative 16-bit industry WORDs, including `0xFFFF` (signed -1) and `0x8000` (signed -32768): 4,099 bounded assertions including signed-boundary checks. These tests model the **original verified expression**, not the possible dynamic sources of every field value; the provenance of other calls that can modify `+0xF0` or its aliases remains to be separately resolved.

## Why the source dependency matters

`Twiddle_Initial_Homeworld_` makes repeated direct CALLs to `Pre_Import_Computing_` and `Pass_Out_Imports_` between setting different packed worker jobs. The original functions write or adjust the very food/industry/research fields that drive the next branch. Their effects cannot be replaced by a single frozen snapshot of `+0xE7,+0xE9,+0xEB,+0xDD,+0xEF`. `Pass_Out_Imports_` has full original source-code coverage in this audit, but its wider empire/transport side effects are **not** claimed fully reconstructed as a native gameplay function.

**Verification achieved:** exact original named producer and consumer field linkage, CALL ordering and output-address identity; verified signed/unsigned semantics of the industry limit.

**Still unverified:** a fully valid v1.31 DOS save witness satisfying the earlier research-report-dependent synthetic production difference, exact final home-world job counts under all legal settings, full dynamic DOS parity and finished native remaster. Prior overall 87% estimate remains unrecalculated.
