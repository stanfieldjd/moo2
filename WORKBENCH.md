# Workbench State

## Current verified position

- Persistent repository: `stanfieldjd/moo2`
- Canonical branch: `main`
- Canonical gameplay reference: official MicroProse v1.31
- Runtime direction: fully native remaster
- Original installation role: local evidence and import source only
- Existing recovered implementation: none committed
- Existing recovered decompilation artifacts: none committed

Claims from a lost temporary workspace are not repository evidence and must not be represented as recovered work.

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

Populate `docs/research/executable-provenance.md` from a lawful local v1.31 installation. Do not upload the executable.
