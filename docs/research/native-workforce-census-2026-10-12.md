# Native v1.31 workforce selection and economy inspection — 2026-10-12

## What was verified

The original game's `Colony_Job_Production_` routine was examined again
from the authenticated v1.31 `ORION2.EXE`, SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
Direct REA/Ghidra analysis reports entry `0xde280` and a 996-byte
function body. Independent `objdump` disassembly of the reconstructed
32-bit LE image established the following:

| Original virtual address | Instruction evidence | Meaning |
| --- | --- | --- |
| `0xde376` | `MOVZX EDI,byte [ESI+0x0a]` | Population count |
| `0xde37a` | `LEA EAX,[ESI+0x0c]` | Beginning of packed population records |
| `0xde37d` | `SHL EDI,2` | Four bytes per record |
| `0xde390` | `SUB EDI,4` | Process records in reverse order |
| `0xde393` | `TEST byte [EDI+1],0x02` | Test **packed bit 9**; absent bit skips production body |
| `0xde39f`, `0xde3a6` | `SHL EDX,23; SHR EDX,30` | Extract packed **bits 7–8**, the job slot 0–3 |
| `0xde3a9` | `CMP EDX,EAX` | Match the selected job slot |
| `0xde3b3` | `AND EAX,0x0f` | Extract low-nibble population category |

The `JZ` at `0xde397` and `JNZ` at `0xde3ab` both
resolve to the next-colonist control-flow target `0xde61e`.
`tools/test_rea_workforce_scan.py` checks **11 exact original opcode sites**,
both relative jump targets, a matching full-executable SHA-256 and the
996-byte original Watcom function extent. This test runs only with a
lawfully held local original game executable.

## Native-browser modules

`web/engine/colony-workforce.mjs` implements a read-only census over
the original packed population records and reports:

- total population count, included/skipped counts by original bit-9 test;
- independent counts in each of four packed job-slot values;
- 16-category low-nibble counts, both overall and by included job slot;
- precise raw bit-10 flag on `decodePopulationEntry` for use with the
  previously verified population maintenance routines.

All four packed job values remain separately counted. The original
base-production dispatch table subsequently confirms **0=food,
1=industry, 2=research, 3=null**. Thus value 3 must remain unclassified
for a census and is not a valid base-production dispatch slot; see
[the independent dispatch-table verification](native-base-production-floor-2026-10-12.md).
The module counts records only. It does not equate bit 9 with a guessed
higher-level social or citizenship concept.

`web/engine/colony-economy-inspect.mjs` is a read-only composition of
the workforce census, earlier verified per-worker production rates and
existing original-derived food/industry maintenance routines. The
caller supplies explicit colony, planet and race record buffers and
the result of the still-unreconstructed anomaly/event guard.
It returns a fresh maintenance-record copy and other inspection
values. It does **not** silently multiply workforce totals by unit
rates or simulate a turn.

Both modules reject malformed records and a population list extending
past the earliest known non-population colony field at `+0xe9`.
The resulting count limit of 55 is **conservative memory safety**,
not an established original game population capacity.

## Regression results and remaining work

- Seven workforce tests cover all job-slot bit values, category decoding,
  inclusion/exclusion by bit 9, bit 10, irrelevant high bits,
  non-mutation, boundary limits and invalid input.
- Three economy-inspection tests cover safe composition, explicit
  anomaly outcomes, returned record isolation and missing-state errors.
- The locally run combined original-source/graphics/browser-engine
  suite passed with **54 JavaScript tests** plus the original-image
  and original-executable Python checks. The system had limited free
  disk/RAM and the work avoided copying game binaries or art into GitHub.
- The original code's per-colonist production includes extra calls and
  conditional modifiers, including `Colony_Pop_Base_Prod_Produced_`
  and gravity-dependent effects. Final original colony output,
  appropriate job labels, complete owner/race selection, turns,
  save/load, a playable game scene, and Xbox One Edge hardware
  verification are **not established**.

The final project objective remains a playable, privately deployed
browser version of Master of Orion II v1.31, controlled using an Xbox
One controller on the actual console, with upscaled graphics.
