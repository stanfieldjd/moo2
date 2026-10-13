# Game Lab website shell (provisional brand)

This is the site-wide front end, not the original-game research menu.
The intended destination is a new ISPConfig-managed virtual host on the
authorized Contabo server. No new ISPConfig site or TLS certificate has
yet been provisioned.

## Structure

- / — Game Lab homepage, with a directory for multiple game projects.
- /games/space-strategy/ — first project's landing/status page.
- /games/space-strategy/play/ — reserved for a future actual native game;
  this route does not exist yet and must not be advertised as playable.
- /games/<future-project>/ — future independent game detail pages.

The web/site/ directory is designed to be copied as an independent static
website root, unlike web/graphics/, which is a private engineering
preview that can load privately decoded copyrighted game imagery.
Do not copy the whole project workspace, web/graphics/, tools/,
proprietary assets, original executable or private user ZIP into
the public web root.

## Run locally

From the repository root:

    python3 -m http.server 8000 --bind 127.0.0.1 --directory web/site

Open http://127.0.0.1:8000/ for Game Lab; the first game project's page
is at /games/space-strategy/. This static site contains no playable
engine, game assets, telemetry, external JavaScript, fonts or stylesheets.

To test structure and simulated controller input:

    python3 tools/test_site_structure.py
    node --test web/site/tests/*.test.mjs

Xbox-style D-pad/left-stick moves between links, A selects and B returns;
keyboard arrows, Enter, Escape and conventional click/touch links are
available. Desktop/browser simulation is not proof that Xbox One Edge
delivers all input. Hardware verification remains a separate gate.

## Design and hosting constraints

- Game Lab is only a working umbrella title. Neither this name nor a
  future domain has been confirmed legally clear or registered.
- The current verified staging DNS candidate is
  gamelab.169-58-188-138.sslip.io. DNS resolution alone does not create
  an ISPConfig vhost, publicly trusted HTTPS certificate or protected site.
- Provision a separate ISPConfig website, with isolated document root
  and per-site logs. Never reconfigure or overwrite the Qwen site.
- Hosting the site and hosting potentially proprietary reconstructed
  game content are separate legal decisions. Verify redistribution rights
  before original assets or a derivative game become publicly accessible.
- For browser/Xbox hardware testing, use a real authorized server HTTPS
  URL with access controls. Do not expose private original imported art.
- All page links use relative URLs so a later domain change is simple.
