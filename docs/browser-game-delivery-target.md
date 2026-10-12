# Master of Orion II browser-game delivery target

## Operative user objective (2026-10-12)

**Build a playable native-browser edition of Master of Orion II v1.31,
hosted on the user's own server, controllable entirely with an Xbox controller,
and with improved/upscaled graphics.**

This delivery target supersedes interpreting reverse-engineering completion,
or the existence of a static graphics preview, as completion of the project.
Qwen and its runtime are **not** part of the project.

## Acceptance criteria

A completed release must satisfy **all** of the following:

1. **Browser:** The real game starts and plays in a current desktop browser
   without DOSBox, ORION2.EXE, DOS/4GW or LBX files at runtime. It runs from
   the user's chosen server endpoint over HTTPS. Native-browser code is allowed;
   a desktop-only package or source-code workbench does not satisfy this.
2. **Gameplay parity:** Original v1.31 turn progression, galaxy generation,
   colony economy, diplomacy, AI, ship construction, tactical combat, technology,
   win/loss conditions, and original probabilities are reproduced and verified
   against reference evidence. Do not silently substitute a simpler 4X game.
3. **Xbox navigation:** Standard Xbox controller works in the browser for
   all major gameplay interactions and menus, including selecting, moving,
   backing out and turn handling. Keyboard/pointer fallbacks remain available;
   important interactions must not require precise pointer targeting.
   Verify with a real controller, not merely synthetic API tests.
4. **Graphics:** Aim for crisp 1280×960 (2×) presentation from original
   640×480 art; responsive scaling to other screen sizes and fullscreen mode.
   Offer pixel-perfect and carefully evaluated edge-aware artwork scaling.
   Retain readable fonts, palette semantics, animation timing, transparency,
   precise hitboxes, and original visual identity. Higher-quality art passes
   should not create gameplay changes. Evaluate performance on actual hardware.
5. **Save/load:** Persist and resume complete games with verified save/load
   integrity. Server-hosted access must not leak personal or proprietary assets.
6. **Deployment:** Install the playable result on the actual selected server,
   configure HTTPS and access control, and verify the deployed browser/gamepad
   route end-to-end. Server identity and URL must be confirmed before deployment.

## Asset and licensing boundaries

User-supplied original game ZIP contains 373 `.LBX` entries, including
artwork, fonts, sprites, sounds and animations; some items that end in
`.LBX` are not graphical archives. Use these assets only in an authorized
**local offline import pipeline**, retaining their palettes, animations and
frame metadata. Do not commit proprietary files or generated artwork to the
public GitHub repository, expose game archives on an unauthenticated server,
or claim rights that have not been established.

## Verified status as of 2026-10-12

- REA and Ghidra can analyze the canonical original v1.31 executable.
- LE extraction, relocation and initial gameplay-evidence regression tests pass.
- Source-only browser scaler and Gamepad API modules are in
  `web/graphics/`. Seven automated scaling/controller tests pass.
- The static graphics preview serves correctly from an HTTP server; actual
  browser rendering and a physical Xbox controller have not yet been tested.
- The original game artwork has **not yet been decoded into a verified
  browser-ready image pipeline**; no playable scene exists; server deployment
  has not been performed. Do not label these incomplete stages "done."

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
