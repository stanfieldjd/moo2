# Original v1.31 race option slot 7 controls player BYTE+0x8AF

## Source and result

Canonical original locally supplied official `ORION2.EXE` v1.31 SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`; original Watcom LE CODE SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. Full original named-body hashes, 34 original opcode-byte anchors, four exact original CALL displacements, three original DATA symbol locations, and 57 controlled source-derived offset/value checks are enforced by `tools/audit_player_option_8af_v131.py`. Machine-readable record: `decompilation/reports/player_option_8af_v131_2026-10-16.json`. The proprietary game executable and extracted images stay local.

The original v1.31 **player BYTE +0x8AF** tested by `Modify_Home_Worlds_` is a round-trippable **race-configuration WORD entry in the original named DATA `_option_toggle` array**, specifically **index 7**. This is stronger than an unknown flag read, but is not a recovered original user-visible label, option cost, or proof that arbitrary combinations of user-selected options are valid.

## Authenticated original UI-to-source call path

- `Newgame_Screen_` original CODE `0xBD722` calls `Race_Selection_Screen_` at CODE `0x4C510`.
- `Race_Selection_Screen_` original CODE `0x4C9D7` calls `Racial_Option_Screen_` at CODE `0x4A3BC`; this named original function also has another call site within the race-selection body.
- `Racial_Option_Screen_` at original CODE `0x4A3EF` calls `Convert_Player_To_Flags_` at CODE `0x4AD97` to prepare the options from the player. At original CODE `0x4A8D4`, it separately calls `Convert_Flags_To_Player_` at CODE `0x4AE38` to transfer race-options state into the player.
- Every named procedure body above is checked **whole-function SHA-256** against the locally authenticated original CODE bytes, and every cited CALL byte/displacement is checked directly. Linker callgraph edges are cross-checked against `decompilation/game_call_edges.csv`. This establishes the original configuration route; the gate governing a particular screen interaction remains subject to full original UI control flow.

## The specific offset mapping, including its nontrivial index shift

Original `Convert_Player_To_Flags_` sets EBX to the player record field `+0x89F` at CODE `0x4ADA0`. In its second option loop, the source reads **a signed BYTE** at `[EBX+ECX]` (CODE `0x4ADDD`), constructs output index `ECX+ESI` (CODE `0x4ADE5–0x4ADE8`) and stores the value as a WORD at original DATA `0x236C8 + 2*(ECX+ESI)` (CODE `0x4ADED`).

At source loop `ECX = 15`, there is an original special representation case: source processes two mutually exclusive WORD choices for a signed option, then changes `ESI` from 0 to 1 at `0x4AE27`. Therefore for source loop `ECX = 16`:

```text
player byte = 0x89F + 16      = 0x8AF
flags WORD  = 0x236C8 + 2*17 = 0x236EA
_option_toggle base            = 0x236DC
slot index  = (0x236EA - 0x236DC)/2 = 7
```

Original `Convert_Flags_To_Player_` starts with ESI pointing to player BYTE `+0x89F` (CODE `0x4AE4F`). In the later options loop, it treats source option index 15 as special and increments EAX at `0x4AECF` and again at `0x4AEE7`, *skipping index 16*. Its regular later conversion subtracts the shift of 1 from the source WORD index (CODE `0x4AED5–0x4AEDB`). For original EAX=17, it loads the **low BYTE** of original flag WORD `0x236C8+2*17` (CODE `0x4AEDD`) and stores it to `[ESI+(17-1)]` (CODE `0x4AEE4`). Again, that is player BYTE `+0x8AF`.

This exact forward and reverse mapping is independently checked for the eight controlled player BYTE values `0,1,2,10,127,128,254,255`. The signed-byte-to-signed-WORD conversion is preserved in the forward direction and low-BYTE extraction in the reverse direction. Seven additional controlled option WORDs validate low-byte behavior; the original index arithmetic tests cover 57 assertions. The normal screen setting is not necessarily restricted to boolean values by these source instructions; subsequent game code treats nonzero as enabled.

## Source connection to research-bonus planet creation

The original `Modify_Home_Worlds_` (CODE `0x6C4AF`) uses player stride `0xEA9`, reads original DATA `_player` at `0x1FF98` and tests exactly **BYTE player+0x8AF** at CODE `0x6C61F`. If zero, its branch at `0x6C627` skips the special assignment. If nonzero, CODE `0x6C635` writes **planet BYTE+0x0F = 10** in an original **17-byte** planet record. `Colony_Research_Per_Scientist_` reads that same original planet BYTE `+0x0F` via the same original `_planet` DATA pointer, and adds **2** to the base for code 10. The original source special planet-code generation and scientist-read are checked again in this auditor and in `tools/audit_research_planet_special_origin_v131.py`.

## Limits and remaining proof

The named original DATA symbol `_option_toggle` is verified at address `0x236DC`, index7 at `0x236EA`. The exact race UI option label, whether the option is allowed by every race/budget, its default values, whole-player-record copy/initialization behavior, and the range of valid combined player-government/colony-worker/settings/gravity values **are not established by this checkpoint**.

This demonstrates an actual source **race-configuration-to-home-world-planet-state route**, not DOS runtime gameplay differential parity, not a confirmed player-facing production display defect, and not a revised completion-percentage measurement. The v1.31 rules are preserved without correction or modernization of gameplay.
