# Original v1.31 industry-to-tax native arithmetic primitive

## Scope and source

This module implements the **isolated arithmetic semantics** supported by
the original, hash-verified `ORION2.EXE` v1.31
`Colony_Industry_To_Tax_` function at `0xe08f6`, length 89 bytes.
The source fingerprint and original opcode regression are recorded in
[the colony tax evidence](rea-v131-colony-yields.md) and
[the byte-level verification](../../tools/test_rea_colony_tax.py).

[web/engine/colony-tax.mjs](../../web/engine/colony-tax.mjs) is a pure
browser-compatible JavaScript calculation. It accepts signed 16-bit
colony industry, unsigned 8-bit reserved industry and unsigned 8-bit
tax rate. If industry-reserved is nonpositive, it yields zero tax and
leaves industry unchanged. Otherwise, the verified original code
uses signed multiplication, signed division by 100, and two 16-bit
stores; the JS implementation preserves word-wrap semantics.

## Reproduction and limits

Test with `node --test web/engine/tests/colony-tax.test.mjs` or the
combined `tools/run_tool_tests.sh` suite. The checks cover known
isolated arithmetic fixtures, word wrap and rejection of unsupported
input widths.

The original routine also selects a tax rate through game-state
records. That state-selection/caller ABI is **not** implemented
in this pure function. Therefore these tests do **not** prove an
end-to-end game-turn equivalence, save/load correctness or a
fully playable original v1.31 economy. No original executable
or copyrighted assets were incorporated into the browser module.

The new browser game remains incomplete. Additional isolated routines
will be promoted only when their inputs, outputs and effects are
established by independent original evidence.
