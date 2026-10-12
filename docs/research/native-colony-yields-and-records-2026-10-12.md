# V1.31 native colony yields and byte-record adapter — 2026-10-12

## Implemented from original source evidence

The canonical original MicroProse `ORION2.EXE` v1.31 is SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
The native-browser pure functions reproduce **isolated** arithmetic
verified through original opcode disassembly and the byte-level
`tools/test_rea_colony_yields.py` regression:

- `Colony_Food2_Per_Farmer_`, entry `0xde03e`: planet byte `+0x0b`
  times two, optional special zero-base correction selected by
  caller-provided race record byte `+0x134 == 3`, followed by +4
  for colony flag `+0x164` and +2 for flag `+0x13a`, **only when
  doubled food is positive**. Output remains doubled-food units.
- `Colony_Industry_Per_Worker_`, entry `0xdec95`: the original
  `_minerals_per_mine` table `[1,2,3,5,8]` indexed by planet byte
  `+0x0a`; colony flags `+0x13a,+0x13d,+0x15a,+0x142`
  add 1, 1, 2, and 3 respectively, and selected race record byte
  `+0x183 == 3` adds one.
- `Colony_Research_Per_Scientist_`, entry `0xdfdc6`: base 3,
  colony flags `+0x13a,+0x154,+0x149,+0x159` add 1, 2, 3, and 1;
  planet byte `+0x0f` adds 2 when equal to 10, 5 when equal to 11,
  and zero otherwise.
- The existing `calculateIndustryTax` implements the separately
  verified `Colony_Industry_To_Tax_` arithmetic and low-word stores.

The new `web/engine/colony-yields.mjs` requires explicit byte/boolean
inputs instead of guessing original building or race names. Unknown
mineral class indices are rejected, not read past the five-byte table.
The `web/engine/colony-records.mjs` adapter reads the original
signed planet-id word from colony `+2`, indexes 17-byte planet
records, reads exact colony and race byte offsets and returns
isolated per-unit production rates. Another pure operation clones
a colony byte record, storing industry tax as a signed 16-bit word
at `+0x127` and adjusted industry at `+0xe9`. Original input
buffers remain unchanged.

## Test results and limitations

- `web/engine/tests/colony-yields.test.mjs` covers the complete five
  mineral classes, full 256-byte planet-value domains, building/flag
  combinations, special cases and invalid widths.
- `web/engine/tests/colony-records.test.mjs` verifies 17-byte
  planet strides, exact colony/race offsets, signed planet id,
  production-rate composition, clone-only tax writes, and
  invalid/out-of-range records.
- The full 35-test JavaScript graphics, controller and engine suite
  passed locally, alongside the original-file LE/relocation/graphics
  regression suite, with no failures.
- Ghidra direct function boundaries and the Watcom symbol data share
  origins. Semantic verification rests on original disassembly and
  byte-level checks, not on asserted independent source recovery.

**Not yet implemented or verified:** population job assignments, full
colony production totals and upkeep ordering, player economy and
treasury state, actual turn advancement, game saves, native galaxy
and battle rules, an enabled New Game action, HTTPS server deployment
and real Xbox One Edge controller behavior. Caller-selected
production-race and owner-tax records remain explicit because their
selection semantics have not been established. The optional Watcom
diagnostic `EBX` output is not implemented. Unsupported/invalid
original planet IDs cannot be considered valid native gameplay
inputs without further original evidence.

The original game binaries and derived copyrighted art remain local
and are not part of this commit.
