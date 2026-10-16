# Original v1.31 gravity production factor and two race-option inputs

## Source identity, byte and decoder coverage

The canonical MicroProse v1.31 original DOS executable is authenticated locally by SHA-256 4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f. Its original extracted Watcom LE CODE object has SHA-256 f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837. Neither source binary nor game assets are committed.

The original named **Gravity_Player_Production_Factor_**, at CODE 0xCDF2C, occupies **167 bytes**, SHA-256 a0660fd4edfd3b57bb91c406ca614e6c445ff509fb191eb5b757bdc254142200. All **52** original instructions, three continuation-byte rows, and **all direct conditional branch targets** were decoded and authenticated. The original full named bodies of **Convert_Player_To_Flags_** (161 bytes), **Convert_Flags_To_Player_** (188 bytes) and **Colony_Job_Production_** (996 bytes) were independently byte-hashed and contiguous-decoded too.

Source-verification program: tools/audit_gravity_production_factor_v131.py; report: decompilation/reports/gravity_production_factor_v131_2026-10-16.json. Four bodies together have 441 decoded original instructions, **49 exact instruction anchors** and 145 controlled assertions. These are bounded static reconstruction tests, not original DOS program execution.

## Original calling convention and return

At CODE 0xCE3B3-0xCE3BB, Colony_Job_Production_ derives the population tag from the packed entry's low nibble, passes it in DX and the colony pointer in EAX, and calls Gravity_Player_Production_Factor_. Original CODE 0xCE3C0-0xCE3CA computes **4 minus the factor**. The caller's subsequent source multipliers include a signed **-5 * (4-factor) * population production base** gravity adjustment, with source native integer widths preserved by the larger worker-stage analysis.

The gravity helper itself tests colony BYTE +0x14F at CODE 0xCDF2E. If nonzero, it returns factor **4** without examining planet gravity. If zero, it checks signed DX against 8 at CODE 0xCDF3B: population tag 8 or greater also receives **4**. The model limits tags to 0..9 and makes no assumption about negative or out-of-range tags.

For tags **0..7** and colony BYTE +0x14F == 0, source reads signed planet ID WORD at colony +0x02, multiplies by **17**, dereferences original DATA _planet at 0x1B0D4, and reads the associated original planet BYTE +0x06. This is a planet gravity *code*, not the planet-special BYTE +0x0F involved in the previous research work. The two sources must not be conflated.

### Exact source-branch factor table for planet gravity codes 0..2

| planet BYTE+0x06 | player BYTE+0x8A9 | player BYTE+0x8AA | factor returned |
|---:|---|---|---:|
| 0 | zero | ignored | **3** |
| 0 | nonzero | ignored | **4** |
| 1 | zero | ignored | **4** |
| 1 | nonzero | ignored | **3** |
| 2 | ignored | zero | **2** |
| 2 | ignored | nonzero | **4** |

Source checkpoints: CODE 0xCDF56–0xCDF67 dispatches the original gravity code; CODE 0xCDF77 and 0xCDF9A test player BYTE +0x8A9 for planet code 0 and 1; CODE 0xCDFB5 tests +0x8AA for planet code 2. Return 3 originates at 0xCDF81, 2 at 0xCDFBF, and 4 at 0xCDFC9.

**The source case for planet gravity codes 3 and above is not assigned a guessed factor.** CODE 0xCDF60 executes MOV EAX,EBX and returns; on that path there is no immediately prior assignment to EBX inside this original helper. This source evidence does not prove a safe normal-game return or a valid runtime input domain. It is not authorization to change original rules.

### Implication for the numeric production stage

For the authenticated normal factor values 2, 3 and 4, the gravity adjustment is, respectively, **-10 times**, **-5 times**, or **0 times** the per-entry production base. There is no independent gravity term added when factor is 4. This stage was previously authenticated against full Colony_Job_Production_ CODE; the new audit now resolves the actual factor input branch conditions.

## Source connection to original race options

The gravity helper reads the original DATA _player pointer at 0x1FF98 with a **0xEA9-byte player stride**; then accesses BYTEs **+0x8A9** and **+0x8AA** for the tag-indexed player.

Their original race-option mapping is independently source-verifiable using the same two converter functions that resolved the +0x8AF home-world flag in the preceding checkpoint:

- The converter's field-base is player BYTE **+0x89F** (CODE 0x4ADA0 and 0x4AE4F).
- Source field **+0x8A9** has pre-special-case field index **10**, which maps to the flag WORD at DATA 0x236C8 + 2*10 = **0x236DC**, exactly **_option_toggle[0]**.
- Source field **+0x8AA** has field index **11**, mapping to DATA 0x236C8 + 2*11 = **0x236DE**, exactly **_option_toggle[1]**.
- The special source index-15 shift only applies beyond those two fields; neither index is shifted. Both conversion directions are independently checked by instruction anchors and original function hashes.

This proves these two gravity-adjusting player fields participate in race-options data conversion. It does **not** independently establish their on-screen labels, allowed selection combinations, racial ability costs, or default states. These remain unknown pending separate original source examination.

## Confidence boundaries

Verified: canonical source bytes, four complete named original bodies, contiguous instruction decode with reassembled disassembler continuation lines, entire gravity branch destination inventory, exact machine code anchors, original _planet/_player/_option_toggle DATA symbol locations, two original named direct callers in the linker callgraph, and complete bounded 0..2 code / boolean option truth table.

Unverified: original DOS runtime differential execution; a globally proven planet gravity-code range; valid saved-game population assignment and option combinations; the full native engine. The previously recorded 87% whole-executable estimate is unchanged and unrecalculated.
