# MOO2 reverse-engineering workbench status

Local source snapshot: `176c55fa21a33df1da4452f52efed2fc3c3a2eb2`

Current phase: full executable decompilation. Gameplay reconstruction is deferred until decompilation coverage is complete enough for a systematic reconstruction pass.

Current best completion estimate: 87% decompilation / 13% remaining.

The original proprietary executable and game assets are not stored in this repository. Development tooling verifies a locally supplied official v1.31 executable before extracting derived analysis.

Recent work has concentrated on resynchronized x86 decoding, CFG-reachable instruction recovery, switch-table recovery, indirect call/table resolution, synthetic unnamed call targets, and Watcom runtime initialization dispatch tables.
