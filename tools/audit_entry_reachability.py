#!/usr/bin/env python3
"""Audit entry-reachability of non-simple-epilogue v1.31 game branches.

Walks decoded x86 instructions from each original Watcom function entry,
following *bounded* direct fall-through/jump edges and previously verified
switch-table cases. A site not reached by this walk is NOT proven dead:
cross-symbol shared tails, mixed-mode instruction alignment or external
entry paths may remain. Only metadata, never original machine code, is output.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "decompilation"
SOURCE_SHA = "4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
INSTRUCTION = re.compile(
    r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$", re.I
)
TARGET = re.compile(r"^0x([0-9a-f]+)(?:\b|$)", re.I)
STOP = {"ret", "retf", "iret", "iretd", "hlt", "ud2"}

def rows(filename):
    with (D / filename).open(newline="") as fp:
        return list(csv.DictReader(fp))

def simple_return_epilogue(raw, addr):
    if not (0 <= addr < len(raw)):
        return False
    at = addr
    if raw[at] == 0xC9: # LEAVE
        at += 1
    n = 0
    while at < len(raw) and n < 8 and 0x58 <= raw[at] <= 0x5F:
        at += 1
        n += 1
    return (n > 0 or raw[addr] == 0xC9) and (
        at < len(raw) and raw[at] in (0xC2, 0xC3)
        and (raw[at] != 0xC2 or at + 2 < len(raw))
    )

def decoded_interval(binary, start, end):
    process = subprocess.run(
        ["objdump", "-D", "-M", "intel", "-b", "binary", "-m", "i386",
         f"--start-address=0x{start:x}", f"--stop-address=0x{end:x}", str(binary)],
        capture_output=True, text=True, check=True
    )
    instructions = {}
    for line in process.stdout.splitlines():
        match = INSTRUCTION.match(line)
        if match:
            instructions[int(match[1], 16)] = (
                len(match[2].split()), match[3].lower(), match[4].strip()
            )
    return instructions

def reachable_entry_addresses(start, end, instructions, switches):
    """Conservative bounded 32-bit CFG walk; never crosses symbol intervals."""
    seen = set()
    pending = [start]
    while pending and len(seen) < 200000:
        addr = pending.pop()
        if addr in seen or not (start <= addr < end):
            continue
        record = instructions.get(addr)
        if record is None:
            continue
        seen.add(addr)
        size, mnemonic, operands = record
        fall = addr + size
        if addr in switches:
            destinations = switches[addr]
        elif mnemonic in STOP:
            destinations = []
        elif mnemonic == "jmp":
            match = TARGET.match(operands)
            destinations = [int(match[1], 16)] if match else []
        elif (mnemonic.startswith("j") and mnemonic != "jmp") or mnemonic.startswith("loop"):
            match = TARGET.match(operands)
            destinations = [fall] + ([int(match[1], 16)] if match else [])
        else:
            # Calls are not followed; their ordinary fall-through is.
            destinations = [fall]
        pending.extend(destinations)
    if len(seen) >= 200000:
        raise ValueError("Exceeded per-function traversal safety bound")
    return seen

def audit(executable, raw_code):
    if hashlib.sha256(executable.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("Original executable is not the verified v1.31")
    blob = raw_code.read_bytes()
    if len(blob) != 1410709:
        raise ValueError("Original unrelocated code-object size changed")
    functions = {r["name"]:r for r in rows("functions.csv")}
    cross = [r for r in rows("function_boundary_audit.csv")
             if r["classification"] == "cross_function_conditional"
             and r["name"] in functions
             and 0 <= int(functions[r["name"]]["module_index"]) < 133]
    if len(cross) != 250:
        raise ValueError("Game-code candidate source inventory changed")
    candidates = [r for r in cross if not simple_return_epilogue(blob,int(r["target"]))]
    if len(candidates) != 92:
        raise ValueError("Non-simple-epilogue candidate inventory changed")
    switches = defaultdict(list)
    for r in rows("switch_targets.csv"):
        switches[int(r["site_hex"],16)].append(int(r["target_offset"]))
    examined = []
    counts = Counter()
    cache = {}
    for branch in candidates:
        f = functions[branch["name"]]
        start, end = int(f["offset"]), int(f["inferred_end"])
        source = int(branch["instruction"])
        if branch["name"] not in cache:
            instructions = decoded_interval(raw_code,start,end)
            reachable = reachable_entry_addresses(start,end,instructions,switches)
            cache[branch["name"]] = (instructions,reachable)
        instructions, reachable = cache[branch["name"]]
        if source not in instructions:
            raise ValueError("Recorded branch source not decoded from source interval")
        mode = "reachable_from_symbol_entry" if source in reachable else "not_established_by_bounded_walk"
        counts[mode] += 1
        examined.append({
            "source_function":branch["name"],
            "source_branch_offset":hex(source),
            "branch_opcode":branch["opcode"],
            "destination_offset":hex(int(branch["target"])),
            "destination_relation":branch["target_relation"],
            "destination_owner":branch["target_owner"],
            "status":mode,
            "decoded_reachable_addresses_in_source_interval":len(reachable),
        })
    if (counts["reachable_from_symbol_entry"],
        counts["not_established_by_bounded_walk"]) != (63,29):
        raise ValueError("Branch reachability accounting differs from expected original")
    return {
        "original_sha256":SOURCE_SHA,
        "previous_non_simple_epilogue_game_branches":len(candidates),
        "reachable_from_symbol_entry":counts["reachable_from_symbol_entry"],
        "not_established_by_bounded_walk":counts["not_established_by_bounded_walk"],
        "scope":"entry-anchored, same-symbol-interval direct x86 CFG with recovered switch cases; negative result does NOT imply dead code",
        "entries":examined,
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path,
                   help="original unrelocated LE object 1 bytes")
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=audit(a.exe,a.code)
    if a.output:
        a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="entries"},indent=2))
