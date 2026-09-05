# Project Rules

1. The remaster must play like original Master of Orion II.
2. Modernization is limited to graphics, interface, audio, portability, maintainability, and technical infrastructure unless the user explicitly changes scope.
3. Official MicroProse v1.31 is the canonical gameplay baseline.
4. Later patches and community reverse engineering are diagnostic evidence. Do not inherit fan features or balance changes automatically.
5. Correct verified defects at their root cause. Do not add bypasses, duplicate fallback paths, compatibility hacks, or workaround layers in place of a proper repair.
6. When observed behavior, documentation, and later fixes conflict, preserve all evidence, identify the conflict, and make an explicit documented decision before implementation.
7. The final native application must not depend on DOSBox, `ORION2.EXE`, DOS/4GW, or LBX files at runtime.
8. Keep raw tool output, interpretation, verified conclusions, and native implementation separate.
9. Never label guessed symbols or inferred behavior as verified.
10. Every material change must be committed, pushed, and verified on GitHub.
11. Never commit proprietary game files, credentials, or private installation data.
