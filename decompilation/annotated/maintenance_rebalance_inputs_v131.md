# Original v1.31 maintenance outputs feeding initial home-world worker rebalancing

## Authenticated source

Canonical MicroProse original DOS `ORION2.EXE` v1.31 SHA-256: `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`; original extracted Watcom LE CODE SHA-256: `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. The executable and proprietary game assets are retained locally and not committed.

Source auditor `tools/audit_maintenance_rebalance_inputs_v131.py` and report `decompilation/reports/maintenance_rebalance_inputs_v131_2026-10-16.json` verify all **seven complete original named body hashes** and **780 contiguously decoded x86 instructions**, plus **61 selected exact opcode anchors**, **8 original CALL displacements**, and **8,200 controlled bounded-byte arithmetic assertions**. Source functions:

| Named original procedure | CODE address | Full source bytes |
|---|---|---:|
| `memset_` | `0x119C70` | 24 |
| `Colony_Food_Maintenance_` | `0xCEB4B` | 330 |
| `Colony_Industry_Maintenance_` | `0xCF546` | 297 |
| `Colony_BC_Maintenance_` | `0xD094F` | 197 |
| `Pre_Import_Computing_` | `0xD1D59` | 198 |
| `Twiddle_Initial_Homeworld_` | `0xD55BE` | 530 |
| `Pass_Out_Imports_` | `0xCF8F0` | 1,238 |

`decompilation/game_call_edges.csv` covers game-to-game named calls but omits original Watcom runtime-library `memset_` edges. The three exact calls to `memset_` are verified directly through their source machine-code displacements and authenticated target function hash; game-to-game edges are also checked against the original indexed callgraph.

## Source-dependent reset and maintenance sequence

`Pre_Import_Computing_` first places a pointer to **colony+0xEF** in EAX (`0xD1D63`), count **4** in EBX (`0xD1D5E`), zero byte in EDX (`0xD1D68`), then directly CALLs original named `memset_` at CODE `0xD1D6A`. The `memset_` body at CODE `0x119C70` replicates DL into its 32-bit fill pattern, passes EBX as count through ECX, and CALLs the original lower-level routine at CODE `0x138220`. This establishes reset of **four bytes +0xEF..+0xF2** before producing this pass's maintenance values; the lower-level helper implementation is not separately exhaustively audited here.

Within that **same** `Pre_Import_Computing_` procedure, the original direct CALL order is:

1. `Colony_Industry_Maintenance_` at CODE `0xD1DB7`, which produces BYTE `+0xF0`, followed by `Colony_Industry_Production_` at `0xD1DC0` (result WORD `+0xE9`).
2. `Colony_Food_Production_` at `0xD1DC9` (result WORD `+0xE7`), then `Colony_Food_Maintenance_` at `0xD1DD0` (BYTE `+0xEF`).
3. `Colony_Replicators_` at `0xD1DD7`; then computation of industry cap WORD `+0xF5` from BYTE `+0xF0` and signed industry WORD `+0xE9` at `0xD1DDC–0xD1DF4`.
4. `Colony_Research_Production_` at `0xD1DFF` (result WORD `+0xEB`), additional tax and BC calculations, then `Colony_BC_Maintenance_` at `0xD1E16`, which produces BYTE `+0xF2`.

Other calls interleaved in `Pre_Import_Computing_` are not asserted side-effect-free. The data provenance here is **the exact original source writer and read instruction**.

## Food maintenance BYTE +0xEF

`Colony_Food_Maintenance_` uses original anomaly check `Event_Check_Space_Anomaly_` at CODE `0xCEB6E`. The anomaly branch stores 0 to BYTE `colony+0xEF` at `0xCEB78`.

Otherwise, its source initializes an **8-byte scratch/counter region at colony+0x104** to zero via the original `memset_` CALL at `0xCEB91`. It iterates original colony population entries, aggregating four counter bytes at **colony+0xFC, +0xFD, +0xFE, +0xFF**. It reads those four bytes through original CODE `0xCEC5D`, `0xCEC65`, `0xCEC6F`, `0xCEC79`. After `CWDE; INC EAX; CDQ; SUB EAX,EDX; SAR EAX,1` (for the bounded nonnegative sum of four BYTEs), the source stores **AL** at CODE `0xCEC8A`. The original isolated formula at this stage is:

```text
BYTE colony+0xEF = ( (food_counter_FC + food_counter_FD +
                      food_counter_FE + food_counter_FF + 1) // 2 ) & 0xFF
```

For four source BYTEs the total is at most 1020, so signed 16-bit conversion is safe. The final **store of AL**, however, can truncate a hypothetical result greater than 255; the fixture suite checks that precise byte-width behavior. Actual game-state counter reachability is a separate question.

## Industry maintenance BYTE +0xF0

`Colony_Industry_Maintenance_` similarly checks the original anomaly helper at CODE `0xCF569` and writes 0 to colony BYTE `+0xF0` at `0xCF573` on its anomaly branch.

Otherwise, at CODE `0xCF584–0xCF58C` it clears **8 bytes starting at colony+0x10C** with `memset_`, iterates population entries, and reads four categorized count BYTEs at **colony+0x100, +0x101, +0x102, +0x103** (CODE `0xCF637`, `0xCF63F`, `0xCF653`, `0xCF649`). It performs the same source half-up rounding and writes its result's low BYTE to colony `+0xF0` at CODE `0xCF664`:

```text
BYTE colony+0xF0 = ( (industry_100 + industry_101 +
                      industry_102 + industry_103 + 1) // 2 ) & 0xFF
```

Again, no simulation of the original category-increment body or wider persistent empire state is substituted for real DOS game execution.

## BC BYTE +0xF2 and downstream consumers

`Colony_BC_Maintenance_` initializes or computes colony BYTE `+0xF2`: original CODE `0xD0960` and `0xD0985` store zero on respective branches, and CODE `0xD09F1` writes the computed low byte. It is a separate maintenance output, not automatically a food or industry input.

The source home-world redistribution `Twiddle_Initial_Homeworld_` reads **BYTE colony+0xF0** at `0xD562F` against signed industry WORD `+0xE9`, and **BYTE colony+0xEF** at `0xD5666` against signed food WORD `+0xE7`. `Pass_Out_Imports_` likewise reads BYTE `+0xEF` at CODE `0xCF978`, `0xCFA6A`, `0xCFCE2`. This is a verified machine-code source dependency between maintenance counters, production outputs, import routines, and conditional job reallocations.

## Verification scope and limits

The auditor's 8,200 fixture assertions exercise all 8^4 four-BYTE input combinations from representative values and eight boundary cases, preserving the original half-up rounding, low-byte storage and positive bounded source arithmetic. They **do not** assert that all synthetic counter combinations occur in original colonies.

Unverified: exact legal saved-game maximum counters and category selection; the lower-level `memset_` helper's complete semantics (though the caller and wrapper are original-source authenticated); every additional importer side effect; final home-world job counts under particular valid game states; the original DOS research-display differential and native gameplay parity. No changes to the proprietary executable, native gameplay rules, website or historical unrecalculated 87% whole-executable estimate.
