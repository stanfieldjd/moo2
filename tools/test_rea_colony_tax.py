#!/usr/bin/env python3
"""Validate v1.31 colony industry-to-tax arithmetic instruction evidence.

The local arithmetic fixtures cover the directly decoded signed/unsigned
instruction sequence. They do not execute DOS, infer taxation policy outside
observed conditions, or establish full game-level behavioral equivalence.
"""
import bisect
import hashlib
import sys
from pathlib import Path

import original_probe as probe
from relocate_le_v131 import EXPECTED_RAW, parse_fixups, reconstruct

BODY_SHA256 = "0801f833e5ad497d8d59d069ee8b40e532829f85bedbeeb7ad4d28ca4805cd84"

# Name, original LE virtual instruction address, opcode prefix,
# immediate, width, position within instruction.
FIELDS = (
    ("signed_industry_word", 0xE08FB, b"\x0f\xbf\x80", 0xE9, 4, 3),
    ("unsigned_reserved_byte", 0xE0902, b"\x0f\xb6\x93", 0xF0, 4, 3),
    ("zero_tax_field", 0xE0911, b"\x66\xc7\x83", 0x127, 4, 3),
    ("owner_record_stride", 0xE0921, b"\x69\xc0", 0xEA9, 4, 2),
    ("tax_rate_field", 0xE092D, b"\x0f\xb6\x44\x01", 0x31, 1, 4),
    ("signed_divisor", 0xE0935, b"\xb9", 100, 4, 1),
    ("store_tax_word", 0xE093D, b"\x66\x89\x83", 0x127, 4, 3),
    ("subtract_from_industry_word", 0xE0944, b"\x66\x29\x83", 0xE9, 4, 3),
)


def as_signed_16(number):
    return ((number + 32768) & 65535) - 32768


def isolated_math_fixture(signed_industry, reserved_byte, rate_byte):
    """Model observed isolated arithmetic, not a verified gameplay API."""
    assert -32768 <= signed_industry <= 32767
    assert 0 <= reserved_byte <= 255
    assert 0 <= rate_byte <= 255
    surplus = signed_industry - reserved_byte
    if surplus <= 0:
        return 0, signed_industry
    product = surplus * rate_byte
    assert -(1 << 31) <= product < (1 << 31)
    tax_ax = as_signed_16(product // 100)
    remaining = as_signed_16(signed_industry - tax_ax)
    return tax_ax, remaining


def verify(path: Path):
    source = path.read_bytes()
    if hashlib.sha256(source).hexdigest() != probe.OFFICIAL_SHA256:
        raise AssertionError("canonical official v1.31 executable required")
    info = probe.inspect(path)
    images = reconstruct(source, info["le_image"])
    if tuple(hashlib.sha256(x).hexdigest() for x in images) != EXPECTED_RAW:
        raise AssertionError("LE object mismatch")
    code = images[0]
    base = info["le_image"]["objects"][0]["address"]
    syms = probe.global_symbols(source, info["watcom"])
    symbol = syms["Colony_Industry_To_Tax_"]
    assert symbol["segment"] == 1 and symbol["kind"] & 4
    starts = sorted({x["offset"] for x in syms.values()
                     if x["segment"] == 1 and x["kind"] & 4})
    pos = symbol["offset"]
    following = starts[bisect.bisect_right(starts, pos)]
    body = code[pos:following]
    assert len(body) == 89
    assert hashlib.sha256(body).hexdigest() == BODY_SHA256

    for name, addr, prefix, expected, width, offset in FIELDS:
        instruction = addr - base
        assert code[instruction:instruction + len(prefix)] == prefix, name
        got = int.from_bytes(code[instruction + offset: instruction + offset + width],
                             "little")
        assert got == expected, (name, got, expected)
    # JG at E090F skips the zero-tax store for positive surplus.
    assert code[0xE090F-base:0xE0911-base] == b"\x7f\x0d"
    assert 0xE0911 + 0x0D == 0xE091E
    # Instruction-specific signed multiplication/division/AX stores.
    assert code[0xE0932-base:0xE0935-base] == b"\x0f\xaf\xc2"
    assert code[0xE093A-base:0xE093D-base] == b"\x99\xf7\xf9"
    assert code[0xE0911-base:0xE091A-base] == b"\x66\xc7\x83\x27\x01\x00\x00\x00\x00"
    # Decode original object-relative pointer to preferred LE address.
    fixups, _ = parse_fixups(source, info["le_image"])
    assert int.from_bytes(code[0xE0929-base:0xE092D-base], "little") == 0x1FF98
    assert fixups[(1, 0xE0929-base)] == 0x18FF98

    fixtures = (
        ((100, 20, 25), (20, 80)),
        ((50, 50, 25), (0, 50)),
        ((5, 10, 100), (0, 5)),
        ((100, 1, 33), (32, 68)),
        ((100, 0, 50), (50, 50)),
        ((32767, 0, 100), (32767, 0)),
    )
    for inputs, expected in fixtures:
        actual = isolated_math_fixture(*inputs)
        assert actual == expected, (inputs, actual, expected)
    print(f"Industry tax opcode/arithmetic regression: PASS "
          f"function_bytes={len(body)} operands={len(FIELDS)} "
          f"arithmetic_fixtures={len(fixtures)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: test_rea_colony_tax.py /path/to/ORION2.EXE")
    verify(Path(sys.argv[1]))

[executed on device: penguin (fe398797-2021-4a30-8c66-0b31be29ec12)]