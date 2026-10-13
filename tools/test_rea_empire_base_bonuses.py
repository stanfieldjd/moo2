#!/usr/bin/env python3
"""Original executable regression for MOO2 v1.31 empire base-production additions.

The source is the user's private official ORION2.EXE; no proprietary bytes
are committed. Function SHA-256 and exact x86 instructions bind the
browser's uncached arithmetic to original executable evidence.
"""
import bisect
import hashlib
import struct
import sys
from pathlib import Path

import original_probe as probe
from relocate_le_v131 import EXPECTED_RAW, reconstruct

FUNCTIONS = (
    ("Colony_Empire_Base_Food2_Produced_", 0xDE0C6, 358,
     "705a9348d1b7e97003bd711a8553e114d453b5fbe745b0706c47dffe1de913c2"),
    ("Colony_Empire_Base_Industry_Produced_", 0xDED47, 212,
     "35aa50fa88250f254ba329b69bc8ed99ba7b9d647fe29f1fcffa1e7ecb4c24d8"),
    ("Colony_Empire_Base_Research_Produced_", 0xDFE77, 253,
     "1e72e37daea066aa98c587b71c86f1faae81775b60886693b9a3d33b8888e0f9"),
)
# Original code-object bytes before load-time relocations (not a synthetic
# ELF). Each checked instruction operand is independently present in source.
OPCODES = (
    (0xDE0E1, "0fb686dd000000"),     # food owner fast path colony +0xdd
    (0xDE155, "6683ff08"),           # food category >=8
    (0xDE16A, "0fbe9406a1080000"),   # signed race food byte +0x8a1
    (0xDE172, "80bc06ab08000000"),   # race climate flag +0x8ab
    (0xDE18B, "3c05"),               # climate code <=5
    (0xDE191, "3c06"),               # climate code <=6
    (0xDE195, "3c08"),               # climate code 8
    (0xDE19B, "3c04"),               # climate code 4
    (0xDE1AC, "0fb6831c580000"),     # global climate table +0x17581c
    (0xDE1B3, "0fb61d24580000"),     # global cap +0x175824
    (0xDE1D4, "0fb61d25580000"),     # global cap +0x175825
    (0xDE1DF, "ba06000000"),         # food special category 8 => +6
    (0xDE1E6, "6683ff09"),           # food special category 9
    (0xDE1EC, "ba04000000"),         # food special category 9 => +4
    (0xDED62, "0fb686de000000"),     # industry owner fast path +0xde
    (0xDEDC7, "6683ff08"),           # industry category >=8
    (0xDEDD9, "0fbe8402a2080000"),   # signed race industry byte +0x8a2
    (0xDEDE5, "b803000000"),         # industry special category 8 => +3
    (0xDFE92, "0fb686df000000"),     # research owner fast path +0xdf
    (0xDFF11, "660fbe36"),           # signed colony owner byte
    (0xDFF15, "0fbe90a3080000"),     # signed race research byte +0x8a3
    (0xDFF21, "80b86b01000003"),     # bonus race byte +0x16b == 3
    (0xDFF2A, "c745f401000000"),     # research owner bonus 1
    (0xDFF35, "ba03000000"),         # research special category 8 => +3
)


def check(path: Path) -> None:
    original = path.read_bytes()
    assert hashlib.sha256(original).hexdigest() == probe.OFFICIAL_SHA256
    report = probe.inspect(path)
    raw_objects = reconstruct(original, report["le_image"])
    assert tuple(hashlib.sha256(o).hexdigest() for o in raw_objects) == EXPECTED_RAW
    code = raw_objects[0]
    base = report["le_image"]["objects"][0]["address"]
    assert base == 0x10000
    symbols = probe.global_symbols(original, report["watcom"])
    starts = sorted({value["offset"] for value in symbols.values()
                     if value["segment"] == 1 and value["kind"] & 4})
    for name, va, expected_size, digest in FUNCTIONS:
        symbol = symbols[name]
        start = symbol["offset"]
        assert symbol["segment"] == 1 and base + start == va
        end = starts[bisect.bisect_right(starts, start)]
        assert end - start == expected_size
        assert hashlib.sha256(code[start:end]).hexdigest() == digest, name
    for va, source_hex in OPCODES:
        prefix = bytes.fromhex(source_hex)
        start = va - base
        assert code[start:start+len(prefix)] == prefix, hex(va)
    # Verify three E8 calls resolve to the independently authenticated
    # existing per-worker primitives (unchanged from earlier regressions).
    for va, target in ((0xDE0F2,0xDE03E),(0xDED73,0xDEC95),(0xDFEA3,0xDFDC6)):
        start=va-base
        assert code[start] == 0xe8
        rel = struct.unpack_from("<i",code,start+1)[0]
        assert va + 5 + rel == target,(hex(va),hex(target))
    print("Empire base bonuses original-byte regression: PASS "
          f"functions={len(FUNCTIONS)} opcodes={len(OPCODES)} "
          "verified_per_worker_calls=3")


if __name__ == "__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: test_rea_empire_base_bonuses.py /path/to/ORION2.EXE")
    check(Path(sys.argv[1]))
