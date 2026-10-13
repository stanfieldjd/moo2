# v1.31 `Fire_Ship_`: original ammunition mutation paths

**Status:** exact original x86 instructions at two ammunition
decrement sites and one slot-reload site recovered and translated
as **isolated post-fire C state mutations**. This is **not**
the complete 2,216-byte `Fire_Ship_` source and does not
perform missile launches, bomb application, animation, event
processing, combat AI, or a whole tactical turn.

Authenticated original `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

## Original source anchors and decision boundary

Original Watcom `Fire_Ship_` entry is CODE
`0x28B5E`, body length 2,216 bytes.
The independent original-code audit checks **15**
selected source instructions and helper symbols,
including the three actual slot-state writes:

| Original CODE address | Immediate preceding control flow | Observed slot mutation |
| --- | --- | --- |
| `0x28FB5` | `0x28F85` CALL `Fire_Missile_`; conditional branch `0x28F95` sees local 16-bit mode equal **2** | Load a byte from original `_weapons` definition at `weapon_id*28 + 0x0D` and store the zero-extended value as a WORD at selected combat ship weapon-slot `+0x58` |
| `0x28FC3` | Following the same missile helper but when the local mode is **not 2** | `DEC WORD` at selected combat ship weapon-slot `+0x58` |
| `0x2910C` | `0x290EE` CALL `Fire_Bomb_` then weapon-slot lookup | `DEC WORD` at selected combat ship weapon-slot `+0x58` |

The weapon-record selection uses the established
**313-byte** combat ship stride (`0x139`) and
**11-byte** weapon-slot stride (`0x0B`).
The selected ammo/state WORD is the same `+0x58`
field examined by the recovered
`Is_Ship_Out_Of_Ammo_` routine
(`decompilation/annotated/combat_ammo_v131.md`).

The original `_weapons` data global is at original
DATA object 2 offset `0x7803`. Its definition
record stride is `0x1C` (28 bytes). The original
reload byte is at `0x7810`, i.e. `+0x0D`
within a weapon definition. The original
`MOVZX DX,BYTE PTR [EDX+0x7810]` makes that
replacement word **0–255**.

Both decrement paths use the original x86
**16-bit** `DEC WORD` operation, so without
an earlier guard, decrementing the zero
bit pattern produces `0xFFFF`; whether
such a state is reachable under normal combat
rules must be established from the rest of the
firing preconditions. Do not replace the
original result with saturating subtraction.

This is a **bounded state-write reconstruction**.
A subsequent source-byte audit **has now resolved the original
selector producer and switch table**. At `0x28CA4`, `Fire_Ship_`
reads the signed weapon ID from the selected 11-byte slot;
at `0x28CA7` it multiplies that ID by the original 28-byte
definition stride, and at `0x28CAA` it reads the category BYTE
at original `_weapons+0x0C`. `0x28CB2` stores that value
into local `[EBP-0x14]`, subsequently consumed as a WORD.

Original jump table at `0x28B46`, dispatched by
`0x28F62` after an unsigned category `<=5` check:

| Category | Branch target | Named helper invoked |
| ---: | --- | --- |
| 0 | `0x28FD1` | `Fire_Beam_Weapon_` |
| 1 | `0x28F6A` | `Fire_Missile_` |
| **2** | `0x28F6A` | `Fire_Missile_`; subsequent `0x28FB5` **overwrites the counter** |
| 3 | `0x290E2` | `Fire_Bomb_` |
| 4 | `0x28F6A` | `Fire_Missile_` |
| 5 | `0x29113` | `Fire_Special_Weapon_` |

Categories above 5 branch to shared `0x29143`; this
means no firing-helper call through the six-case dispatch,
not necessarily that the whole routine performs no other work.
The special category-2 counter behavior is now proven to
be tied to **weapon definition category 2**, not an
independent, unknown gameplay "reload mode."

New source-audit and C reconstruction:
`tools/audit_fire_ship_category_dispatch_v131.py`,
`decompilation/reports/fire_ship_category_dispatch_v131_2026-10-13.json`,
`decompilation/reconstructed/fire_ship_category_dispatch_v131.c`.
Regression:
`tests/test_fire_ship_category_dispatch_v131.c`,
`tests/test_fire_ship_category_counter_integration_v131.c`.
All 2,048 category/slot combinations and 6,144
category-driven missile-counter writes passed under
strict C11, ASan and UBSan.



## Source, audit and derived tests

- `tools/audit_fire_ship_ammo_mutations_v131.py`
- `decompilation/reports/fire_ship_ammo_mutations_v131_2026-10-13.json`
- `decompilation/reconstructed/fire_ship_ammo_mutations_v131.c`
- `tests/test_fire_ship_ammo_mutations_v131.c`

The derived C does **not** call `Fire_Missile_`
or `Fire_Bomb_`; it accepts an already-selected
ship record and slot, then reproduces **only**
the observed post-call mutation. It deliberately
adds input length/index checks that the original
machine code lacks. This is a safe host interface
choice, **not original DOS error behavior**.

The C compiled with strict C11 warnings
and passed AddressSanitizer/UndefinedBehaviorSanitizer.
Regression tests covered all eight weapon slots,
the complete 65,536-value 16-bit decrement
domain, all 256 replacement-byte values,
and malformed host input.

Original state-write audit verified the named helper
calls and all 15 selected original instructions. The follow-on
category-dispatch audit verified an additional 17 original
instruction anchors and all six original jump table DWORDs.
It is **not** a dynamic differential comparison
with the original DOS executable.

## Pending original-game work

The six-way `Fire_Ship_` dispatch and its selector
producer are now recovered; fully decompile
`Fire_Missile_`, `Fire_Bomb_`, `Fire_Beam_Weapon_`
and `Fire_Special_Weapon_`, and identify
how firing eligibility, action points, cooldowns
and effects are applied. Then connect these
post-fire state mutations to the existing
weapon activation/remaining-count and
launched-fighter logic with original-game
differential tests.

Full game decompilation is incomplete. No
original media, executable bytes, or private
archives are distributed. Game Lab, Xbox
controller code and Qwen remain unchanged.
