#!/usr/bin/env python3
"""Verify v1.31 packed workforce selection from original x86 instruction bytes.

These checks establish the record layout, bit extraction and per-job filter.
They do not prove job-production numerical totals or a whole turn.
"""
import bisect
import hashlib
import struct
import sys
from pathlib import Path

import original_probe as probe
from relocate_le_v131 import EXPECTED_RAW, reconstruct

# Preferred x86 instruction address -> exact opcode prefix and operands.
SITES = (
    (0xDE376, bytes.fromhex("0fb67e0a")),  # MOVZX EDI,colony+0xa
    (0xDE37A, bytes.fromhex("8d460c")),    # LEA EAX,colony+0xc
    (0xDE37D, bytes.fromhex("c1e702")),    # SHL EDI,2
    (0xDE390, bytes.fromhex("83ef04")),    # SUB EDI,4
    (0xDE393, bytes.fromhex("f6470102")),  # TEST [record+1],bit 1 (=bit9)
    (0xDE39D, bytes.fromhex("8b17")),      # MOV EDX,[record]
    (0xDE39F, bytes.fromhex("c1e217")),    # SHL EDX,23
    (0xDE3A6, bytes.fromhex("c1ea1e")),    # SHR EDX,30 (bits7-8)
    (0xDE3A9, bytes.fromhex("39c2")),      # compare job to requested slot
    (0xDE3B1, bytes.fromhex("8b07")),      # read packed record again
    (0xDE3B3, bytes.fromhex("83e00f")),    # category low nibble
)


def verify(path: Path) -> None:
    source = path.read_bytes()
    assert hashlib.sha256(source).hexdigest() == probe.OFFICIAL_SHA256
    info = probe.inspect(path)
    images = reconstruct(source, info["le_image"])
    assert tuple(hashlib.sha256(x).hexdigest() for x in images) == EXPECTED_RAW
    image = images[0]
    base = info["le_image"]["objects"][0]["address"]
    symbols = probe.global_symbols(source, info["watcom"])
    symbol = symbols["Colony_Job_Production_"]
    assert symbol["segment"] == 1 and symbol["kind"] & 4
    assert base + symbol["offset"] == 0xDE280
    code_starts = sorted({v["offset"] for v in symbols.values()
                          if v["segment"] == 1 and v["kind"] & 4})
    next_index = bisect.bisect_right(code_starts, symbol["offset"])
    end = code_starts[next_index]
    assert end - symbol["offset"] == 996
    for address, expected in SITES:
        at = address - base
        assert image[at:at + len(expected)] == expected, hex(address)
        assert symbol["offset"] <= at < end
    # JZ from bit-9 test jumps over the full current-colonist production path.
    addr = 0xDE397
    at = addr - base
    assert image[at:at+2] == b"\x0f\x84"
    displacement = struct.unpack_from("<i",image,at+2)[0]
    assert addr + 6 + displacement == 0xDE61E
    # After extracting job bits, JNZ also skips a nonselected job record.
    addr = 0xDE3AB
    at = addr - base
    assert image[at:at+2] == b"\x0f\x85"
    displacement = struct.unpack_from("<i",image,at+2)[0]
    assert addr + 6 + displacement == 0xDE61E
    print(f"Original workforce scan opcode regression: PASS "
          f"instructions={len(SITES)} verified_jumps=2 body_bytes=996")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: test_rea_workforce_scan.py /path/to/ORION2.EXE")
    verify(Path(sys.argv[1]))
