#!/usr/bin/env python3
"""Audit the 19 indirect CALL sites originating in v1.31 game modules.

Uses locally verified original executable, relocated LE code/data images,
and already exported Watcom symbols. Does not reconstruct executable data
or invent callback targets. Emits metadata only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHA256 = "4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BASE = 0x10000
COLONY_TABLE = 0xB55C
KNOWN_STATIC = {
    0xCDFF0: "colony-indexed-table",
    0xCE24E: "colony-indexed-table",
    0xC7EBC: "conditional-ship-helper",
    0xC7FDB: "conditional-ship-helper",
    0xF3031: "conditional-paragraph-helper",
    0xF3049: "conditional-paragraph-helper",
    0xF3077: "conditional-paragraph-helper",
    0xF309B: "conditional-paragraph-helper",
}
CALLBACK_MECHANISM = {
    0x007C7: "caller-provided function pointer in memory addressed by EAX",
    0x7F22E: "function pointer passed in EAX and saved on stack",
    0x8E273: "function pointer passed in EBX and saved on stack",
    0x902EC: "function pointer passed in EDX and saved on stack",
    0xD989C: "planet-filter predicate passed in EDX",
    0xDDBCC: "building predicate passed in EDX",
    0xF2C91: "callback in caller-provided list object at +0x1e",
    0xF5FE1: "runtime-assignable global data callback slot 0x34f70",
    0xFA287: "callback in caller-provided list object at +0x22",
    0xFA3A5: "callback in caller-provided list object at +0x22",
    0xFCFE8: "callback in caller-provided icon object at +0x1c",
}
# Relocated analysis-image virtual code pointers (NOT original raw code offsets).
SHIP_VA = (0x5EF09, 0x5EF17)
PARA_VA = (0x103CAF, 0x103952)
EXPECTED_TABLE = (0xDE0C6, 0xDED47, 0xDFE77, 0, 0, 0, 0)

def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def fail_if(condition, message):
    if condition:
        raise ValueError(message)

def inspect_calls(functions, sites, code_path):
    """Observe exact CALL bytes in symbol-entry-anchored objdump windows."""
    checked = {}
    for row in sites:
        off = int(row["site_offset"])
        name = row["function"]
        if name not in checked:
            f = functions[name]
            start = int(f["offset"]) + BASE
            end = start + int(f["inferred_size"])
            out = subprocess.run([
                "objdump", "-D", "-M", "intel", "-b", "binary", "-m", "i386",
                "--adjust-vma=0x10000", f"--start-address={start}",
                f"--stop-address={end}", str(code_path)
            ], capture_output=True, text=True, check=True).stdout
            checked[name] = out
        matched = re.search(rf"^\s*{off+BASE:x}:\s+[^\n]*\bcall\s+(.+)$",
                            checked[name], re.M | re.I)
        fail_if(matched is None, f"No decoded call at {hex(off)} in {name}")
        # The exported assembly originates from the same verified code image.
        operand = matched.group(1).lower()
        fail_if("ptr" not in operand,
                f"Indirect-call operand unrecognized at {hex(off)}: {operand}")
    return checked

def run(exe, code, data):
    digest = hashlib.sha256(exe.read_bytes()).hexdigest()
    fail_if(digest != EXPECTED_SHA256, "Original executable SHA-256 does not match v1.31")
    functions_raw = read_csv(ROOT/"decompilation/functions.csv")
    functions = {f["name"]: f for f in functions_raw}
    modules = {int(m["index"]): m["name"] for m in
               read_csv(ROOT/"decompilation/modules.csv")}
    by_addr = {}
    for f in functions_raw:
        by_addr.setdefault(int(f["offset"]), []).append(f["name"])
    sites = []
    for row in read_csv(ROOT/"decompilation/indirect_transfers.csv"):
        if row["kind"] != "call":
            continue
        f = functions.get(row["function"])
        fail_if(f is None, "Unknown function in indirect call inventory")
        if int(f["module_index"]) < 133:
            sites.append(row)
    fail_if(len(sites) != 19, f"Expected 19 game-module indirect calls; got {len(sites)}")
    codebytes, databytes = code.read_bytes(), data.read_bytes()
    fail_if(len(codebytes) != 1410709, "Relocated LE code object size mismatch")
    fail_if(len(databytes) < COLONY_TABLE + 28, "Data table outside image")
    checked = inspect_calls(functions, sites, code)
    values = [int.from_bytes(databytes[COLONY_TABLE+i*4:COLONY_TABLE+(i+1)*4],
                             "little") for i in range(7)]
    fail_if(tuple(values) != EXPECTED_TABLE, "Colony dispatch pointer table differs")
    # Static helper selection is demonstrated by two constant-pointer
    # stores feeding one saved stack variable in each routine.
    tests = [
        ("Ship_Rough_Strength_At_Star_", "ebp-0x24", SHIP_VA),
        ("Ship_Min_Strength_Versus_Players_At_Star_", "ebp-0xc", SHIP_VA),
        ("_Squeeze_Print_Paragraph_", "ebp-0x24", PARA_VA),
    ]
    for name, local, pointers in tests:
        dump = checked[name]
        for pointer in pointers:
            probe = rf"mov\s+DWORD PTR \[{re.escape(local)}\],0x{pointer:x}\b"
            fail_if(re.search(probe, dump, re.I) is None,
                    f"Missing constant-pointer store {name} -> {hex(pointer)}")
    dynamic = set(CALLBACK_MECHANISM)
    static = set(KNOWN_STATIC)
    actual = {int(row["site_offset"]) for row in sites}
    fail_if(actual != (static | dynamic) or static & dynamic,
            "Indirect site classifications are incomplete or overlapping")
    resolved = []
    for row in sorted(sites, key=lambda r:int(r["site_offset"])):
        off = int(row["site_offset"])
        if off in (0xCDFF0, 0xCE24E):
            targets = [dict(index=i, code_offset=hex(val-BASE),
                 watcom_symbols=by_addr.get(val-BASE, []))
                 for i,val in enumerate(values) if val]
        elif off in (0xC7EBC, 0xC7FDB):
            targets = [dict(code_offset=hex(val-BASE),
                  watcom_symbols=by_addr.get(val-BASE, [])) for val in SHIP_VA]
        elif off in (0xF3031, 0xF3049, 0xF3077, 0xF309B):
            targets = [dict(code_offset=hex(val-BASE),
                  watcom_symbols=by_addr.get(val-BASE, [])) for val in PARA_VA]
        else:
            targets = []
        for target in targets:
            fail_if(not target["watcom_symbols"], "Static target is not a named CODE entry")
        resolved.append({
            "site_hex": hex(off),
            "function": row["function"],
            "module": modules[int(functions[row["function"]]["module_index"])],
            "source_operand": row["operand"],
            "classification": KNOWN_STATIC.get(off, "runtime-dependent-callback"),
            "verified_static_targets": targets,
            "unresolved_reason": CALLBACK_MECHANISM.get(off),
        })
    counts = Counter(r["classification"] for r in resolved)
    fail_if(sum(counts.values()) != 19 or counts["runtime-dependent-callback"] != 11,
            "Indirect classification accounting differs")
    return {
        "original_sha256": digest,
        "game_module_count": 133,
        "game_indirect_call_sites": len(sites),
        "known_static_dispatch_sites": len(static),
        "runtime_dependent_callback_sites": len(dynamic),
        "classifications": dict(sorted(counts.items())),
        "sources": ["decompilation/functions.csv", "decompilation/modules.csv",
                    "decompilation/indirect_transfers.csv",
                    "verified relocated LE code object", "verified relocated LE data object"],
        "scope": "static target provenance only; no game-rule execution, dynamic callback resolution, or C-source recovery",
        "sites": resolved,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", required=True, type=Path)
    parser.add_argument("--code", required=True, type=Path)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.exe, args.code, args.data)
    content = json.dumps(result, indent=2)+"\n"
    if args.output:
        args.output.write_text(content)
    print(json.dumps({k:v for k,v in result.items() if k != "sites"}, indent=2))
