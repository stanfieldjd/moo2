#!/usr/bin/env python3
"""Validate and apply official MOO2 v1.31 LE internal fixups to separate local images.

The source executable is never modified or copied to GitHub. Requires only
Python 3 and the neighboring original_probe.py from this repository.
"""
import argparse
import collections
import hashlib
import json
import shutil
import struct
from pathlib import Path

import original_probe as probe

EXPECTED_RAW = (
    "f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837",
    "c1f592ecdef3538a34bc42957b4c790152de288d4fa2cd85cc47b3668e448856",
)
EXPECTED_RELOCATED = (
    "d85e5536e7181c3bfd332d43284522448af22fca2133101869e034d8de29be85",
    "13158fa46216feb6a3f93ff119c98be99f8ad487191fe4e2bbaffcea79ecb0e0",
)


class FixupError(ValueError):
    pass


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def reconstruct(data, le):
    images = []
    for obj in le["objects"]:
        image = bytearray(obj["size"])
        for off in range(0, obj["size"], le["page_size"]):
            n = min(le["page_size"], obj["size"] - off)
            try:
                file_off = probe.le_object_file_offset(data, le, obj["number"], off)
            except probe.ProbeError:
                continue
            if file_off + n > len(data):
                raise FixupError("mapped page exceeds source file")
            image[off:off + n] = data[file_off:file_off + n]
        images.append(bytes(image))
    return images


def parse_fixups(data, le):
    """Return object-relative source positions and resolved preferred-base targets.

    This intentionally supports only the two observed v1.31 record variants:
    source type 0x07 and target flags 0x00/0x10. Other formats fail closed.
    """
    objects = le["objects"]
    if len(objects) != 2:
        raise FixupError("expected exactly two LE objects")
    h = le["le_start"]
    count = struct.unpack_from("<I", data, h + 0x14)[0]
    first = h + struct.unpack_from("<I", data, h + 0x68)[0]
    records_start = h + struct.unpack_from("<I", data, h + 0x6c)[0]
    imports_start = h + struct.unpack_from("<I", data, h + 0x70)[0]
    if count != sum(o["map_count"] for o in objects):
        raise FixupError("logical page count does not match object page maps")
    if first + 4 * (count + 1) > records_start:
        raise FixupError("fixup page table overlaps record table")
    pointers = [struct.unpack_from("<I", data, first + 4 * i)[0]
                for i in range(count + 1)]
    if pointers[0] != 0 or records_start + pointers[-1] != imports_start:
        raise FixupError("fixup record table bounds mismatch")
    if any(a > b for a, b in zip(pointers, pointers[1:])):
        raise FixupError("fixup page offsets not monotonic")
    sites = {}
    flag_counts = collections.Counter()
    pair_counts = collections.Counter()
    duplicates = 0
    total = 0
    for page in range(count):
        cursor = records_start + pointers[page]
        stop = records_start + pointers[page + 1]
        while cursor < stop:
            if cursor + 4 > stop:
                raise FixupError("truncated relocation header")
            src_type, flags = data[cursor], data[cursor + 1]
            cursor += 2
            if src_type != 0x07 or flags not in (0x00, 0x10):
                raise FixupError("unsupported relocation type/flags")
            source = struct.unpack_from("<h", data, cursor)[0]
            cursor += 2
            width = 4 if flags & 0x10 else 2
            if cursor + 1 + width > stop:
                raise FixupError("truncated relocation target")
            target_obj = data[cursor]
            cursor += 1
            target_off = struct.unpack_from("<I" if width == 4 else "<H", data, cursor)[0]
            cursor += width
            if not 1 <= target_obj <= len(objects):
                raise FixupError("invalid target object number")
            target = objects[target_obj - 1]
            if target_off >= target["size"]:
                raise FixupError("target offset outside object")
            source_obj = 1 if page < objects[0]["map_count"] else 2
            local_page = page if source_obj == 1 else page - objects[0]["map_count"]
            local = local_page * le["page_size"] + source
            if not 0 <= local <= objects[source_obj - 1]["size"] - 4:
                raise FixupError("source offset outside object")
            key = (source_obj, local)
            target_va = target["address"] + target_off
            if key in sites:
                if sites[key] != target_va:
                    raise FixupError("conflicting fixups at same address")
                duplicates += 1
            else:
                sites[key] = target_va
            flag_counts[str(flags)] += 1
            pair_counts[f"{source_obj}->{target_obj}"] += 1
            total += 1
        if cursor != stop:
            raise FixupError("record did not end at page boundary")
    occupied = {}
    for (src_obj, source), target_va in sites.items():
        for j, value in enumerate(struct.pack("<I", target_va)):
            addr = (src_obj, source + j)
            if addr in occupied and occupied[addr] != value:
                raise FixupError("overlapping relocation bytes disagree")
            occupied[addr] = value
    return sites, {
        "records": total,
        "unique_sites": len(sites),
        "equal_duplicate_records": duplicates,
        "source_type": 7,
        "target_flags": dict(sorted(flag_counts.items())),
        "object_pair_counts": dict(sorted(pair_counts.items())),
        "conflicting_bytes": 0,
    }


def apply(images, sites):
    patched = [bytearray(x) for x in images]
    for (source_obj, offset), target in sites.items():
        struct.pack_into("<I", patched[source_obj - 1], offset, target)
    return [bytes(x) for x in patched]


def self_test():
    raw = bytearray(0x400)
    struct.pack_into("<I", raw, 0x14, 3)
    struct.pack_into("<I", raw, 0x68, 0x100)
    struct.pack_into("<I", raw, 0x6c, 0x200)
    struct.pack_into("<I", raw, 0x70, 0x219)
    for i, offset in enumerate((0, 9, 18, 25)):
        struct.pack_into("<I", raw, 0x100 + 4 * i, offset)
    record = lambda source, target_obj, offset: b"\x07\x10" + struct.pack("<hBI", source, target_obj, offset)
    raw[0x200:0x209] = record(4094, 2, 0x50)
    raw[0x209:0x212] = record(-2, 2, 0x50)
    raw[0x212:0x219] = b"\x07\x00" + struct.pack("<hBH", 0x30, 1, 0x400)
    le = {"le_start": 0, "page_size": 4096,
          "objects": [{"size": 8192, "address": 0x10000, "map_count": 2},
                      {"size": 4096, "address": 0x170000, "map_count": 1}]}
    sites, stats = parse_fixups(raw, le)
    assert stats["records"] == 3 and stats["unique_sites"] == 2
    assert stats["equal_duplicate_records"] == 1
    images = apply([bytes(8192), bytes(4096)], sites)
    assert struct.unpack_from("<I", images[0], 4094)[0] == 0x170050
    assert struct.unpack_from("<I", images[1], 0x30)[0] == 0x10400
    invalid = bytearray(raw)
    invalid[0x201] = 0x80
    try:
        parse_fixups(invalid, le)
    except FixupError:
        pass
    else:
        raise AssertionError("unexpected acceptance of unknown fixup flags")
    conflicting = bytearray(raw)
    conflicting[0x20e] = 0x51
    try:
        parse_fixups(conflicting, le)
    except FixupError:
        pass
    else:
        raise AssertionError("conflicting cross-page duplicate not detected")
    print("LE fixup synthetic regression: PASS")


def run(original, destination):
    if destination.exists():
        raise FixupError("destination already exists; refusing overwrite")
    data = original.read_bytes()
    info = probe.inspect(original)
    if info["sha256"] != probe.OFFICIAL_SHA256 or not info["official_v131_reference"]:
        raise FixupError("source does not match official v1.31 SHA-256")
    images = reconstruct(data, info["le_image"])
    if tuple(map(sha256, images)) != EXPECTED_RAW:
        raise FixupError("original LE image hashes differ from repository baseline")
    sites, stats = parse_fixups(data, info["le_image"])
    if (stats["records"], stats["unique_sites"], stats["equal_duplicate_records"]) != (51363, 51318, 45):
        raise FixupError("unexpected official v1.31 relocation count")
    patched = apply(images, sites)
    if tuple(map(sha256, patched)) != EXPECTED_RELOCATED:
        raise FixupError("relocated image hashes differ from independently verified reference")
    manifest = {
        "source_sha256": info["sha256"],
        "raw_object_sha256": list(EXPECTED_RAW),
        "relocated_object_sha256": list(EXPECTED_RELOCATED),
        "relocation_summary": stats,
        "method": "LE internal 32-bit offset fixups resolved to verified object preferred bases",
        "limitations": ["derived static analysis images only",
                        "does not execute the DOS/4GW loader",
                        "never substitutes for gameplay verification"],
    }
    destination.mkdir(parents=True, exist_ok=False)
    try:
        for i, image in enumerate(patched, 1):
            (destination / f"object_{i}.relocated.bin").write_bytes(image)
        (destination / "le-relocations.manifest.json").write_text(
            json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    except BaseException:
        shutil.rmtree(destination)
        raise
    print(json.dumps({"status": "verified", "output_dir": str(destination),
                      "stats": stats}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, nargs="?")
    parser.add_argument("destination", type=Path, nargs="?")
    parser.add_argument("--self-test", action="store_true")
    a = parser.parse_args()
    if a.self_test:
        if a.original or a.destination:
            parser.error("--self-test does not take file paths")
        self_test()
    elif a.original and a.destination:
        run(a.original, a.destination)
    else:
        parser.error("provide original ORION2.EXE and a new output directory")


if __name__ == "__main__":
    main()
