# Original v1.31 origin of research planet-special codes 10 and 11

## Canonical evidence

Source: locally supplied official v1.31 `ORION2.EXE` SHA-256 `4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`, Watcom LE CODE SHA-256 `f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837`. Original binary, extracted proprietary bytes, and game assets remain outside Git.

Reproducer: `tools/audit_research_planet_special_origin_v131.py`; machine-readable source hashes, exact opcode bytes, original named callgraph edges and controlled fixtures: `decompilation/reports/research_planet_special_origin_v131_2026-10-16.json`.

Six complete original Watcom named bodies are authenticated (original CODE addresses): `Init_New_Game_` `0x2479` (801 bytes); `Generate_Home_Worlds_` `0x6B8CD` (745); `Modify_Home_Worlds_` `0x6C4AF` (576); `Generate_Orion_` `0x6BBBC` (459); `Enforce_Artifacts_Special_` `0x6B5B2` (33); `Colony_Research_Per_Scientist_` `0xCFDC6` (177). Original named source headers, extents and complete SHA-256 values are checked against the local original CODE image.

## Direct new-game call chain and original assignments

The original CODE instruction `0x252A` in `Init_New_Game_` directly calls `Generate_Home_Worlds_`. That routine directly calls `Modify_Home_Worlds_` at CODE `0x6BB46` and `Generate_Orion_` at CODE `0x6BBA7`. All three directed edges are verified against both the exact original machine-code CALL displacement and `decompilation/game_call_edges.csv`.

**Planet code 10 — original home-world construction:**

- In `Modify_Home_Worlds_`, CODE `0x6C614–0x6C61F` uses original player stride `0xEA9`, DATA global `_player` `0x1FF98` and BYTE `player+0x8AF`; it compares the byte against zero.
- CODE `0x6C627` jumps over the assignment when that byte is zero. When the flag is nonzero, CODE `0x6C629–0x6C635` computes a 17-byte planet record stride, reads original DATA `_planet` pointer at `0x1B0D4`, and writes **planet BYTE+0x0F = 10**.
- In the same condition, CODE `0x6C63A–0x6C645` writes 10 to a corresponding 0x71-byte star record BYTE+0x28, based on original DATA `_star` pointer at `0x1B06C`.
- The independent named `Enforce_Artifacts_Special_` helper (CODE `0x6B5B2`) also writes planet BYTE+0x0F = 10 at CODE `0x6B5BC` using the **same `_planet` global and 17-byte stride**. No direct caller was established in the static named callgraph for this helper, so it is not assumed invoked on any particular normal game path.

**Planet code 11 — original Orion construction:**

- `Generate_Orion_` computes the original planet record using the same DATA `_planet` at `0x1B0D4`. At CODE `0x6BD17`, it writes **WORD planet+0x00 = 0xFFFF**, conventionally -1 when interpreted signed. This is an *initial unowned marker*, not evidence of an immediately populated/colonized Orion planet.
- At CODE `0x6BD3E` it writes **planet BYTE+0x0F = 11**; preceding nearby source operands initialize other original planet fields. The call from `Generate_Home_Worlds_` is source-authenticated. Whether or how later code allows colonization/research on Orion remains separately unresolved.

**Original scientist bonus consumer:**

- `Colony_Research_Per_Scientist_` CODE `0xCFE35` reads the colony's planet-id signed WORD, CODE `0xCFE39` multiplies by **17**, CODE `0xCFE3C` reads the **same DATA global** `_planet`, and CODE `0xCFE42` reads planet BYTE+0x0F.
- CODE `0xCFE46` compares against 10, with source `INC EDX; INC EDX` at `0xCFE54–0xCFE55` producing **+2**. CODE `0xCFE4C` compares against 11, leading to original `ADD EDX,5` at `0xCFE65`.
- If a non-null breakdown pointer exists, CODE `0xCFE5A` or `0xCFE6C` additionally writes +2 or +5 to DWORD breakdown+0x226; this exact field is the previously authenticated research-production numeric alias. The bonus and the optional breakdown write are distinct source effects.

These are **real code paths writing the exact 10 and 11 values** to the same planet field read by the research calculation. They are not fictitious test constants.

## Evidence limits and next source obligations

The auditor verifies **28 exact original opcode-byte checkpoints**, original function and CODE hashes, all three named direct call edges and 13 controlled synthetic branch/value checks. The original game-state domains and runtime behaviors are **not** inferred from the small tests.

It remains unproved that an actual saved/active **colony** with special value 10 or 11 simultaneously satisfies the synthetic research example's population tags, government group, gravity factor, technology/settings bytes, occupation and branch guards. The initialized Orion field explicitly indicates unowned at construction; do not present it as immediately colonized. The exact gameplay significance of player BYTE+0x8AF is not assigned a further named ability without independent evidence.

A real DOS original runtime comparison and a valid, traceable original save state are still required to label the earlier optional-breakdown-dependent calculation a user-visible gameplay defect. No original game, assets, server, website or gameplay rule has been changed; the historical 87% overall executable estimate is not recalculated.
