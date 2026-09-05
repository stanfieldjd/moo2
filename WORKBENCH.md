# Workbench State

## Current verified position

- Persistent repository: `stanfieldjd/moo2`
- Canonical branch: `main`
- Canonical gameplay reference: official MicroProse v1.31
- Runtime direction: fully native remaster
- Original installation role: local evidence and import source only
- Existing recovered implementation: no native reimplementation committed
- Existing recovered decompilation artifacts: verified analysis metadata, symbol maps,
  call graphs, reconstruction packets, disassembly excerpts, and reproducible tooling
  imported from `moo2_remaster_work.zip`

The imported archive contained 116 intentionally tracked paths totaling 9,600,968
bytes after its exclusion rules were applied. Its SHA-256 is
`0738232ea6ac569f8027d2a6270d2f06c05f659db1a79fb978eb9d34220e73db`.
These counts describe the workbench evidence, not a percentage of game code recovered.

## Immediate line of work

1. Record the exact provenance and cryptographic hashes of locally supplied v1.31 files without committing those files.
2. Identify the executable format, compiler/runtime signatures, memory model, overlays, imports, and entry points.
3. Preserve untouched decompiler output separately from annotated analysis.
4. Build an address-and-symbol map with evidence attached to every name.
5. Convert verified behavior into deterministic regression tests.
6. Implement clean native behavior only after the relevant rule is evidenced.

## Completion rule

A finding is complete only when its source, reproduction method, confidence, and verification result are recorded. A code change is complete only when tests pass and the commit is pushed and verified on GitHub.

## Next action

Audit and promote the highest-confidence reconstruction packets into annotated,
test-backed subsystem specifications. Do not upload the executable.
