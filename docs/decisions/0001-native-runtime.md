# Decision 0001: Native Runtime

Status: accepted

## Context

The project is a remaster, not an emulator package or DOS wrapper.

## Decision

The final application will use a modern native engine and modern runtime assets. DOSBox, `ORION2.EXE`, DOS/4GW, and original LBX archives may support local research or import but will not be runtime dependencies of the distributed remaster.

## Gameplay effect

None intended.

## Verification

A release build must start and operate without the original executable, DOS runtime, or LBX files present.
