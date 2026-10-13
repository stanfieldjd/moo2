# v1.31 original `Ship_Owner_` — cross-symbol function reconstruction

**Status:** complete observed decision/return *shape* of this isolated
original Watcom routine, with original error path cross-referenced
through runtime shutdown. This is **derived C-like pseudocode**,
not MicroProse source and not a complete game-ship subsystem.

Authenticated source: `ORION2.EXE`, SHA-256
`4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f`.

The original Watcom symbol `Ship_Owner_` starts at LE CODE
offset **`0x67FF5`** and its short 30-byte symbol-bounded
interval ends at `0x68013`. It immediately branches into a
common block at **`0x6892D`**, which lies inside the
provisional `Ship_Icon_Y_` symbol interval. The latter was
independently re-decoded and its 48 reachable instructions
enumerated; it contains two machine-code RET sites at
`0x68982` and `0x689C6`.

## Observed control/validity checks

1. Input EAX is copied into EBX, then the lower 16 bits
   **BX** are tested as signed. Negative index sets internal
   error code **1**.
2. Nonnegative indices enter target `0x6892D`.
   A signed `CMP BX,0x1F4` rejects indices **500 or above**
   with internal error code **2**.
3. For IDs 0..499, the routine accesses the ship record table
   pointed to by original DATA global `[0x1FF9C]`, with record
   stride **`0x81`** bytes and owner byte at offset **`0x63`**.
4. Signed byte owner below 0 selects error code **3**.
   Signed byte owner above 15 selects error code **4**.
5. For a valid owner in 0..15, code at `0x68969`
   reloads the signed owner byte, moves it into AX, restores
   the caller's frame and returns. The index is at most 499,
   so the `index*0x81` temporary fits the low 16 bits
   before the AX-only assignment.
6. For nonzero error code the path at `0x68983`
   constructs a formatted message via `sprintf_`
   (`0x1165F2`) and passes its buffer to
   `Exit_With_Message_` (`0x116487`). This helper
   calls `Reset_System_`, `printf_`, and finally
   `exit_` (`0x12F2F4`) with exit code **1**.
   The source's subsequent `XOR EAX,EAX; RET` is a
   fallback if the exit wrapper somehow returns; it is
   not evidence that invalid inputs ordinarily return owner 0.

## C-like reconstruction of the valid-index and error classification

```c
// Derived algorithm, NOT original C. All ship pointers are original-game
// records; the fatal branch's original printf/exit pipeline is
// specified below, not modeled as an ordinary safe error return.
int16_t recovered_Ship_Owner_(int16_t ship_index,
                               const uint8_t *ship_records) {
    int error = 0;
    int8_t owner = 0;

    if (ship_index < 0) {
        error = 1;
    } else if (ship_index >= 500) {
        error = 2;
    } else {
        // Each original ship record is 0x81 bytes.
        owner = (int8_t)ship_records[ship_index * 0x81 + 0x63];
        if (owner < 0)
            error = 3;
        else if (owner > 15)
            error = 4;
        else
            return (int16_t)owner;
    }

    // Original program passes formatted failure diagnostics through
    // sprintf_ and Exit_With_Message_, which calls exit_(1).
    // Do not turn this into a normal "return 0" in a faithful port.
    report_original_ship_owner_failure_and_exit(error, ship_index);
    return 0; // original post-exit fallback only
}
```

The snippet intentionally leaves the error function **unimplemented**;
the original error branch also accesses the ship record to compose the
diagnostic, possibly even after a bad index is detected. Recreating
that read blindly would risk an out-of-bounds access. A safe
reimplementation requires an explicit policy decision and separate
validation rather than silently presenting this as a byte-for-byte
equivalent routine.

## Evidence anchors

- Source signed-index check: `0x68000: TEST BX,BX`;
  `0x68003: JGE 0x6892D`.
- Valid-range check: `0x6892D: CMP BX,0x1F4`;
  `0x68932: JL 0x6893B`.
- Owner record read: `0x6893B..0x68950`,
  scaled by `0x81), byte at `+0x63`.
- Owner high-bound comparison: `0x68959..0x6895F`.
- Valid return: `0x68969..0x68982`.
- Fatal formatting path: `0x68983..0x689BB`, then
  `0x689C0..0x689C6` fallback return.
- Runtime exit: `Exit_With_Message_` at
  `0x116487..0x1164CB` calls original `exit_` at
  `0x12F2F4`.

## Remaining uncertainties

A full game-compatible port still needs call-site argument
contracts, the player/ship allocation bounds, error-message
format string/data-symbol identity, any game states where an
invalid ship ID is intentionally passed, and differential validation.
This reconstruction does **not** change the live Game Lab site,
gameplay engine, Xbox configuration or Qwen.
