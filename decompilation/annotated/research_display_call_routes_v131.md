# v1.31 research production: direct original UI and turn-computation caller routes

## Provenance and audited scope

Source: official locally supplied v1.31 `ORION2.EXE`, SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`; extracted Watcom LE CODE SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. Reproducer: `tools/audit_research_display_call_routes_v131.py`, report `decompilation/reports/research_display_call_routes_v131_2026-10-16.json`. No original executable or game assets are checked into Git.

Eight complete named original body hashes and function-map extents are authenticated: `Evaluate_Screen_Input_` (1038 bytes, CODE `0xAFDEE`), `Show_Research_Production_` (46 bytes, CODE `0xD03C3`), `Pre_Import_Computing_` (198 bytes, CODE `0xD1D59`), `Colony_Research_Production_` (1103 bytes, CODE `0xCFF74`), `Colony_Job_Production_` (996 bytes, CODE `0xCE280`), `Colony_Pop_Base_Prod_Produced_` (84 bytes, CODE `0xCE22C`), `Colony_Empire_Base_Research_Produced_` (253 bytes, CODE `0xCFE77`) and `Colony_Research_Per_Scientist_` (177 bytes, CODE `0xCFDC6`).

The audit contiguously decodes **all seven** named bodies other than `Evaluate_Screen_Input_` and its **exact 0xB009B..0xB00B9 UI call-site block**. `Evaluate_Screen_Input_` contains bytes elsewhere that a generic linear decoder cannot reliably classify as instructions; the body as a whole is **only SHA-verified** and is *not* claimed instruction-covered in this checkpoint. In total, 822 instructions are checked within those supported scopes, alongside 55 exact source opcode checks, six named original direct-call edges, and 13 bounded controlled path fixtures. The original call-graph CSV separately lists these two direct callers of `Colony_Research_Production_`: `Pre_Import_Computing_` and `Show_Research_Production_`. This does **not** exclude independent indirect call sites.

## The original caller difference is demonstrable

**Ordinary colony calculation** proceeds as follows:

1. `Pre_Import_Computing_` original CODE `0xD1DFD` executes `XOR EDX,EDX`, then CODE `0xD1DFF` directly CALLs `Colony_Research_Production_`.
2. The called procedure at CODE `0xCFF7E` saves EDX into EDI, so the optional output pointer is **zero** in this path. On the normal nonempty/nonanomaly branch at CODE `0xCFFD3–0xCFFE8`, it uses `XOR EBX,EBX` and passes EBX null to `Colony_Job_Production_`.

**On-screen research explanation** uses a different original caller:

1. `Evaluate_Screen_Input_` checks an original UI selection word at CODE `0xB009B`; on its matching branch, CODE `0xB00AB` sets EDX to 1 and `0xB00B0` CALLs `Show_Research_Production_`.
2. `Show_Research_Production_` allocates a local `0xBB8`-byte stack frame and at CODE `0xD03D6` executes `LEA EDX,[EBP-0xBB8]`. CODE `0xD03DC` directly CALLs `Colony_Research_Production_` with that **non-null** temporary buffer pointer.
3. The research calculation stores this EDX into EDI and at CODE `0xCFFD7` constructs a local breakdown pointer in EBX, which it passes to `Colony_Job_Production_` at CODE `0xCFFE8`.

In both normal branches, the original research calculator takes the job result, adds its own original colony flags, and **writes WORD colony+0xEB** at CODE `0xD0050` before checking EDI again to select the optional formatting/return path. A screen explanation request therefore invokes the original production calculation and can update the numeric colony field; it is **not** merely a read-only formatting wrapper.

## Connection with the previously proved nested breakdown alias

The original `Colony_Job_Production_` creates a zeroed temporary breakdown structure at `EBP-0x4D4` and passes it in ECX to the nested source dispatcher only if its own incoming breakdown pointer is non-null. Original research dispatch selects `Colony_Empire_Base_Research_Produced_`, which conditionally calls `Colony_Research_Per_Scientist_` with that structure in EBX.

When the planet BYTE `+0x0F` equals 10 or 11, the scientist helper conditionally writes +2 or +5 to temporary breakdown DWORD `+0x226`, respectively. Later, the job routine **always** reads DWORD `[EBP-0x2AE]` as a numeric contribution at CODE `0xCE609`, and `-0x4D4+0x226=-0x2AE`. Thus the source original UI/turn caller routes decide whether that nested breakdown write is enabled, and the corresponding buffer field is also read by original numeric computation.

### Bounded synthetic paired experiment, *not* original DOS gameplay

The separate test model combines the original authenticated scientist, multiplier and signed final-division arithmetic on a hypothetical one-population research state, with synthetic government group 0, gravity factor 2, settings BYTE +8, tag 0 different from colony owner, appropriate original entry flags, and no other production bonuses. This input has **not** been demonstrated as a reachable unmodified official v1.31 game save.

| Hypothetical planet BYTE +0x0F | Normal recalculation caller: no breakdown | Screen explanation caller: with breakdown |
|---|---:|---:|
| 0 | 0 | 0 |
| 10 | 0 | 1 |
| 11 | 0 | 1 |

The first row is the control; the second and third show a possible source-visible numerical difference. The test is deterministic arithmetic **derived from machine-code branches**, not execution of the game's DOS runtime.

## Conclusions and limitations

- **Authenticated:** two distinct original named caller paths, a real direct UI call site, the exact null versus non-null buffer propagation, both routes' numeric write to colony WORD `+0xEB`, the nested scientist-buffer write and original job-stage numeric read. All four deeper computation bodies were independently source-authenticated in the earlier dependency checkpoint.
- **Not established:** reachability of the hypothetical combined planet/player/colony state; whether the behavior causes an actual observable mismatch in unmodified DOS gameplay; any externally indirect research-production call sites; original x86 high-half/overflow behavior outside fixtures; native runtime parity.
- **No behavioral change authorized:** the original MicroProse v1.31 baseline is preserved. Any possible correction requires a real-state/differential check and a separate explicit deviation decision under `PROJECT_RULES.md`.

This is a verifiable **static original-source caller-route expansion**, not finished full-game decompilation or a new overall completion-percentage measurement.
