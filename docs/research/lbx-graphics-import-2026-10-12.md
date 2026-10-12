# Master of Orion II original graphics import – verified evidence

## Objective

Supply the native browser remaster with converted visual assets from a locally owned original game archive. The browser runtime must use normal browser-renderable artwork, **not LBX files, DOS/4GW, or the original executable**. This is a source-only offline converter, not an assertion of full game-asset support or a playable game.

## Original asset evidence (2026-10-12)

- User's existing 1996 game ZIP contains **373** files named `.LBX`, including fonts, ships, menus, logos, planet panels, sprites, and animation.
- Some `.LBX`-named files are **not LBX archives**; `INTRO.LBX` starts with an `SMK2` video signature. Header validation rejects non-LBX data rather than misinterpreting it.
- The archive was read directly from the user's machine. It was **not modified**, and no original/derived game artwork was added to GitHub.
- The `LOGO.LBX` entry 0 and `MAINMENU.LBX` entry 1 both decode to original 640×480 RGBA PNG with complete internal palettes.
- `LOGO.LBX` entry 1 declares **64 animation frames**, including first and final frames decoded and hash-checked.
- The original `MAINMENU.LBX` entry 0 has **50 animated frames but no internal palette**. The importer can verify indexed animation frames; it intentionally refuses to render them with invented colors until the external palette has been identified.
- `NEWGAME.LBX` entry 1 decodes to a 65×65 image using its 128-color embedded palette.

## Format basis and discovered discrepancy

Format reference: [Nick Bowler, liblbx image-format.txt](https://git.draconx.ca/gitweb/liblbx.git/tree/doc/txt/image-format.txt), retrieved from liblbx commit `62a3ff717b63511c94adb0876746852c13907f8b`. Independent earlier documentation: [MarcoKull/liblbx](https://github.com/MarcoKull/liblbx), [ModdingWiki LBX Format](https://moddingwiki.shikadi.net/wiki/LBX_Format).

Image header: little-endian width, height, frame count, lead-in, chunk size, flags; frame-offset table. Embedded palette uses RGB6 channels in four-byte records, scaled by 4 on conversion to 8-bit output. The container uses 0xFEAD magic and a monotonic absolute-offset directory.

**Discrepancy:** The format text describes the first byte of each RGB6 palette record as always `1`. In the original user's `LOGO.LBX`, `MAINMENU.LBX`, `RACES.LBX`, and `PLANETS.LBX` image palettes, **all inspected first bytes were actually `0`**. The importer deliberately supports `0` or `1` at this field, but uses the separate frame coverage mask (not that byte) for transparency. This interpretation has passed real-file conversion checks; any other values fail closed.

Compression: compressed frame drawing commands encode a uint16 pixel-run length, uint16 horizontal skip, optional raw pixel indices, padding for odd run lengths, vertical skip commands and end marker `(0,1000)`. Drawn pixels overlay the prior animation frame except where overwrite/chunk flags reset the frame. Raw frames use an exact width×height index buffer.

## Importer and tests

- `tools/lbx_graphics.py`: standard-library-only LBX image metadata/frame decoder and RGBA PNG writer, with size bounds, palette checks and no overwriting of existing outputs.
- `tools/test_lbx_graphics.py`: synthetic checks for archive validation, raw frames, compressed rows, transparency, animation delta, chunk reset, missing palettes, truncated data, and PNG dimensions. Optional real-game integration tests run when `MOO2_GAME_ARCHIVE` points to a lawful, local original ZIP. No proprietary fixture bytes are committed.
- `tools/run_tool_tests.sh` includes the generic decoder tests.

Example private conversion (requires embedded image palette):

```bash
python3 tools/lbx_graphics.py "$MOO2_GAME_ARCHIVE" --member mastori2/LOGO.LBX --entry 0 --frame 0 --output /tmp/moo2-logo-private.png
```

The output is for **private local comparison**, and must not be uploaded to GitHub or published on an open site.

## Real-file hashes (regression evidence, not distributed assets)

| Input image | Frame | Dimensions | Opaque pixels | Output RGBA SHA-256 |
| --- | ---: | --- | ---: | --- |
| LOGO.LBX entry 0 | 0 | 640×480 | 300,671 | `6659d5496e098ec1f9bc33ffc82bd77e3fca60e1a016bc643c4755d94e082190` |
| MAINMENU.LBX entry 1 | 0 | 640×480 | 307,200 | `fa88fcdb0d52b837eeb85c8dc73263e60a8a911e4406746c3582cb30a4b9cb4e` |
| LOGO.LBX entry 1 | 0 | 640×480 | 307,200 | `d483433bcbb422b9b02ecf9bae3332c50830b8b5696698ad3e629c00c35da68e` |
| LOGO.LBX entry 1 | 63 | 640×480 | 307,200 | `3afe946498bb3d843364af766626a4681828beb76762332c1014bd2e4ee6129b` |

These hashes prove reproducible bytes under **this decoder**; they do not independently prove that every palette and animation semantics match native 1996 rendering. A side-by-side visual comparison and source executable palette lookup remain necessary.

## Current limits and immediate next work

- Locate and validate **external** and mixed palettes, including MAINMENU entry 0, without falling back to guessed grayscale/color.
- Inspect multi-frame chunks, transparent sprites, retained previous pixels, and palette cycling against original.
- Add an offline import manifest and frame-animation exporter, then load converted sprites into the browser UI.
- Validate pixel-perfect vs Scale2x upscaling, UI text/readability, controller focus, and memory/frame times on an actual Xbox One Edge browser at 720p/1080p.
- Complete the gameplay engine, save/load, private HTTPS deployment, and end-to-end Xbox One controller checks; the project is not yet playable.
