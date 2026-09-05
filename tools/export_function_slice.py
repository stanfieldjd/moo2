#!/usr/bin/env python3
"""Export a named recovered function as a small raw x86 analysis slice.

Development-only. Reads the verified reconstructed code object, never ORION2.EXE,
and emits only the requested function bytes plus metadata suitable for offline
cross-decompiler comparison.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FUNCS = ROOT / "decompilation" / "functions.csv"
CODE = ROOT / "decompilation" / "code_object_1.bin"

def intval(v: str) -> int:
    return int(v, 0)

def load(name: str):
    with FUNCS.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    exact = [r for r in rows if r.get("name") == name]
    if len(exact) != 1:
        raise SystemExit(f"expected exactly one symbol named {name!r}, found {len(exact)}")
    return exact[0]

def pick(row, *keys):
    for k in keys:
        v = row.get(k)
        if v not in (None, ""):
            return intval(v)
    raise SystemExit(f"missing any of fields {keys}; available={sorted(row)}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("symbol")
    ap.add_argument("--out", type=Path, default=ROOT / "analysis" / "function_slices")
    a = ap.parse_args()
    row = load(a.symbol)
    start = pick(row, "object_offset", "code_offset", "start_offset", "offset")
    if row.get("size"):
        size = intval(row["size"])
    elif row.get("inferred_size"):
        size = intval(row["inferred_size"])
    elif row.get("inferred_end"):
        size = intval(row["inferred_end"]) - start
    else:
        end = pick(row, "end_object_offset", "end_offset", "next_offset")
        size = end - start
    if size <= 0:
        raise SystemExit(f"invalid provisional size {size}")
    code = CODE.read_bytes()
    if start < 0 or start + size > len(code):
        raise SystemExit("slice outside reconstructed code object")
    blob = code[start:start+size]
    a.out.mkdir(parents=True, exist_ok=True)
    stem = a.symbol.rstrip("_") or "function"
    raw = a.out / f"{stem}.bin"
    meta = a.out / f"{stem}.json"
    raw.write_bytes(blob)
    metadata = {
        "symbol": a.symbol,
        "object_offset": start,
        "size": size,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "architecture": "x86-32",
        "format": "raw function slice",
        "boundary_status": "provisional recovered-symbol boundary",
        "source": "reconstructed LE code object; original executable not included",
    }
    meta.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(raw)
    print(meta)

if __name__ == "__main__":
    main()
