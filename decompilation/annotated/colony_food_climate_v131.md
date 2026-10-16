# Original v1.31 colony food-production climate correction — complete bounded static audit

## Original evidence

Source baseline: official locally supplied `ORION2.EXE` v1.31, SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. Original Watcom LE CODE object SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`; original initialized LE DATA object SHA-256 `082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b`. These original game bytes are **not** committed to Git.

The named original routine `Colony_Empire_Base_Food2_Produced_` begins in original **CODE** at `0xCE0C6` and has a complete 358-byte body, SHA-256 `705a9348d1b7e97003bd711a8553e114d453b5fbe745b0706c47dffe1de913c2`. Its full original x86 decode, source-byte checkpoints, branch targets and controlled fixtures are reproducibly checked by `tools/audit_colony_food_climate_v131.py`; see `decompilation/reports/colony_food_climate_v131_2026-10-16.json`.

This supplements existing authenticated original base/farmer formulas, source food result-cache contract, and Watcom function-pointer dispatch. It does **not** replace or modify the original raw disassembly `analysis/Colony_Empire_Base_Food2_Produced_.disasm`.

## Crucial CODE/DATA distinction

The climate correction at original CODE `0xCE1AC` and `0xCE1CD` loads a byte from the named original **DATA** `_food_per_farmer_table` at offset `0x581C`, indexed by the colony's climate BYTE `+0xE2`. It does not use the adjacent named **DATA** `_climate_modifier_table` at offset `0x5817`, whose five signed BYTE values are `[0,0,0,-10,-20]`.

The original initialized `_food_per_farmer_table` has **ten** BYTEs:

| Climate index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DATA `0x581C + index` | 0 | 0 | 0 | 1 | 1 | 2 | 2 | 1 | 2 | 3 |

Source DATA bytes SHA-256 `00723b29c9735d5b593affde81837443b627641360d56ca40823caf383978979`.

The original instructions at CODE `0xCE1B3` and `0xCE1D4` read static BYTE addresses `0x5824` and `0x5825`, which are **the last two entries of this same DATA table**. Thus those two reference values are `_food_per_farmer_table[8] == 2` and `_food_per_farmer_table[9] == 3`, respectively. Neither address is in the CODE segment.

## Source-observed gate and exact bounded normal formula

The climate correction is **not universal to all workers**: it occurs only on the source cache-*miss* computation path, after a positive original food base and source-tag check. In CODE `0xCE155–0xCE17A` the original compares signed population tag DI to **8**; only tags **0–7** enter the player path. For such a tag, player BYTE `+0x8A1` is sign-extended to DX, and player BYTE `+0x8AB` must be nonzero to enable the climate branch. Tags **8** and **9** take a separate path adding the original fixed values **6** and **4**, respectively, with no climate adjustment.

Source CODE `0xCE180–0xCE1DB` implements two different climate cases (all comparisons of climate code use unsigned AL):

- **Climate 4 or 6:** `2 * (_food_per_farmer_table[8] - _food_per_farmer_table[climate])`, using the original `MOVZX` loads, `SUB EBX,EAX`, `ADD EBX,EBX`.
- **Climate 5 or 8:** `2 * (_food_per_farmer_table[9] - _food_per_farmer_table[climate])`, using the second original direct reference and the **same subtraction/doubling** instructions.
- **Any other climate byte:** jump directly to source final component accumulation with EBX still zero.

Therefore, with the source-original ten-entry table and the four specifically selected climate cases:

| Climate code | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Climate bonus, when enabled for population tag 0–7 | 0 | 0 | 0 | 0 | **+2** | **+2** | 0 | 0 | **+2** | 0 |

**There is no negative climate adjustment among these source-selected cases**, notwithstanding the fact that the source uses 32-bit `SUB EBX,EAX` rather than an unsigned saturating operation.

For bounded non-overflow inputs after the positive-base gate, a source-observed cache *miss* behaves as:

```c
int population_bonus;
int climate_bonus = 0;
if (tag < 8) {
    population_bonus = (int8_t)player[tag].byte_8A1;
    if (player[tag].byte_8AB != 0) {
        unsigned climate = colony.byte_E2;
        if (climate == 4 || climate == 6)
            climate_bonus = 2 * (food_table[8] - food_table[climate]);
        else if (climate == 5 || climate == 8)
            climate_bonus = 2 * (food_table[9] - food_table[climate]);
    }
} else {
    population_bonus = (tag == 8) ? 6 : 4; // bounded original cache slot 0..9
}
uint16_t result = (uint16_t)(positive_base + population_bonus + climate_bonus);
food_cache[tag] = (uint8_t)result;
```

The cached result is only one **BYTE**; an existing cache hit returns a **signed** BYTE, as independently verified by `tools/audit_colony_empire_base_cache_v131.py`. The initial food base <=0 exits before this entire routine's cache branch, and a non-null breakdown pointer invalidates cache and forces component evaluation. Other climate BYTE values (including 10–255) are routed directly to the zero-modifier path, so they do **not** index beyond the table. The model is deliberately not an uncontrolled native replacement.

### Optional component buffer and state ownership

When the original optional ECX breakdown pointer is non-null, CODE `0xCE1F5–0xCE1FD` stores the signed population-source bonus as a WORD at `+0x04+2*tag` and stores **the climate bonus in EBX as a DWORD at `+0x222`**. This DWORD write occurs even if climate bonus is zero. The later original CODE `0xCE203–0xCE211` adds DX and BX to the local return WORD and writes only its low BYTE into food cache. An already filled breakdown buffer is **not** cleared by this climate subbranch, only the two fields are written; higher-level buffer initialization is a separate procedure's responsibility.

## Confidence and remaining proof obligations

The audit checks original named body SHA, DATA image SHA, table identity and neighboring-table distinction, all climate branch instruction anchors, full contiguous disassembly/branch destinations and **27 bounded synthetic cases**. It establishes a deterministic source-derived v1.31 climate calculation for original unsigned climate BYTE values and bounded population cache-miss input domains. It is **not** a comparison to executing official DOS code, does not prove valid runtime ranges for every original planet/state field, does not test invalid cache indices, and does not establish full game or native remaster equivalence. No overall decompilation percentage is recalculated here.
