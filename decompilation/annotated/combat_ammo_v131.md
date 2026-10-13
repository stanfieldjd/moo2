# Original v1.31 combat ammunition and special-bitfield decompilation

**Status:** isolated machine-instruction-supported C reconstruction of
three complete game-code functions, plus the result semantics of one
original runtime bitfield helper. This is **not original MicroProse C**,
not a complete combat engine, and not differentially executed in the
original DOS game.

Verified `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

## Original Watcom code anchors

| Function | Original CODE | Length |
| --- | ---: | ---: |
| `Check_For_Launched_Fighters_` | `0x19480` | 95 bytes |
| `Is_Ship_Out_Of_Ammo_` | `0x194DF` | 241 bytes |
| `Does_Combat_Ship_Have_Special_` | `0x3B0D3` | 75 bytes |
| `Test_Bit_Field_` (support helper) | `0x1176F0` | 34 bytes |

The audited original LE CODE object is 1,410,709 bytes. The
authenticated source hash and 43 selected original opcode anchors,
all original entry lengths, helper call destinations and case table
DWORDs are checked by `tools/audit_combat_ammo_v131.py`, with the
generated result in
`decompilation/reports/combat_ammo_audit_v131_2026-10-13.json`.

## Original game data and exact field offsets

These are original DATA object 2 symbols, not absolute host pointers:

- `_combat_data` at `0x1A864` is a pointer to combat ship records.
  Each combat ship has an original **313-byte** (`0x139`) stride.
- Its eight weapon slots begin at record `+0x52`, with
  **11-byte** (`0x0B`) stride. Within a slot:
  `+0` is signed 16-bit weapon ID, `+2` is a nonzero
  installed/present byte, and `+6` is a **signed 16-bit**
  stock/ammunition-like field.
- `_weapons` begins at DATA offset `0x7803` and contains
  **28-byte** (`0x1C`) records. Weapon-category byte
  `record+0x0C` is read at original DATA `0x780F + id*28`.
- `_missile` at DATA offset `0x1AB14` points to records
  with **26-byte** (`0x1A`) stride. Within each:
  `+0` is signed 16-bit weapon ID and `+4`
  is signed 16-bit owner/combat-ship ID.
- Original DATA word at `0x218AC` is compared as a WORD
  with zero-extended combat-ship byte `ship+0x20`.
  The semantic name and producer of this DATA word
  are **not yet verified**.

## `Is_Ship_Out_Of_Ammo_`: exact observed decision structure

Input `AX` is the combat ship index. The original function first
calls `Does_Combat_Ship_Have_Special_` for IDs `0x25`
and then `0x26`. If **either call** is nonzero,
it returns **0** immediately.

Otherwise it initializes an EDX slot index to 0 and a
BX result flag to 1, and scans slots 0 through 7 until
the flag changes or the eighth slot is complete. A
zero weapon ID or zero present byte skips that slot.
A weapon-category byte above 5 also skips it.

The exact original **six-case switch table** lives inside CODE
offset `0x194C7`. Its dispatch is the previously omitted
indexed jump at `0x1956D`, guarded by
`CMP CX,5; JA`.

| Category | Exact CODE target | Observed effect on result flag |
| ---: | --- | --- |
| 0 | `0x1959A` | Set result to **0**, independent of stock |
| 1 | `0x1957C` | Set result to **0** only if signed stock is positive |
| 2 | `0x1959A` | Set result to **0**, independent of stock |
| 3 | `0x19585` | Set result to **0** only when signed stock is positive **and** the ship `+0x20` byte equals the DATA word `0x218AC` |
| 4 | `0x1959E` | Positive stock sets result **0**. Otherwise, call `Check_For_Launched_Fighters_`; result becomes **1 only if no relevant launched fighter was found** |
| 5 | `0x19575` | Weapon ID `0x21` follows positive-stock rule; **other IDs immediately set result 0** |

The final return is `MOV EAX,EBX; LEAVE; POP ESI;
POP EDX; POP ECX; POP EBX; RET` at
`0x195C8..0x195CF`. The observed **1** means
the function sees no usable attack under its special,
weapon, and launched-fighter checks. It is not the
complete story about all tactical capabilities.

## `Check_For_Launched_Fighters_`

The original helper iterates missile records with BX
from 0 through **299** (`CMP BX,0x12C; JGE`),
looking for a matching signed ship owner at record
`+0x4`. When matched, it reads the missile's weapon
ID at `+0`, indexes the `_weapons` 28-byte
definitions, and returns **1** as soon as it finds
category **4**. Otherwise it returns 0 after 300.
The original loop does not inspect record index 300.
These bounds are retained in derived code.

## `Does_Combat_Ship_Have_Special_` and `Test_Bit_Field_`

The 75-byte special query reads two original bitfields
inside the selected 313-byte combat ship record:

- First bitfield begins at `ship+0x4C`.
- Second bitfield begins at `ship+0xB2`.
- `Test_Bit_Field_` takes the special bit index
  (original EDX), uses `index >> 3` for the
  selected byte and `index & 7` for the bit,
  then returns `(byte >> bit) & 1`.
- Special detection returns **1** only when its bit
  is set in the first field **and not set** in the
  second. Both criteria must hold.

For an installed/suppressed special with ID
`0x25` (37), the selected bit is byte 4, bit 5;
ID `0x26` (38) uses byte 4, bit 6.

**Important side-effect boundary:** the original
34-byte `Test_Bit_Field_` uses `PUSHA/POPA`
and a writable scratch DWORD at CODE offset
`0x1176EC` to return its result. The derived
C uses a pure bit calculation, omitting that
scratch write. This is functionally consistent
for this local return value, but does **not**
prove equivalence of every memory side effect,
concurrency/race behavior, or the full binary.

## Derived code and tests

- `decompilation/reconstructed/combat_ammo_v131.c`
- `tests/test_combat_ammo_v131.c`
- `tools/audit_combat_ammo_v131.py`
- `decompilation/reports/combat_ammo_audit_v131_2026-10-13.json`

The original combat code assumes valid ship IDs,
weapon indices, pointers and 300 missile slots.
The standalone derived C introduces explicit
host-pointer and array-count bounds checks
that return a separate INVALID_INPUT status;
this is a **deliberate safety change** rather
than a representation of original DOS error
semantics. Original `Does_Combat_Ship_Have_Special_`
uses `Test_Bit_Field_` to obtain results; it
does not copy/overwrite the special bitfield.
The derived C assumes all original-format
data buffers have already been initialized.

C regression exercises each of the six
category branches, positive/zero/negative stock,
both built-in special IDs, suppressed specials,
the 300th/301st missile-record boundary,
and malformed host inputs. It is **not**
differential execution of the DOS game.

## Remaining work

Cross-reference producers of the unnamed DATA word
`0x218AC`, the gameplay labels for weapon category
IDs 0–5, and all callers of these helpers.
Verify safe/wrapper behavior when original in-game
pointers or indices are malformed. Trace the rest
of tactical turn resolution, ammunition decrement,
combat movement and firing. Full-game decompilation
and a playable Game Lab engine remain incomplete.

No original executable bytes, LBX archives,
artwork or audio have been committed or
installed on the public Game Lab website.
