# MOO2 v1.31 — planet maximum population for a player

**Status:** The original 206-byte named Watcom `Planet_Max_Population_For_Player_` at CODE `0xD0B4F` is reconstructed as source-derived C. The direct numerical callees `Size_And_Climate_Race_Pop_Limit_` (188 original bytes) and `Colony_Race_Pop_Limit_` (81 bytes, itself depending on the recovered 49-byte maximum-population helper) are implemented and linked. The function no longer depends on hypothetical population-capacity formulas.

Authenticated local original executable `ORION2.EXE` SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

Original 206-byte complete source body SHA-256:
`00adaceecdeea9bb7cd18420bf11803ee6d784361fb2282b2581b4122f72b886`.

The original code uses an **external shared Watcom return** at CODE `0xCEB17`: `LEAVE; POP EDI; POP ESI; POP ECX; POP EBX; RET` (six authenticated bytes). An apparent short symbol boundary does not mean its procedure lacks a return.

`tools/audit_planet_max_population_v131.py` authenticates the complete 206-byte body, both named original helper bodies, original `_colony` and `_player` global addresses, four direct call edges and **72 exact source machine instructions**, including the shared exit. Machine report: `decompilation/reports/planet_max_population_v131_2026-10-16.json`.

## Original control flow

Original input EAX is a planet record pointer; EDX is the requested player race index.

**Uncolonized or inactive colony:** If signed planet WORD `+0x00 == -1`, or the planet's colony record has BYTE `+0x06` nonzero, the original returns the low-AX signed capacity from `Size_And_Climate_Race_Pop_Limit_(planet BYTE+5, planet BYTE+8, requested race)`, plus **5** when the *requested player's* technology BYTE `+0x11A ==3`. The original looks up the planet's colony index in a 0x169-byte colony-record array before testing the +0x06 state.

**Established colony with no population:** When the referenced colony BYTE `+0x06` equals zero but BYTE `+0x0A` population count is zero, original calls `Colony_Race_Pop_Limit_(colony,requested race)` and returns the signed low-AX result. The local colony wrapper applies technology from the *colony's owner*, which may differ from the requested player race.

**Established occupied colony:** The original clears a ten-byte race-class marker array, reverse-reads the four-byte population records at colony `+0x0C`, and sets markers using each record's DWORD low nibble. It then scans represented classes **9, 8, ... 1**, calls `Colony_Race_Pop_Limit_(colony,class)` for each, sign-extends its low AX, and takes the **maximum** (starting with zero).

**Notable source behavior:** Class **0** is marked but never examined because the original loop decrements ECX from 10 and ends when ECX reaches zero. An occupied colony with only class-0 population therefore returns zero. The port preserves this rather than assuming all represented classes participate.

## Files and verification

- `decompilation/reconstructed/planet_max_population_v131.c` and `.h`
- `tests/test_planet_max_population_v131.c`
- `tools/audit_planet_max_population_v131.py`
- `decompilation/reports/planet_max_population_v131_2026-10-16.json`
- `decompilation/reconstructed/size_climate_pop_limit_v131.c`
- `decompilation/annotated/size_climate_pop_limit_v131.md`

Regression checks cover uncolonized planets and technology, planet condition +0x06, unpopulated colonies, owner-versus-requested-race technology, occupied colonies with multiple represented races, class-0 omission and malformed-state bounds. The test passes strict C11/AddressSanitizer/UndefinedBehaviorSanitizer. These are source-consistency host tests, **not** a DOS differential test against the original game's runtime state.

The remaining colony-production and turn progression systems still require extensive reconstruction. The game is **not** fully decompiled or playable in the browser. Original copyrighted executable/artwork remain on the authorized local machine. No Game Lab website, Xbox controller or Qwen changes occurred.
