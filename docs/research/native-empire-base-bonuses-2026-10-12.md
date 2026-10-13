# MOO2 v1.31 uncached empire-production bonuses — 2026-10-12

## Evidence and precise scope

These additions were reconstructed from the user's locally held, canonical
MicroProse v1.31 `ORION2.EXE`, SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
REA/Ghidra analysis and independent raw-byte disassembly identified the
following original functions, with body lengths and SHA-256 hashes:

| Symbol | Virtual entry | Bytes | Raw LE-code SHA-256 |
| --- | --- | ---: | --- |
| `Colony_Empire_Base_Food2_Produced_` | `0xde0c6` | 358 | `705a9348d1b7e97003bd711a8553e114d453b5fbe745b0706c47dffe1de913c2` |
| `Colony_Empire_Base_Industry_Produced_` | `0xded47` | 212 | `35aa50fa88250f254ba329b69bc8ed99ba7b9d647fe29f1fcffa1e7ecb4c24d8` |
| `Colony_Empire_Base_Research_Produced_` | `0xdfe77` | 253 | `1e72e37daea066aa98c587b71c86f1faae81775b60886693b9a3d33b8888e0f9` |

The independently executable source regression
`tools/test_rea_empire_base_bonuses.py` verifies **24 original machine-code
instruction sites**, all three body hashes and boundaries, and three original
relative `CALL` targets for the preexisting per-worker calculations.
It reads only a lawful local original executable and does not publish binaries.

### Uncached production arithmetic

- **Food (job 0):** Use the previously verified doubled-food-per-farmer
  computation, except when the colony's signed owner byte matches the
  requested category and there is no diagnostics context, in which
  case the original fast path reads byte `colony+0xdd`. The original
  food function returns immediately if the selected base is **nonpositive**,
  without adding subsequent population-category bonuses. For
  categories 0–7 on the uncached positive path, add the signed race byte at
  `race+0x8a1`. When race flag `+0x8ab` is nonzero and colony climate
  byte `+0xe2` is 4 or 6, add `2*(globalCapA-climateTable[climate])`.
  Climate values 5 and 8 instead select `globalCapB`. The climate table
  and caps are original game-state globals, so the native implementation
  accepts them explicitly instead of guessing them. Category 8 receives
  special +6, category 9 receives +4. Other categories above 9
  receive no bonus from this branch.
- **Industry (job 1):** Use the previously verified per-worker industry
  calculation or the owner fast-path byte `colony+0xde`. For categories
  0–7 on the uncached path, add the signed race byte `+0x8a2`;
  category 8 adds **3**; remaining categories add zero.
- **Research (job 2):** Use the previously verified per-scientist calculation
  or the owner fast-path byte `colony+0xdf`. For categories 0–7 on the
  uncached path, add signed race byte `+0x8a3`; an additional +1
  applies only if the category equals the signed colony-owner byte and
  the corresponding race byte `+0x16b` equals 3. Category 8 adds 3;
  higher categories receive no bonus here.

The original uses **16-bit word additions**, so the browser helper
models signed 16-bit wrapping where necessary. The independently verified
`Colony_Pop_Base_Prod_Produced_` minimum-output rule is applied only
*after* the uncached calculation in the source-only record adapter.

### Files and validation

- `web/engine/empire-base-bonuses.mjs`: pure arithmetic helpers with
  explicit original record fields and the category/climate branches.
- `web/engine/empire-base-records.mjs`: read-only adapter for raw colony
  and 0xEA9-stride race record arrays, explicit calculated base and
  external climate globals. It combines the verified bonus arithmetic
  with the previously reconstructed minimum-output function.
- Two browser tests add **17 passing test cases** covering climate cases
  4/5/6/8, negative and positive race bonus bytes, special categories,
  signed word wrapping, owner matching, input validation and source
  immutability.
- The full verified original-executable/graphics/JavaScript suite
  passed **77 JavaScript tests and all existing Python checks** locally
  before this publication.

### Material limitations

The original routines maintain **global signed-byte caches** keyed by
colony context and owner. The new helpers are explicitly **uncached**:
they do not implement cache initialization/invalidation, original
diagnostic breakdown buffers, automatic race and player selection,
actual colony production totals, population assignment, or end-of-turn
updates. The original owner fast paths are identified by byte offsets
but are not automatically chosen by the helpers; callers explicitly
supply the computed base. A complete browser-game turn has **not**
been reconstructed and no new playable game screen is claimed.

The output is source-only; original executable files, palettes and
privately decoded animation frames remain outside GitHub. Xbox One
Edge hardware testing and HTTPS deployment remain outstanding.
