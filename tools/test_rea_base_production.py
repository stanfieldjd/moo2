#!/usr/bin/env python3
"""Verify MOO2 v1.31 per-colonist base-production dispatch and return floor.

Tests exact original LE object bytes, three relocated function pointers and
the fourth null table entry. Does not execute the proprietary game.
"""
import bisect
import hashlib
import struct
import sys
from pathlib import Path

import original_probe as probe
from relocate_le_v131 import EXPECTED_RAW, parse_fixups, reconstruct

# Original preferred virtual addresses and exact bytes (not modernized code).
OPCODES = (
    (0xDE237, bytes.fromhex("8b02")),              # read packed colonist word
    (0xDE23C, bytes.fromhex("83e00f")),            # category low nibble
    (0xDE24E, bytes.fromhex("ff14bd5cb50000")),  # indexed indirect call, raw
    (0xDE255, bytes.fromhex("6685c0")),            # TEST AX,AX
    (0xDE258, bytes.fromhex("7f17")),              # JG after positive
    (0xDE25A, bytes.fromhex("66837df800")),        # CMP WORD [EBP-8],0 (job)
    (0xDE25F, bytes.fromhex("7509")),              # JNE set min one
    (0xDE261, bytes.fromhex("80bedd00000000")),    # CMP colony byte +0xdd,0
    (0xDE268, bytes.fromhex("7607")),              # JBE preserve zero floor
    (0xDE26A, bytes.fromhex("c745fc01000000")),    # min = 1
    (0xDE271, bytes.fromhex("663b45fc")),          # CMP AX, min
    (0xDEE14, bytes.fromhex("8b45fc")),            # shared tail: MOV EAX,min
    (0xDEE17, bytes.fromhex("c95f5ec3")),          # LEAVE; POP EDI; POP ESI; RET
)
# The table contains zero-based entries for food, industry and research.
RAW_POINTERS = (0xCE0C6, 0xCED47, 0xCFE77, 0)
PREFERRED_POINTERS = (0xDE0C6, 0xDED47, 0xDFE77, 0)
SYMBOLS = (
    "Colony_Empire_Base_Food2_Produced_",
    "Colony_Empire_Base_Industry_Produced_",
    "Colony_Empire_Base_Research_Produced_",
)


def verify(path: Path) -> None:
    original = path.read_bytes()
    assert hashlib.sha256(original).hexdigest() == probe.OFFICIAL_SHA256
    report = probe.inspect(path)
    le = report["le_image"]
    images = reconstruct(original, le)
    assert tuple(hashlib.sha256(obj).hexdigest() for obj in images) == EXPECTED_RAW
    code, data = images
    code_base = le["objects"][0]["address"]
    data_base = le["objects"][1]["address"]
    assert code_base == 0x10000 and data_base == 0x170000
    sym = probe.global_symbols(original, report["watcom"])
    name = "Colony_Pop_Base_Prod_Produced_"
    start = sym[name]["offset"]
    assert code_base + start == 0xDE22C
    boundaries = sorted({s["offset"] for s in sym.values()
                         if s["segment"] == 1 and s["kind"] & 4})
    next_start = boundaries[bisect.bisect_right(boundaries, start)]
    assert next_start - start == 84
    for address, expected in OPCODES:
        at = address - code_base
        assert code[at:at+len(expected)] == expected, hex(address)

    # Exact original binary branch targets, including Watcom shared-tail.
    assert 0xDE25A + struct.unpack("<b", code[0xDE259-code_base:0xDE25A-code_base])[0] == 0xDE271
    branch = 0xDE275
    assert code[branch-code_base:branch-code_base+2] == b"\x0f\x8d"
    rel = struct.unpack_from("<i", code, branch-code_base+2)[0]
    assert branch + 6 + rel == 0xDEE17
    branch = 0xDE27B
    assert code[branch-code_base] == 0xE9
    rel = struct.unpack_from("<i", code, branch-code_base+1)[0]
    assert branch + 5 + rel == 0xDEE14

    fixups, _ = parse_fixups(original, le)
    assert fixups[(1, 0xDE251-code_base)] == 0x17B55C
    table = 0x17B55C - data_base
    for index, (raw, preferred) in enumerate(zip(RAW_POINTERS, PREFERRED_POINTERS)):
        address = table + index * 4
        assert struct.unpack_from("<I", data, address)[0] == raw, index
        if index < 3:
            assert fixups[(2, address)] == preferred, index
            assert code_base + sym[SYMBOLS[index]]["offset"] == preferred
        else:
            assert address not in (k[1] for k in fixups if k[0] == 2)
    print("Base-production floor/dispatch byte regression: PASS "
          "opcodes=13 table_entries=4 function_bytes=84")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: test_rea_base_production.py /path/to/ORION2.EXE")
    verify(Path(sys.argv[1]))
