#!/usr/bin/env python3
"""Verify colony-yield instruction operands against official MOO2 v1.31 bytes.

This checks exact original machine-code fingerprints, not complete gameplay
equivalence or an inferred Watcom register calling convention.
"""
import bisect
import hashlib
import sys
from pathlib import Path

import original_probe as probe
from relocate_le_v131 import EXPECTED_RAW, reconstruct, parse_fixups

FUNCTIONS = {
    "Colony_Food2_Per_Farmer_": (136, "6aef5f245db959b949a22eb0cfccd03b65db2c103a18c4dc47f5bbabcf9a04e4"),
    "Colony_Industry_Per_Worker_": (178, "1e58a5b42e7d04cbc1d412b55ba007dbee502d5f0c257a96890c93d5689d8aa9"),
    "Colony_Research_Per_Scientist_": (177, "7d9e54a024e600115cf99d1d299806ceaf74f93c1aa95638a135b97e2efadd14"),
}

# Name, instruction virtual address, exact opcode/modrm prefix, immediate
# value, immediate width, and immediate offset from instruction start.
FIELDS = (
    ("research_base", 0xDFDC7, b"\xba", 3, 4, 1),
    ("research_flag_1", 0xDFDD6, b"\x80\xb8", 0x13A, 4, 2),
    ("research_flag_2", 0xDFDED, b"\x80\xb8", 0x154, 4, 2),
    ("research_flag_3", 0xDFE05, b"\x80\xb8", 0x149, 4, 2),
    ("research_flag_4", 0xDFE1E, b"\x80\xb8", 0x159, 4, 2),
    ("research_plus_3", 0xDFE0E, b"\x83\xc2", 3, 1, 2),
    ("research_plus_5", 0xDFE65, b"\x83\xc2", 5, 1, 2),
    ("research_compare_10", 0xDFE46, b"\x3c", 10, 1, 1),
    ("research_compare_11", 0xDFE4C, b"\x3c", 11, 1, 1),
    ("industry_planet_id_field", 0xDEC9B, b"\x0f\xbf\x40", 2, 1, 3),
    ("industry_planet_data_ptr", 0xDECA2, b"\xa1", 0x1B0D4, 4, 1),
    ("industry_flag_1", 0xDECBD, b"\x80\xb9", 0x13A, 4, 2),
    ("industry_flag_2", 0xDECD4, b"\x80\xb9", 0x13D, 4, 2),
    ("industry_flag_3", 0xDECEB, b"\x80\xb9", 0x15A, 4, 2),
    ("industry_flag_4", 0xDED03, b"\x80\xb9", 0x142, 4, 2),
    ("industry_plus_3", 0xDED0C, b"\x83\xc2", 3, 1, 2),
    ("food_planet_data_ptr", 0xDE04B, b"\xa1", 0x1B0D4, 4, 1),
    ("food_lookup_field", 0xDE050, b"\x66\x0f\xb6\x54\x02", 0x0B, 1, 5),
    ("food_race_status", 0xDE074, b"\x80\xbc\x06", 0x134, 4, 3),
    ("food_flag_1", 0xDE090, b"\x80\xb9", 0x164, 4, 2),
    ("food_flag_2", 0xDE0A9, b"\x80\xb9", 0x13A, 4, 2),
    ("food_plus_4", 0xDE099, b"\x83\xc2", 4, 1, 2),
)
MINERAL_VALUES = (1, 2, 3, 5, 8)
MINERALS_SHA256 = "0a834026e5178e5a668be1e368aeb321b6acdd1d651a3eb141541de4531c6c20"


def test(path: Path) -> None:
    original = path.read_bytes()
    if hashlib.sha256(original).hexdigest() != probe.OFFICIAL_SHA256:
        raise AssertionError("official v1.31 executable SHA-256 required")
    evidence = probe.inspect(path)
    images = reconstruct(original, evidence["le_image"])
    if tuple(hashlib.sha256(item).hexdigest() for item in images) != EXPECTED_RAW:
        raise AssertionError("original LE memory images differ from verified baseline")
    code = images[0]
    base = evidence["le_image"]["objects"][0]["address"]
    syms = probe.global_symbols(original, evidence["watcom"])
    starts = sorted({s["offset"] for s in syms.values()
                     if s["segment"] == 1 and s["kind"] & 4})
    for name, (expected_size, expected_digest) in FUNCTIONS.items():
        symbol = syms[name]
        assert symbol["segment"] == 1 and symbol["kind"] & 4, name
        start = symbol["offset"]
        index = bisect.bisect_right(starts, start)
        end = starts[index] if index < len(starts) else len(code)
        body = code[start:end]
        assert len(body) == expected_size, (name, len(body), expected_size)
        assert hashlib.sha256(body).hexdigest() == expected_digest, name

    symbol = syms["_minerals_per_mine"]
    assert symbol["segment"] == 1
    mineral_data = code[symbol["offset"]:symbol["offset"] + 5]
    assert hashlib.sha256(mineral_data).hexdigest() == MINERALS_SHA256
    assert tuple(mineral_data) == MINERAL_VALUES
    assert base + symbol["offset"] == 0xDD4B5

    # Cross-check original object-relative operands against the independent
    # LE page-fixup parser before asserting preferred-base addresses.
    fixups, summary = parse_fixups(original, evidence["le_image"])
    assert summary["records"] == 51363
    for address, target in (
        (0xDECA3, 0x18B0D4),  # industry per-worker planet data pointer
        (0xDE04C, 0x18B0D4),  # food per-farmer planet data pointer
        (0xDFE3E, 0x18B0D4),  # research per-scientist planet data pointer
        (0xDECB0, 0x0DD4B5),  # industry mineral table access
    ):
        assert fixups[(1, address - base)] == target, hex(address)

    for name, address, prefix, expected, width, value_offset in FIELDS:
        at = address - base
        assert code[at:at + len(prefix)] == prefix, name
        actual = int.from_bytes(code[at + value_offset:at + value_offset + width], "little")
        assert actual == expected, (name, actual, expected)
    # Check paired increments explicitly; do not imply executable semantics.
    assert code[0xDFE54 - base:0xDFE56 - base] == b"\x42\x42"
    assert code[0xDECF4 - base:0xDECF6 - base] == b"\x42\x42"
    print(f"Colony yield opcode/fingerprint regression: PASS "
          f"functions={len(FUNCTIONS)} operands={len(FIELDS)} "
          f"mineral_values={MINERAL_VALUES}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: test_rea_colony_yields.py /path/to/ORION2.EXE")
    test(Path(sys.argv[1]))