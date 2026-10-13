# Galactic Turn Lab browser-game development target (provisional title)

## Operative user objective (2026-10-12)

**Research and implement a native-browser space-strategy game, using Master of Orion II v1.31 as the fidelity reference where legally permitted,
hosted on the user's own server and playable in both a computer browser and
Microsoft Edge on the user's Xbox One console, using the Xbox One controller,
with improved/upscaled graphics.**

This delivery target supersedes interpreting reverse-engineering completion,
or the existence of a static graphics preview, as completion of the project.
Qwen and its runtime are **not** part of the project.

## Acceptance criteria

A completed release must satisfy **all** of the following:

1. **Browser:** The real game starts and plays in a current computer browser
   **and in Microsoft Edge on an actual Xbox One console**, without installing
   a game, DOSBox, ORION2.EXE, DOS/4GW or LBX files on either client. It runs
   from the user's chosen server endpoint over HTTPS. A native-browser app is
   permitted; a desktop-only package, controller-on-PC test or source-code
   workbench does not satisfy this.
2. **Gameplay parity:** Original v1.31 turn progression, galaxy generation,
   colony economy, diplomacy, AI, ship construction, tactical combat, technology,
   win/loss conditions, and original probabilities are reproduced and verified
   against reference evidence. Do not silently substitute a simpler 4X game.
3. **Xbox navigation:** The Xbox One's own controller works **inside Edge on
   that Xbox One** for all major gameplay interactions and menus, including
   selecting, moving, backing out and turn handling, without requiring a
   keyboard, mouse or second device. Computer-browser keyboard/pointer
   fallbacks remain available. Important interactions cannot require precise
   cursor positioning. Console Edge may intercept buttons such as B for
   browser navigation, or not expose a standard Gamepad API mapping; test the
   real browser's Gamepad API, keyboard and pointer events rather than
   assuming desktop Edge behavior applies. Do not count a synthetic-input
   or controller-on-PC test as console acceptance.
4. **Graphics:** Aim for crisp 1280×960 (2×) presentation from original
   640×480 art; responsive scaling to computer monitors and Xbox One TV
   output, including 720p/1080p displays, safe-area margins, and readable
   couch-distance interface text. Fullscreen must be tested on Xbox Edge;
   browser restrictions may apply. Offer pixel-perfect and carefully evaluated
   edge-aware artwork scaling. Retain readable fonts, palette semantics,
   animation timing, transparency, precise hitboxes, and original visual
   identity. Higher-quality art passes cannot change gameplay. Evaluate
   frame rate, memory usage, performance and input delay on actual hardware.
5. **Save/load:** Persist and resume complete games with verified save/load
   integrity. Server-hosted access must not leak personal or proprietary assets.
6. **Deployment:** Install the playable result on the existing **Contabo ISPConfig server**, using a **new, separate ISPConfig-managed website** for Galactic Turn Lab (provisional title), without modifying the Qwen site. Avoid the original game's trademarks in public branding. The permanent domain has **not been selected, cleared or registered**; do not assume ownership. Once a hostname is selected,
   configure HTTPS and access control, and verify the deployed route end-to-end
   from a computer **and the Xbox One Edge browser**, over the normal network
   without localhost, developer mode or local software installation. Verify
   navigation, settings, fullscreen or best available display, save/load,
   resume after browser reload, and an extended play session using only the
   console controller. Server identity and URL must be confirmed before deployment.

## Xbox One console compatibility gate

**The console itself is a required target, not just its controller.**
Microsoft announced the updated Edge browser for all Xbox consoles in
September 2021: https://news.xbox.com/en-us/2021/09/23/september-2021-xbox-update/
Edge supporting the Gamepad API on PCs does **not** establish that game
pages on Xbox One receive the controller. The browser can claim some
buttons for its own interface, and the console may expose a pointer,
keyboard events, gamepad events, or a combination.

Before promising native-controller gameplay, run a private HTTPS input
diagnostic **on the Xbox One**, triggered by a user button press, and record:

- Edge/console build and `navigator.getGamepads` availability, including
  permission errors or empty reports after activation;
- Controller A/B, D-pad, both sticks, shoulder buttons and Menu/View event
  delivery, plus any browser-level back/focus behavior;
- Focus changes, audio initiation, suspend/resume, fullscreen and
  TV-safe graphics geometry.

Determine the usable input pathway from the observed console results and
implement a consistent controller-first focus model. Do **not** claim that
keyboard-generated events or browser pointer emulation substitute for raw
Gamepad API access until observed and tested on the console. Do not ask for
developer-mode installations to play the game. An HTTPS server accessible
from the console is required for the end-to-end test; no console hardware
test has yet occurred.

## Asset and licensing boundaries

User-supplied original game ZIP contains 373 `.LBX` entries, including
artwork, fonts, sprites, sounds and animations; some items that end in
`.LBX` are not graphical archives. Use these assets only in an authorized
**local offline import pipeline**, retaining their palettes, animations and
frame metadata. Do not commit proprietary files or generated artwork to the
public GitHub repository, expose game archives on an unauthenticated server,
or claim rights that have not been established.


The chosen hosting platform and outstanding domain are documented in [ISPConfig deployment plan](deployment/ispconfig-browser-hosting.md). A separate rights review must precede any public use of the original game's protected expressive assets; owning a game copy is not redistribution permission. Work on the native engine and UI can proceed before hostname selection. Do not create a placeholder public hostname or issue a certificate without a real approved hostname.

## Verified status as of 2026-10-12

- REA and Ghidra can analyze the canonical original v1.31 executable.
- LE extraction, relocation and initial gameplay-evidence regression tests pass.
- Source-only browser scaler and Gamepad API modules are in
  `web/graphics/`. Seven automated scaling/controller tests pass.
- The static graphics preview serves correctly from an HTTP server; actual
  browser rendering and a physical Xbox controller have not yet been tested.
- A validated private **offline LBX-to-PNG importer** handles embedded and verified external RGB6 palettes. All 50 main-menu frames were privately converted using `FONTS.LBX` entry 6; the new browser menu prototype renders the animation locally with Xbox-oriented Graphics and Controller Test panels. Original animation timing, actual browser/console hardware validation and full game-engine integration remain outstanding. See [external palette and menu evidence](research/lbx-external-palette-console-menu-2026-10-12.md).
- The native browser engine includes isolated, evidence-based v1.31 colony food-per-farmer, industry-per-worker, research-per-scientist and industry-to-tax operations. An explicit byte-record adapter reads their known colony, planet and race fields; all 35 combined JavaScript tests pass. These are **not** a complete colony turn or playable game; see [native record adapter evidence](research/native-colony-yields-and-records-2026-10-12.md).
- The native engine now also has separately tested packed-population **food and industry upkeep scans** with original race weights, special categories, byte counters, and conservative record-bounds checking. Nine additional tests passed. The original anomaly/event guard and job assignment are still unresolved. The full remote original-executable suite has **not been re-run after this addition** because the `penguin` command connection timed out; see [packed upkeep evidence](research/native-packed-population-upkeep-2026-10-12.md).
- A verified read-only workforce census now decodes v1.31 packed colonist job-slot bits 7–8 and the production-scan inclusion bit 9; a separate economy inspector combines the census, known per-unit rates, and food/industry upkeep without claiming full production totals. Ten new JavaScript tests and an original-executable opcode regression passed, bringing the local JavaScript suite to **54 passing tests**. See [workforce evidence](research/native-workforce-census-2026-10-12.md).
- The verified production dispatch table now identifies job 0 as food, 1 as industry, 2 as research, and 3 as a null dispatch. An isolated native minimum-output wrapper and original-byte table/fixup regression were added. The full local suite passes **60 JavaScript tests**; the three dispatched production formulas and full colony turn remain unresolved. See [dispatch evidence](research/native-base-production-floor-2026-10-12.md).
- Original-byte verification now covers three additional empire-production bonus routines (food, industry, research). The native browser engine has uncached bonus functions and a read-only original-record adapter with explicit climate globals. Seventeen new JavaScript tests and an executable regression pass, bringing the **latest combined JavaScript suite to 77 tests**. Cache invalidation, complete colonist output and colony turn processing remain unresolved. See [bonus reconstruction](research/native-empire-base-bonuses-2026-10-12.md).
- No playable scene exists; original assets have not been deployed to the server, and Xbox One Edge has not yet been tested with hardware. Do not label these incomplete stages "done."

## Immediate engineering order

1. Build and validate original LBX graphic-frame, palette, alpha and animation
   decoding into local browser asset representations (without publishing files).
2. Use the preview harness to compare real original images under sharp and
   edge-aware 2× scaling; test text, small icons and animation fidelity.
3. Integrate game controller navigation/focus with the first stateful native
   gameplay scene, then implement the complete native rules engine.
4. Establish save/load and input accessibility and test both against original
   game behavior.
5. Confirm target server and deploy a private HTTPS end-to-end browser build,
   with actual Xbox controller tests. Repeat until all acceptance criteria pass.

Continue from the last verified artifact and test result; do not restart
working reverse-engineering or mistake research output for a playable release.
