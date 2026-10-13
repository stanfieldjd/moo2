# Game Lab website (provisional name)

A separate ISPConfig-managed website is deployed on the user's Contabo
server at https://gamelab.169-58-188-138.sslip.io/ (website ID 4).
It serves the public Game Lab site without a login; HTTPS is verified.
The Qwen ISPConfig website is a separate site and must not be modified.

## Routes and release truth

- `/` — umbrella homepage.
- `/games/space-strategy/` — game status page: **not yet playable**.
- `/games/space-strategy/controller-test/` — input/focus diagnostic.
  The user verified the Xbox One controller test starts working after
  holding the controller Start/Menu button for approximately 3 seconds
  to access Edge Game Controls; this does not prove gameplay compatibility.
- `/games/space-strategy/engine-lab/` — controller-first **non-game**
  inspection screen with five *synthetic* systems. It now includes a
  **synthetic workforce record editor**: select a person, change the packed
  job-slot bits on a clone, and inspect original-routine workforce totals,
  per-worker yields and food/industry upkeep. The editor does not establish
  the original job-reassignment procedure or calculate full colony output.
  Changes remain tab-local and reset on reload. No colony turn, original
  galaxy generator, save/load, combat or gameplay is implemented there.
- `/games/space-strategy/play/` — intentionally absent (HTTP 404)
  until real gameplay exists.

## Safe deployment manifest

Only publish these site assets and any subsequently reviewed production
files; **do not copy the entire `web/site` tree to the public webroot**,
because that previously exposed `README.md` and test scripts.

- `web/site/index.html` → `/index.html`
- `web/site/favicon.svg` → `/favicon.svg`
- `web/site/site.css` → `/site.css`
- `web/site/site.mjs`, `web/site/site-nav.mjs` → same root paths
- `web/site/games/space-strategy/index.html` → matching path
- `web/site/games/space-strategy/controller-test/{index.html,probe.mjs}`
  → matching paths
- `web/site/games/space-strategy/engine-lab/{index.html,model.mjs,lab.mjs,colony-lab.mjs}`
  → matching paths
- **Only** `web/engine/colony-yields.mjs` → `/engine/colony-yields.mjs`
  (required public ES module import for the test deck).
- Reviewed engine dependencies only:
  `web/engine/{colony-economy-inspect,colony-workforce,colony-records,colony-maintenance,colony-tax}.mjs`
  → matching `/engine/` paths for the workforce inspector. They contain
  independently verified routines and no original game binaries or images.

The live ISPConfig docroot is `/var/www/clients/client0/web4/web`.
Deployment changes are made on the authorized server using source
identified by its exact Git commit, with tests before publication.
Do not overwrite existing `.htaccess` or unrelated ISPConfig content.
Never include `web/graphics/private-assets`, reverse-engineering targets,
private original-game binaries, original game art, `tools/`, `tests/`,
`README.md` or proprietary user-supplied archives in a public deployment.

## Development and tests

For just the static homepage, serve `web/site` locally as before.
For the engine laboratory, its imports must resolve both the site and
`web/engine` trees. Start the **loopback-only** development server at
the `web` directory, and open `/site/games/space-strategy/engine-lab/`:

    python3 -m http.server 8000 --bind 127.0.0.1 --directory web

Production places the site at `/` and the verified yield module at
`/engine/colony-yields.mjs`. To run the tested JavaScript suite:

    node --test web/engine/tests/*.mjs web/site/tests/*.test.mjs
    python3 tools/test_site_structure.py

Tests are not a substitute for inspecting the page in a real browser or
testing controller input on the Xbox One console. In particular, the
new workforce UI/controller navigation still needs physical-console testing.
  The UI must permit controller focus scrolling to controls below the fold.

## Boundaries

Game Lab is a working title and its permanent registered domain remains
undecided. Neither the original game's protected artwork nor its executable
is publicly hosted. Formula tests and engine-lab scaffolding are not evidence
of completed game parity. The existing Qwen site and runtime are outside
this project.
