# moo2_remaster

This component contains the reverse-engineering/decompilation workbench and will contain the modern application layer.

## Current decompilation state

The official v1.31 executable is the current reference target. Original proprietary game executables/assets are deliberately excluded from GitHub.

Current local workbench head: `176c55f` (`Recover runtime initialization dispatch tables`).

Recent completed decompilation passes include:

- resynchronized decoding at surviving Watcom CODE entries;
- conservative CFG-derived function extents;
- synthetic entries for unnamed direct-call targets;
- switch-table recovery and indexed-dispatch recovery;
- exact CFG-reachable instruction corpus generation;
- static indirect-call slot resolution;
- indexed indirect-call table resolution;
- indexed helper-table detection;
- runtime initialization dispatch-table recovery;
- Watcom module/global/local/type/line metadata extraction;
- module ownership and inter-module call-graph generation.

The current working estimate before the latest indirect-dispatch passes was 87% complete. This number is intentionally not advanced here until the remaining indirect-control-flow inventory is remeasured after the latest passes.

## Repository policy

Do not commit original `ORION2.EXE`, LBX archives, original artwork/audio/video/manuals, or other proprietary game content. Commit only our tools, derived metadata that does not reproduce proprietary content, behavioral specifications, tests, and clean remaster source.

## Final application responsibilities

- rendering;
- interface and accessibility;
- input;
- audio;
- platform integration;
- asset import and conversion;
- save-game presentation;
- diagnostics.

The final native application must consume `moo2_core` without changing verified gameplay rules.
