# v1.31 switch-dispatch export repair — verified lower-bound reconciliation

**Date:** 2026-10-13  
**Goal:** complete the original-code control-flow map *before* adding
more Game Lab gameplay. No executable assets, game files, or copyrighted
graphics are published.

Original executable SHA-256:
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.
The audit uses original unrelocated LE CODE object 1,
**1,410,709 bytes**, rather than an emulator, game assets, or
unverified reconstructed C.

## Why previous switch totals were too low

The previous `decompilation/indirect_transfers.csv` was generated
from a resynchronized but still **linearly decoded** function-interval
disassembly. Watcom places four-byte jump tables inside the executable
CODE object. After one such table, linear disassembly can treat table
data as instructions or lose synchronization with the next
actual instruction. Consequently the earlier CSV recorded
**only 137 indirect JMPs**, and the associated switch CSV held
**135 bounded tables**, of which **118** originated in core game
modules. Verifying those 118 against original bytes was correct
but never established exhaustiveness.

The new audits scanned exact source **CS-prefixed x86 indexed JMP
opcodes**, independently decoded each site, cross-referenced the
Watcom function/module symbol, and verified original table DWORDs:

1. `2E FF 24 <SIB> <DWORD table offset>`: scale-four indexed
   **CS:[index*4+TABLE]**, e.g. game `Universe_Generation_`
   at original CODE `0x7DD4F`.
2. `2E FF A0 <DWORD table offset>`: pre-scaled **CS:[EAX+TABLE]**,
   e.g. `Do_Colony_Info_Military_Stuff_For_` at `0xACF3E`,
   where earlier code stores an index multiplied by four.
3. Bounds use locally observed unsigned `CMP/JA` sequences or,
   for one game table at CODE `0xE3C1`, the original
   `MOV ECX,14; REPNE SCASW` dispatch idiom.

All **68** newly detected game `2E FF 24` sites were absent
from the old switch inventory. **67** have local CMP/JA bound
evidence; the other is the fourteen-way word scan. Original
table entries across these 68 sites total **537**.

Two additional omitted pre-scaled dispatches were verified:

- **Game:** `Do_Colony_Info_Military_Stuff_For_`,
  site `0xACF3E`, table `0xACE92`, 4 entries
  (`0xACF45, 0xACF9D, 0xACF9D, 0xACF9D`).
  This source's index is multiplied by four at `0xACF2A`;
  the `CMP [EBP-0x10],3; JA` sequence guards table lookup.
- **Support:** `Farload_Library_Data_`, site
  `0x117190`, table `0x117145`, 4 allocation-mode
  entries. It is Watcom module **152**, *not* a game-code
  module; thus it must not inflate the game switch count.

## Authenticated reconciliation

A separate script rechecked all original table DWORDs from
the old and new sources, ensured **no site overlap**, checked
the reported source SHA, and counted game and support module
provenance independently.

| Original CODE-object switch tables | Verified distinct sites | Original DWORD case entries |
| --- | ---: | ---: |
| Earlier export: all modules | 135 | 1,080 |
| Additional game indexed tables | 68 | 537 |
| Additional game pre-scaled table | 1 | 4 |
| Additional support pre-scaled table | 1 | 4 |
| **Known original tables, reconciled** | **205** | **1,625** |

Reconciled **game** subset: **187** sites, **1,484**
case entries. Reconciled **support/runtime** subset:
**18** sites, **141** entries. The original previous
claim of "118 total game switches" is obsolete.

**This is a lower bound, not exhaustive original code coverage.**
The audit currently covers two common CS-prefixed indexed-jump
encodings and prior export sites. Other indirect JMP forms,
unclassified callbacks, dynamic target generation, and original
data embedded inside other symbols could be missed. Nearby
bounds/target DWORDs are *static provenance*, not proof that
all cases execute at runtime or that their bodies are fully
decompiled to equivalent C.

## Reproducible and GitHub-authoritative artifacts

- `tools/audit_omitted_game_switches_v131.py`
- `tools/audit_omitted_prescaled_dispatches_v131.py`
- `tools/reconcile_v131_switch_inventories.py`
- `decompilation/reports/omitted_game_switches_v131_2026-10-13.json`
- `decompilation/reports/omitted_prescaled_dispatches_v131_2026-10-13.json`
- `decompilation/reports/reconciled_switch_inventory_v131_2026-10-13.json`

Each script reads the authenticated local original and is
**read-only** with respect to the public game site. Future
global inventory generation must incorporate source-anchored
re-decoding, skip embedded case-DWORD regions, and rerun both
old and additive source-byte audits before replacing the
legacy CSV files. Do not silently overwrite original research
metadata with a smaller, less-complete export.

## New game-rule source recovery accompanying this audit

A verified new four-case switch in the **65-byte**
original `Get_Advanced_Government_Type_` is reconstructed
as isolated C:

- `decompilation/reconstructed/advanced_government_type_v131.c`
- `decompilation/annotated/advanced_government_type_v131.md`

This routine reads the signed byte at original `_player`
record offset `0x89F` (record stride `0xEA9`), divides
toward zero by 2, compares the low byte to 3 unsigned,
and returns 1/3/5/7 for cases 0/1/2/3, or 0 otherwise.
Negative raw **-1 returns 1** because truncation toward
zero produces index 0. The derived code compiled under
strict C11 flags and agreed with independently expressed
branch arithmetic across all 256 raw byte values; it has
not been differentially executed inside the original game.

## Next work

Continue translating original function bodies and their
calling conventions, focusing on newly recovered galaxy,
diplomacy, technology-value, combat and colony dispatches.
Reconcile other indirect opcode families before claiming an
exhaustive code-control map. Reconstruct original save/turn
and AI routines. No Game Lab website, Xbox controller or Qwen
configuration changes were made during this pass.
