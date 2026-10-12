# Browser graphics and Xbox controller preview

This is an engineering preview, **not yet a playable game**. Its source code contains no Master of Orion II artwork, and no original game assets should be committed to GitHub.

## Run

From the repository root:

    python3 -m http.server --bind 127.0.0.1 8000 --directory web/graphics

Then open http://localhost:8000/ and select a PNG, WebP, BMP or JPEG exported locally from a lawfully owned game copy. The browser reads the picture locally without uploading it.

Rendering uses original **640 × 480** logical coordinates, responsive 4:3 fitting, and a target **1280 × 960 (2×)** presentation.

Modes:
- Sharp pixels (nearest neighbor) for bitmap fonts, UI and original pixel art.
- Edge-aware Scale2x/EPX for sprites and illustrations; exact RGBA matches and no new colors.
- Smooth bilinear interpolation for comparison; may blur text.

Xbox standard Gamepad API input: left analog stick / D-pad moves a test cursor; A activates a test selection; B invokes a test back action. Keyboard arrows, Enter and Escape are supported as alternatives. No real game actions, Xbox hardware validation or save/load behavior are implemented yet.

## Automated tests

    node --test web/graphics/tests/*.test.mjs

Seven initial tests check alpha-preserving scaling, edge-aware corners, fit-to-screen geometry, Xbox button edge-triggering and analog/D-pad bounds. These are synthetic tests; real browser/controller verification remains outstanding. **Actual Xbox One Edge console compatibility is a mandatory separate acceptance gate.** Desktop Edge with an Xbox controller does not satisfy it. Console Edge might reserve B/back or other controls; whether raw Gamepad API, keyboard, or pointer input reaches the webpage is not yet verified. Xbox One must be tested through a secure HTTPS deployment accessible from the console, without installing a game or using developer mode.

## Production constraints

Original v1.31 gameplay is canonical. The final game is a native browser game hosted on an authorized private server, with graphical modernization and Xbox controls. It **must not** need ORION2.EXE, LBX archives, DOS/4GW or DOSBox at runtime. Original LBX art needs a separate offline importer with palette, animation and frame integrity validation; proprietary game files and derived copyrighted assets stay outside the public source repository and must not be made openly downloadable.

Next: finish a verified offline LBX sprite decoder and graphics importer, wire the native game scene, integrate controller focus/activation, save/load, and deploy an authenticated preview on the selected host. Do not call the engineering preview a finished game.

## Original animated main-menu engineering preview (local only)

The source-only test page `menu.html` provides working Graphics and Controller
Test panels. Xbox A activates the focused item, B returns, D-pad/left stick
selects items, and Xbox A toggles the scaling option when selected inside the
Graphics panel. Keyboard and pointer alternatives are available.

**New Game and Load Game remain disabled** until native gameplay exists.
This UI is an input/graphics milestone, **not** a playable game.

To prepare the original 50-frame main-menu animation **locally**, from the
user's lawfully held original ZIP (never add converted assets to GitHub):

```bash
python3 tools/export_lbx_animation.py "$MOO2_GAME_ARCHIVE"   --member mastori2/MAINMENU.LBX --entry 0   --palette-member mastori2/FONTS.LBX --palette-entry 6   --output-dir web/graphics/private-assets/mainmenu

python3 -m http.server --bind 127.0.0.1 8000 --directory web/graphics
```

Open `http://127.0.0.1:8000/menu.html` from that machine. The importer
refuses an existing output directory and performs no uploads. The entire
`web/graphics/private-assets/` directory is gitignored; it contains
copyrighted converted game artwork for **private local testing only**.

The "Play animation preview" button uses a user-selectable preview rate
of eight frames per second, **not an established original-game timing**.
A true Xbox One console test requires an authorized HTTPS server the
console can reach. Do **not** bind a public test server or copy the
private graphics onto an open website. Browser hardware and save/load
have not yet been tested.
