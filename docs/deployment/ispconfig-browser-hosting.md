# ISPConfig hosting plan — Master of Orion II browser edition

## Binding deployment decision (2026-10-12)

The user has explicitly selected **the existing Contabo server's ISPConfig
installation** to host the Master of Orion II browser game. Create a **separate
ISPConfig-managed website/vhost for the game**. Do not install the game into
the existing Qwen website, alter Qwen's virtual host, or repurpose any Qwen
service or document root.

**Preferred permanent domain (user delegated choice): `orion2web.com`.**
This is a recommendation only, NOT a registered/owned domain. Availability
could not be confirmed by authoritative RDAP; an absent A record does not
establish that registration is possible. Confirm registrar availability,
trademark/branding suitability and purchase authorization before registering.
Do not set production DNS or attempt certificate issuance yet.

**Verified free temporary DNS candidate:**
`orion2.169-58-188-138.sslip.io`, resolving to the Contabo IPv4 address
`169.58.188.138` during an authorized read-only check. sslip.io's DNS service
is operated by a third party; this hostname is suitable only for optional
staging, not a permanent identity. A valid HTTPS certificate, a separate
ISPConfig vhost, authentication, and actual Xbox One browser tests do not yet
exist. Do not treat working DNS resolution as site readiness.

The desired browser game must run from the server in computer browsers **and
Microsoft Edge on the Xbox One itself**, using the console's Xbox controller.
The game should retain original v1.31 rules and use enhanced/upscaled graphics.
No local emulator or console install is the finished product.

## Read-only server observations

Inspection of the authorized host on 2026-10-12 established:
- Contabo host with an active ISPConfig installation;
- Apache and MariaDB active;
- a preexisting **Qwen ISPConfig website**, which must remain untouched;
- **no distinct Master of Orion II ISPConfig site** yet provisioned;
- adequate free disk space on that host at inspection time for source-only
  staging; capacity and permissions must be rechecked before copying assets.

These observations do **not** constitute installation, DNS provisioning,
a valid HTTPS endpoint, browser hardware validation, or completion of the game.

## Staging and provisioning sequence

1. Continue the native browser gameplay and input implementation in the
   repository without tying the code to an undecided hostname. Use relative
   asset URLs and avoid hardcoded origins.
2. Keep repository source files, offline art-import tooling and
   privately converted copyrighted artwork separate. No original LBX
   archives, executable, or derived copyrighted artwork belongs in public
   GitHub. Do not expose private assets via an unauthenticated web root.
3. Once a temporary testing hostname is explicitly approved **or** the
   permanent domain is selected, create a **new, dedicated ISPConfig site**
   with its own document root, site ownership and logs. Do not overwrite
   other configured sites. A fully operational web vhost requires a hostname.
4. Configure DNS to the actual server, then a publicly trusted TLS
   certificate for the selected hostname, HTTPS redirect and appropriate
   security headers. Avoid false claims about Let's Encrypt issuance until
   the domain resolves, challenge validation succeeds and HTTPS is tested.
5. Stage a non-public, access-controlled browser preview from source-only
   outputs. Determine whether/when licensed game art can be deployed;
   keep proprietary sources inaccessible even if an authenticated preview
   is later approved.
6. Verify page load, module/CSP compatibility, responsive TV-safe visuals,
   render performance, controller input and B/back behavior **on the actual
   Xbox One Edge browser** as well as a desktop browser. A controller on a
   computer is not a substitute for a console test.
7. Only mark the site playable when gameplay state, colonist production,
   turn processing, save/load, original rule parity, and the complete
   Xbox One input path have passed end-to-end tests.

## Current non-actions

- No production domain selected and **no temporary domain authorized**.
- No Master of Orion II ISPConfig website created yet.
- No DNS, certificates, public game assets, virtual hosts, or existing
  Qwen services changed.
- Do not claim deployment or Xbox One playability until observed.

Domain selection should **not block work on the game's engine and UI**.
Provision the site when a real hostname is chosen, or ask once for approval
to use a temporary hostname if early console-browser testing needs one.
