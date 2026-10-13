# Official v1.31 production-job dispatch and minimum output — 2026-10-12

## Original binary evidence

The source is the same authenticated official v1.31 `ORION2.EXE`
(SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`).
REA/Ghidra located `Colony_Pop_Base_Prod_Produced_` at preferred virtual
address `0xde22c`, with an 84-byte Watcom symbol extent. A separate
`objdump` check of the relocated original LE object confirmed the exact
instructions and control-flow. The wrapper jumps into a shared Watcom
epilogue at `0xdee14/0xdee17`; those jumps are compiler tail sharing,
not evidence of an invalid instruction.

The indirect `CALL [EDI*4+0x17b55c]` at `0xde24e` uses the original
second LE object's data table. Its first three entries have original
object-relative words `0xce0c6,0xced47,0xcfe77`, relocated to:

| Job slot | Preferred target | Original Watcom symbol |
| ---: | --- | --- |
| 0 | `0xde0c6` | `Colony_Empire_Base_Food2_Produced_` |
| 1 | `0xded47` | `Colony_Empire_Base_Industry_Produced_` |
| 2 | `0xdfe77` | `Colony_Empire_Base_Research_Produced_` |
| 3 | `0x00000000` | **Null pointer; not dispatchable** |

The original source-level record layout is not recovered. This table
nevertheless establishes original zero-based **food, industry, and
research** job values. Slot 3 is not assigned to a fourth economy job.

The post-dispatch low-word calculation at `0xde255..0xde27b` uses
`TEST AX,AX`, signed comparisons, the selected job word, and a colony
byte at offset `+0xdd`. For valid **signed 16-bit** base-produced output:

- Positive values remain unchanged.
- Nonpositive food output (job 0) has a minimum of **0** if the colony
  byte at `+0xdd` is zero, otherwise **1**.
- Nonpositive industry or research output (jobs 1 and 2) has a minimum
  of **1**.
- The final selection compares signed `AX` with that minimum, using
  the original shared tail. No additional original-game bonus, rounding,
  or full 32-bit calling convention is claimed here.

## Native implementation and tests

`web/engine/colony-base-production.mjs` exposes a pure
`applyBaseProductionMinimum` function. It accepts an already-computed
signed 16-bit base amount, a verified job slot 0–2, and the raw colony
byte at `+0xdd`; it rejects slot 3 and invalid widths rather than
dereferencing a null pointer or guessing a fourth job.

`tools/test_rea_base_production.py` independently checks the
canonical source hash, original LE-image object hashes,
**13 instruction byte sequences**, shared-tail control transfers,
four original table entries, three relocation records, resolved
Watcom symbol targets, and the 84-byte function extent.

Six additional JavaScript tests verify the isolated minimum-output
calculation including zero, negative, positive and boundary inputs.
With these additions, the local full suite passed **60 JavaScript tests**
along with the original-executable and graphics regressions. The
original binaries and converted artwork remain unmodified and outside
GitHub.

**Not implemented:** the three `Colony_Empire_Base_*_Produced_`
dispatch targets, many production multipliers and category modifiers,
per-colonist final aggregation, job reassignments, full colony turns,
saves, or multiplayer. Browser and Xbox One Edge end-to-end testing
remains pending. This wrapper is not a playable game.
