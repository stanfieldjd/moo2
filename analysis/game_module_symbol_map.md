# MOO2 v1.31 Game-Module Symbol Map

This index separates symbols belonging to the original MOX gameplay/application modules from linked support libraries. It is derived from the executable's Watcom module index plus global-symbol `mod_index`; symbol kind is decoded as a bitfield (CODE=0x04, DATA=0x02, STATIC=0x01).

Generated datasets:
- `decompilation/game_module_symbols.csv` — every global/static symbol attributed to a MOX module.
- `decompilation/game_module_manifest.csv` — per-module code/data counts.

This map is the primary module/function ownership layer for subsequent call-graph reconstruction. Rich local/type debug information from WLIBS must not be projected onto these MOX modules.
