# Official v1.31 colony yields: original-byte and REA evidence

## Investigation question

What original instructions and data underpin food-per-farmer, industry-per-worker, and research-per-scientist calculations in official *Master of Orion II* v1.31?

This is **static reverse-engineering evidence**, not an assertion that a native implementation already reproduces gameplay. No game binary, compiled image, or large machine-code excerpt is committed here.

## Sources, reproducibility, and level of confidence

- Canonical original `ORION2.EXE`: SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
- REA 6.4.0 directly connected to ChatGPT; Ghidra 12.1.4 loaded a bounded 32-bit x86 ELF synthetic analysis window derived from the original LE image.
- LE object and fixup verification: [relocation tooling](../../tools/relocate_le_v131.py). Hash-checked independent instruction tests: [test_rea_colony_yields.py](../../tools/test_rea_colony_yields.py).
- Existing reconstruction reference: [LE analysis](rea-ghidra-le-v131-2026-10-12.md) and [production-function audit](rea-v131-production-bounded-audit.md).
- Tests first succeeded on the private v1.31 source and passed again through the full `tools/run_tool_tests.sh` suite on `penguin`.
- The *same* original function bytes were verified using the raw LE page reconstruction and the relocation-aware Ghidra analysis image. That validates source identity, but Ghidra's higher-level types and parameter assignments still require separate proof.

## Observed function bodies

| Original Watcom symbol | Preferred virtual entry | Bytes | Original-body SHA-256 |
| --- | --- | ---: | --- |
| `Colony_Food2_Per_Farmer_` | `0xde03e` | 136 | `6aef5f245db959b949a22eb0cfccd03b65db2c103a18c4dc47f5bbabcf9a04e4` |
| `Colony_Industry_Per_Worker_` | `0xdec95` | 178 | `1e58a5b42e7d04cbc1d412b55ba007dbee502d5f0c257a96890c93d5689d8aa9` |
| `Colony_Research_Per_Scientist_` | `0xdfdc6` | 177 | `7d9e54a024e600115cf99d1d299806ceaf74f93c1aa95638a135b97e2efadd14` |

Those bounds come from the Watcom CODE symbols. Ghidra observed matching function lengths in the bounded image; because Ghidra had those symbol-derived labels, the equal lengths are a *consistency result* rather than independent function-boundary discovery.

## Direct instruction facts

**Research:** The routine starts with a 32-bit register assignment of 3 at `0xdfdc7`. It compares colony byte fields at offsets `0x13a`, `0x154`, `0x149`, and `0x159` against zero. Its additive instruction sites include +3 at `0xdfe0e` and +5 at `0xdfe65`, with successive +1 or +2 increments in other branches. Later it loads a byte from planet data at stride 17 and offset `0xf`, then compares that byte to 10 and 11. The observed branch assembly and Ghidra decompilation distinguish value 10 (+2) from value 11 (+5), with values outside those cases taking the other path. These are instruction-level observations; the exact gameplay identity and valid range of the planet field are not yet established.

**Industry:** The routine reads a colony word at offset `+2`, multiplies it by 17, and indexes a planet field at `+0xa`. It uses a short mineral-yield lookup table and tests colony flags at offsets `0x13a`, `0x13d`, `0x15a`, and `0x142`; the observed additive instruction constants include +1, +2, and +3. Its final race-related conditional accesses a race record at stride `0xea9`, with a byte comparison against 3 at offset `0x183`. The original symbol `_minerals_per_mine`, although classified CODE in Watcom's debug record, points to five original bytes `[1, 2, 3, 5, 8]` at virtual address `0xdd4b5`. The exact five-byte table is asserted both by values and hash `0a834026e5178e5a668be1e368aeb321b6acdd1d651a3eb141541de4531c6c20`. Table interpretation beyond those five observed indices is unresolved.

**Food:** The routine reads a colony word at `+2`, multiplies it by 17, and fetches a planet-data byte at `+0xb`; an original instruction doubles the fetched value. It checks a race-related field at `+0x134` against 3 and colony flags at `0x164` and `0x13a`. The observed instructions contain +4 and paired +1 increments. Ghidra's candidate pseudocode suggests a special zero-base case followed by conditional bonuses, but the exact register-width and calling-convention effects are not yet verified at runtime.

## Original vs relocated addressing

Raw MOO2 LE instructions refer to object-relative values; they are not necessarily directly meaningful linear addresses until the LE loader fixups are applied.

Four instruction operand source sites were independently checked against the original relocation records:

| Raw LE operand location | Original encoded operand | Verified preferred relocated target |
| --- | --- | --- |
| Industry planet-data pointer `0xdeca3` | `0x1b0d4` | `0x18b0d4` |
| Food planet-data pointer `0xde04c` | `0x1b0d4` | `0x18b0d4` |
| Research planet-data pointer `0xdfe3e` | `0x1b0d4` | `0x18b0d4` |
| Industry mineral lookup `0xdecb0` | `0xcd4b5` | `0xdd4b5` |

The preferred relocated addresses describe the static LE memory image; they do not imply these are the actual runtime bases under every DOS/4GW execution mode.

## Independent static data flow

REA `trace_native_values` on `Colony_Research_Per_Scientist_` at depth 0 reported **110 operation nodes and 113 data-dependency edges**, one decompilation, zero reported unknowns within that limited function traversal, and no truncation when all nodes were requested. The graph included constant 3, branch comparisons, memory loads/stores, and additive operators. The result has **derived** confidence, not verified runtime provenance. It is not proof of pointer aliasing, input ABI, or gameplay equivalence.

## Test status, decisions, and unresolved work

`tools/test_rea_colony_yields.py` verifies three entire original function fingerprints, 22 specifically identified immediate/field operands, four original LE fixup targets, and the five mineral-table values. It refuses any executable whose full SHA-256 differs from the canonical original. `tools/run_tool_tests.sh` invokes this alongside the source integrity, relocation, direct-call, and bounded-window regression suites. These tests passed in the current local workbench and no proprietary source was uploaded.

A conformant future native implementation must first resolve register-width effects, planet record field meanings, valid index ranges, and returned value conventions, ideally through controlled cross-checks against original behavior. Do not replace these unknowns with inferred decompiler variable names or adopt later community-balance changes.

## Industry-to-tax instruction and arithmetic verification

A separate bounded REA/Ghidra query examined `Colony_Industry_To_Tax_` at virtual `0xe08f6` (89 bytes). The original raw function body has SHA-256 `0801f833e5ad497d8d59d069ee8b40e532829f85bedbeeb7ad4d28ca4805cd84`.

The observed instruction sequence loads the colony's **signed 16-bit** industry field at `+0xe9` and **unsigned 8-bit** reserved amount at `+0xf0`, subtracts reserve, then takes a signed-positive branch. If the difference is nonpositive, it stores a 16-bit zero into the tax field at `+0x127` and returns without subtracting from industry. Otherwise it selects the indexed player/race record using the **signed colony byte at `+0`**, record stride `0xea9`, and unsigned tax-rate byte at `+0x31`. The routine multiplies by the positive surplus using 32-bit signed multiplication, executes signed `IDIV 100`, writes the low 16 bits of the quotient at colony `+0x127`, and subtracts that 16-bit tax word from the original industry word at `+0xe9`.

An original operand at `0xe0929` encodes relative `0x1ff98`; the independent LE relocation table resolves it to preferred address `0x18ff98`. The validated original-byte test [test_rea_colony_tax.py](../../tools/test_rea_colony_tax.py) checks the whole body hash, eight opcode/operand sites, the signed branch, multiplication, signed division, low-word stores and the LE relocation. Six numerical examples also test a small isolated arithmetic model. The examples are **derived fixture checks**, not observed DOS gameplay executions or proof of calling-convention equivalence.

The 16-bit write has modular storage semantics; out-of-range inputs, negative owner indices, and exact runtime state selection remain material uncertainties. No gameplay implementation was committed.
