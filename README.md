# Game Lab — Browser Game Workspace (provisional brand)

**Public-facing umbrella name:** Game Lab is a provisional working title for a website that can host multiple independent game projects, not a legally cleared trademark. Its first project is currently labeled Space Strategy Project. The original game's name is used in this research workbench solely to identify the historical subject and benchmark; there is no affiliation, endorsement or license implied. Do not publish source-game assets or a derivative adaptation without sufficient rights or authorization. See [hosting and rights gates](docs/deployment/ispconfig-browser-hosting.md).

This repository is the persistent engineering workbench for studying the official MicroProse *Master of Orion II: Battle at Antares* version 1.31 behavior and building a native remaster.

## Objective

Preserve the original game's rules, AI, economy, combat, balance, events, and probabilities while modernizing graphics, interface, audio, portability, and technical infrastructure.

The finished application must be native. It must not require DOSBox, `ORION2.EXE`, DOS/4GW, or LBX archives at runtime. A lawful original installation may be used locally as evidence and as an import source.

## Browser-playable delivery goal

The operative development goal is a **browser-based space-strategy game on the user's server, using Master of Orion II v1.31 as the original-behavior reference only to the extent legally permitted, accessible both from a computer browser and from Microsoft Edge on the Xbox One console itself, using its Xbox controller, with upscaled graphics**, not merely a finished analysis workbench. This browser deployment must preserve original gameplay behavior while modernizing the visual and input layers. Qwen is not part of this project.

See the [multi-game website shell](web/site/README.md), [browser-game delivery acceptance criteria](docs/browser-game-delivery-target.md) and the [graphics/controller preview](web/graphics/README.md). The latter is an engineering preview only; it does not yet implement game logic, use verified decoded original artwork, or constitute the finished game.

## Authority

Official v1.31 behavior is the canonical gameplay baseline. Later patches, reverse engineering, documentation, and community findings are evidence used to identify and understand defects; fan-added features and balance changes are not automatically canonical.

See [PROJECT_RULES.md](PROJECT_RULES.md), [WORKBENCH.md](WORKBENCH.md), and [docs/authority/README.md](docs/authority/README.md).

## Repository policy

Do not commit original game binaries, LBX archives, copyrighted artwork, music, sound, video, manuals, or other proprietary assets. Do not commit secrets, credentials, or personal installation paths.

All material findings require provenance, confidence, verification status, and a reproducible validation path.

## Workbench contents

The tracked workbench includes reproducible analysis tools, function and symbol metadata, control-flow and indirect-dispatch results, focused annotated disassembly, behavioral reconstruction notes, and tests. Large generated corpora and original or reconstructed machine-code bytes remain local and are regenerated from a lawfully supplied official v1.31 installation.
