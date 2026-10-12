# MOO2 external palette and Xbox-oriented menu milestone — 2026-10-12

## Confirmed engineering progress

A verified offline importer now decodes original `MAINMENU.LBX` entry 0,
using the correct external RGB6 palette from `FONTS.LBX` entry 6.
All 50 original 640×480 frames have been privately converted to PNG files,
with SHA-256 fingerprints and frame-order metadata. Neither original LBX
data nor converted artwork was committed to GitHub.

Local browser-serving checks returned HTTP 200 for the menu page, modules,
animation manifest, and first and last menu frames. Frame file hashes
matched the import manifest. The console-oriented `web/graphics/menu.html`
provides controller-navigable Graphics and Controller Test panels.
`New Game` and `Load Game` are intentionally disabled: **no playable
gameplay engine has yet been implemented**.

## Original palette provenance and verification

The original main menu entry has no embedded palette. Per
[liblbx's MOO2 file catalogue](https://git.draconx.ca/git/liblbx.git)
(commit `62a3ff717b63511c94adb0876746852c13907f8b`),
`FONTS.LBX` entry 6 provides the palette. Its 256 RGB6 records
start with first byte `1` whereas several embedded image palettes
observed in the original archive used first byte `0`. The strict
importer now handles both forms without substituting guessed colors.

- Menu animation original entry 0: 50 frames, 640×480.
- Frame 0 RGBA SHA-256: `fa88fcdb0d52b837eeb85c8dc73263e60a8a911e4406746c3582cb30a4b9cb4e`.
- Frame 49 RGBA SHA-256: `2420bc887b5032b79579afb8a2dff97fedf9684d9587fe66a8d83609a9c97239`.
- Generated frames reside only under the private local
  `web/graphics/private-assets/mainmenu/` directory, which is ignored
  by Git. The exporter refuses an existing destination.
- 10 LBX decoder regression tests include actual original menu palette
  and animation hashes. Three animation-exporter safety tests and
  19 JavaScript graphics/input/menu tests also passed.
- Browser menu animation preview uses an *arbitrary* eight frames/sec.
  **Original animation timing has not been proven.**

## Reproduce privately

```bash
python3 tools/export_lbx_animation.py "$MOO2_GAME_ARCHIVE" \
  --member mastori2/MAINMENU.LBX --entry 0 \
  --palette-member mastori2/FONTS.LBX --palette-entry 6 \
  --output-dir web/graphics/private-assets/mainmenu
python3 -m http.server --bind 127.0.0.1 8000 --directory web/graphics
```

On the same computer visit
`http://127.0.0.1:8000/menu.html`. This is an
engineering preview on a loopback-only local HTTP listener, **not** a
publicly deployed website and **not yet the game**. Proprietary assets
must not be placed on a public or unauthenticated service.

## Remaining gates

The native v1.31 gameplay engine, saved games, actual browser visual UI
testing, validated original frame timing, controller-tested Xbox One
Edge compatibility, and authorized HTTPS server deployment remain
outstanding. No claim of gameplay parity or console playability is made.
