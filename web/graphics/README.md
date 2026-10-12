# Browser graphics and Xbox controller preview

This is an engineering preview, **not yet a playable game**. Its source code contains no Master of Orion II artwork, and no original game assets should be committed to GitHub.

## Run

From the repository root:

    python3 -m http.server 8000 --directory web/graphics

Then open http://localhost:8000/ and select a PNG, WebP, BMP or JPEG exported locally from a lawfully owned game copy. The browser reads the picture locally without uploading it.

Rendering uses original **640 × 480** logical coordinates, responsive 4:3 fitting, and a target **1280 × 960 (2×)** presentation.

Modes:
- Sharp pixels (nearest neighbor) for bitmap fonts, UI and original pixel art.
- Edge-aware Scale2x/EPX for sprites and illustrations; exact RGBA matches and no new colors.
- Smooth bilinear interpolation for comparison; may blur text.

Xbox standard Gamepad API input: left analog stick / D-pad moves a test cursor; A activates a test selection; B invokes a test back action. Keyboard arrows, Enter and Escape are supported as alternatives. No real game actions, Xbox hardware validation or save/load behavior are implemented yet.

## Automated tests

    node --test web/graphics/tests/*.test.mjs

Seven initial tests check alpha-preserving scaling, edge-aware corners, fit-to-screen geometry, Xbox button edge-triggering and analog/D-pad bounds. These are synthetic tests; real browser/controller verification remains outstanding.

## Production constraints

Original v1.31 gameplay is canonical. The final game is a native browser game hosted on an authorized private server, with graphical modernization and Xbox controls. It **must not** need ORION2.EXE, LBX archives, DOS/4GW or DOSBox at runtime. Original LBX art needs a separate offline importer with palette, animation and frame integrity validation; proprietary game files and derived copyrighted assets stay outside the public source repository and must not be made openly downloadable.

Next: finish a verified offline LBX sprite decoder and graphics importer, wire the native game scene, integrate controller focus/activation, save/load, and deploy an authenticated preview on the selected host. Do not call the engineering preview a finished game.
