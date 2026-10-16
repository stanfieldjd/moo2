# Source-verified MOO2 v1.31 per-population food, industry and research base-production formulas

## Original machine-code provenance

The canonical official local `ORION2.EXE` v1.31 SHA-256 is `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`. The extracted original Watcom LE CODE SHA-256 is `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. Original binaries/assets are deliberately excluded from the repository.

These routines are **one level below** the three original dispatch-table functions identified in `decompilation/annotated/colony_job_indirect_dispatch_v131.md`; their return values feed the food/industry/research population production computations and are not themselves colony-wide final outputs.

| Original Watcom procedure | Original CODE range | Full original bytes | SHA-256 |
|---|---|---:|---|
| `Colony_Food2_Per_Farmer_` | `0xCE03E–0xCE0C5` | 136 | `6aef5f245db959b949a22eb0cfccd03b65db2c103a18c4dc47f5bbabcf9a04e4` |
| `Colony_Industry_Per_Worker_` | `0xCEC95–0xCED46` | 178 | `1e58a5b42e7d04cbc1d412b55ba007dbee502d5f0c257a96890c93d5689d8aa9` |
| `Colony_Research_Per_Scientist_` | `0xCFDC6–0xCFE76` | 177 | `7d9e54a024e600115cf99d1d299806ceaf74f93c1aa95638a135b97e2efadd14` |

Complete original bodies, 151 decoded machine instructions, 34 direct branch edges, 55 exact opcode anchors, CODE/DATA symbol identity, and 19 controlled fixture checks are reproduced by `tools/audit_colony_empire_base_formulas_v131.py` with machine-readable evidence in `decompilation/reports/colony_empire_base_formulas_v131_2026-10-16.json`. The original named Watcom function extents are also checked against `decompilation/functions.csv`. The original helper bodies are **not** original recovered C source; this is a source-derived algorithmic reconstruction.

## Food: original `Colony_Food2_Per_Farmer_` algorithm

The original function takes a colony pointer, a player/population tag in DX, and an optional breakdown pointer in EBX.

For valid original planet reference and synthetic unsigned planet BYTE `+0x0B`, the base return in EAX is `2 * planet.BYTE_0B` (`0xCE050–0xCE056`). If and **only if** that base is zero and the tag-indexed player BYTE `+0x134` equals 3, replace the base with 2 (`0xCE061–0xCE087`). If the resulting base is still zero, skip the remaining flag modifiers.

For positive base only, colony BYTE `+0x164` nonzero contributes +4 (`0xCE090–0xCE0A0`), and colony BYTE `+0x13A` nonzero contributes +2 (`0xCE0A9–0xCE0B8`). Thus for bounded in-range inputs:

```c
unsigned base = 2 * planet.byte_0B;
if (base == 0 && player[tag].byte_134 == 3) base = 2;
if (base > 0) {
    if (colony.byte_164) base += 4;
    if (colony.byte_13A) base += 2;
}
return base;
```

With optional EBX breakdown output: source writes the initial doubled planet base as DWORD at `+0x00`; if the zero-base fallback fires, source additionally writes WORD 2 at `+0x52`; the +4 source branch writes WORD 4 at `+0x21C`; the +2 branch writes WORD 2 at `+0x1C8`. No other fields are claimed initialized by this function. These writes are conditional on a non-null output pointer.

## Industry: original `Colony_Industry_Per_Worker_` algorithm

The base is the original **CODE** table `_minerals_per_mine[planet.BYTE_0A]` at CODE `0xCD4B5`; authentic five bytes `[1,2,3,5,8]`, SHA-256 `0a834026e5178e5a668be1e368aeb321b6acdd1d651a3eb141541de4531c6c20`.

Original feature flags contribute successively: colony BYTE `+0x13A` gives +1; `+0x13D` gives +1; `+0x15A` gives +2; `+0x142` gives +3; tag-indexed player BYTE `+0x183 == 3` gives +1. The source has separate conditionals at CODE `0xCECBD`, `0xCECD4`, `0xCECEB`, `0xCED03`, `0xCED2A`. For bounded valid mineral indices:

```c
unsigned base = minerals_per_mine[planet.byte_0A];
if (colony.byte_13A) base += 1;
if (colony.byte_13D) base += 1;
if (colony.byte_15A) base += 2;
if (colony.byte_142) base += 3;
if (player[tag].byte_183 == 3) base += 1;
return base;
```

If breakdown EBX is non-null, source writes the original table base as DWORD at `+0x00`, and conditional WORD contributions at `+0x1C8` (1), `+0x1CE` (1), `+0x208` (2), `+0x1D8` (3), and `+0x0F0` (1). The original code does **not** validate planet mineral-table indices; no out-of-bounds behavior is inferred.

## Research: original `Colony_Research_Per_Scientist_` algorithm

The original base is **3** at CODE `0xCFDC7`. Nonzero colony flag BYTEs add `+1` at `+0x13A`, `+2` at `+0x154`, `+3` at `+0x149`, and `+1` at `+0x159`. The owner planet's BYTE `+0x0F` contributes **+2 if value 10** or **+5 if value 11**, with no other contribution for a value outside these two cases (`0xCFE42–0xCFE73`).

```c
unsigned base = 3;
if (colony.byte_13A) base += 1;
if (colony.byte_154) base += 2;
if (colony.byte_149) base += 3;
if (colony.byte_159) base += 1;
if (planet.byte_0F == 10) base += 2;
else if (planet.byte_0F == 11) base += 5;
return base;
```

With optional breakdown output, the initial DWORD at `+0x00` becomes 3; conditional WORD component writes are at `+0x1C8` (1), `+0x1FC` (2), `+0x1E6` (3), and `+0x206` (1). Planet-index-dependent values **add** +2 or +5 to the existing DWORD at breakdown `+0x226`; the original uses `ADD DWORD`, **not** a set/overwrite. This matters when the shared production helper has already populated that accumulator.

## Evidence, limitations and confidence

This checkpoint establishes exact source-observed returns on controlled valid input domains and conditional original buffer writes. The byte-contiguous decoder explicitly reconnects split disassembly continuation rows; all decoded branch destinations are checked against original instruction boundaries, and none of these three named helper bodies has a direct nested CALL.

The model **does not** prove behavior for corrupted colony pointers, invalid planet player tags, or indices outside the original five-byte mineral table. It does **not** execute DOS runtime differential tests, guarantee all state-lifecycle interactions or reconstruct the entirety of the native remaster. The role of all faction/building flags can be given full gameplay names only with independent source evidence. The original workbench's 87% whole-executable estimate is unchanged.
