# v1.31 original `Get_Advanced_Government_Type_` — isolated full routine

**Status:** the complete **65-byte** original routine is reconstructed
as a standalone C function. It is not original MicroProse source,
not a full government or technology system, and has not been
differentially executed inside the original DOS game.

Source is authenticated v1.31 `ORION2.EXE`, SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

Original Watcom CODE symbol `Get_Advanced_Government_Type_`
starts at `0x83D0A`, ending at `0x83D4A` inclusive.
Its four-entry, original-byte-verified CODE table is immediately
**before** the function at `0x83CFA`, and its dispatch is at
`0x83D2E`. All four case target addresses are in this one
function interval:

| Case index | Target (original CODE offset) | Result |
| ---: | --- | ---: |
| 0 | `0x83D36` | 1 |
| 1 | `0x83D3A` | 3 |
| 2 | `0x83D3E` | 5 |
| 3 | `0x83D42` | 7 |

## Exact observed dataflow

1. Watcom input `AX` is sign-extended to EAX with `CWDE`.
   The signed player index is multiplied by original record stride
   **`0xEA9`**.
2. Load the player-record base pointer from original DATA global
   **`_player`** at DATA object 2 offset `0x1FF98`,
   then load and **signed-extend the byte** at relative record
   offset **`0x89F`** into EAX.
3. `CDQ; SUB EAX,EDX; SAR EAX,1` computes the signed input
   divided by two **truncated toward zero**.
4. `XOR BL,BL`; `CMP AL,3; JA`: a *byte-width unsigned*
   comparison. If the low 8-bit index is greater than 3, leave
   BL=0, then return.
5. Otherwise `MOVZX EAX,AL` and the four-entry
   `JMP DWORD PTR CS:[EAX*4+0x83CFA]` selects
   `MOV BL,1/3/5/7`. Each case converges on
   `MOVSX AX,BL; POP EDX; POP EBX; RET`.
   That original 16-bit AX result is the authoritative
   output; no assumption is made about unused upper EAX bits.

The isolated equivalent mapping for a signed 8-bit input is:

- `raw == -1` maps to **1** (signed -1/2 truncates to 0)
- `raw == 0 or 1` maps to **1**
- `raw == 2 or 3` maps to **3**
- `raw == 4 or 5` maps to **5**
- `raw == 6 or 7` maps to **7**
- All `raw <= -2` or `raw >= 8` maps to **0**

The special `raw == -1` behavior would be silently
lost if code used floor division, unsigned interpretation,
or an ordinary division of a widened value without the
original low-byte test.

## Portable derived C verification

The isolated C source was compiled as C11 with
`-Wall -Wextra -Werror -pedantic -O2`. Its signed-byte helper
was compared with an independently expressed emulation of
the observed divide-by-two, low-byte unsigned dispatch, and
four return cases for **all 256** possible signed-byte inputs.
A separate record-access check covered all 256 stored byte
encodings at one player-record offset and compared the
record wrapper's output to the verified helper. Both checks passed.

This is a **derived-code self-consistency verification**, not
dynamic equivalence testing inside the original DOS executable.
The original symbol table confirms the global pointer is
`_player` (singular), at original DATA object 2 offset
`0x1FF98`.

## Reconstructed code

`decompilation/reconstructed/advanced_government_type_v131.c`

The C implementation exposes both the original data-record
access and a pure signed-byte helper, and assumes an existing
valid player-record allocation. It has no copyrighted game
assets or external game-library dependency.

**Important semantic limit:** the names `Get_Advanced_Government_Type_`
and `_players` come from the original Watcom symbol table.
The meaning, normal range, and producer of the signed byte
at record `+0x89F` must be cross-referenced before making
this a definitive player-government rule inside a running
game. No website or game-engine files were modified.
