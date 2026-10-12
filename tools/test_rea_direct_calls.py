#!/usr/bin/env python3
"""Verify direct rel32 calls in the official MOO2 v1.31 LE code image.

Reads a lawful local executable and original Watcom debug-symbol records.
Checks exact E8 CALL instruction bytes and destinations independently of
Ghidra's decompiler output. Does not execute or mutate the game.
"""
import bisect
import hashlib
import struct
import sys
from pathlib import Path

import original_probe as probe
from relocate_le_v131 import EXPECTED_RAW, reconstruct

# Watcom caller symbol, CALL opcode virtual address, Watcom target symbol.
EDGES = (
    ("Colony_Industry_Production_", 0xDEEA5, "Colony_Job_Production_"),
    ("Colony_Industry_Production_", 0xDEF90, "Colony_Officer_"),
    ("Colony_Industry_Production_", 0xDF24F, "Format_Quotient_"),
    ("Colony_Research_Production_", 0xDFFE8, "Colony_Job_Production_"),
    ("Colony_Research_Production_", 0xE01ED, "Format_Quotient_"),
    ("Colony_Job_Production_", 0xDE2BB, "Colony_Officer_"),
    ("Colony_Job_Production_", 0xDE3BB, "Gravity_Player_Production_Factor_"),
    ("Colony_Job_Production_", 0xDE3FA, "Colony_Pop_Base_Prod_Produced_"),
)


def verify(path: Path):
    file_bytes = path.read_bytes()
    digest = hashlib.sha256(file_bytes).hexdigest()
    if digest != probe.OFFICIAL_SHA256:
        raise ValueError("original executable SHA-256 does not match official v1.31")
    info = probe.inspect(path)
    le = info["le_image"]
    raw = reconstruct(file_bytes, le)
    if tuple(hashlib.sha256(item).hexdigest() for item in raw) != EXPECTED_RAW:
        raise ValueError("LE code or data object hash mismatch")
    assert len(le["objects"]) == 2
    base = le["objects"][0]["address"]
    code = raw[0]
    syms = probe.global_symbols(file_bytes, info["watcom"])
    offsets = sorted(set(value["offset"] for value in syms.values()
                         if value["segment"] == 1 and value["kind"] & 4))
    observed = []
    for caller, insn_address, target in EDGES:
        source = syms[caller]
        dest = syms[target]
        if source["segment"] != 1 or dest["segment"] != 1:
            raise AssertionError("CALL source or target is not an LE code symbol")
        insn_offset = insn_address - base
        index = bisect.bisect_right(offsets, source["offset"])
        caller_end = offsets[index] if index < len(offsets) else len(code)
        if not source["offset"] <= insn_offset < caller_end:
            raise AssertionError("CALL site is not inside its named Watcom caller")
        if not 0 <= insn_offset <= len(code) - 5:
            raise AssertionError("CALL site outside LE code image")
        opcode = code[insn_offset]
        if opcode != 0xE8:
            raise AssertionError(f"not E8 at {insn_address:#x}")
        displacement = struct.unpack_from("<i", code, insn_offset + 1)[0]
        resolved = insn_address + 5 + displacement
        expected_target = base + dest["offset"]
        if resolved != expected_target:
            raise AssertionError(
                f"bad CALL target at {insn_address:#x}: "
                f"{resolved:#x} != {expected_target:#x}"
            )
        observed.append((caller, insn_address, target, expected_target))
    print("MOO2 v1.31 direct CALL byte regression: PASS")
    print(f"verified_sites={len(observed)} unique_targets="
          f"{len(set(item[3] for item in observed))} "
          f"original_sha256={digest}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: test_rea_direct_calls.py /path/to/ORION2.EXE")
    verify(Path(sys.argv[1]))