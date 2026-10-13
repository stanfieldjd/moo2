#!/usr/bin/env python3
"""Verify recovered game switch tables against authentic v1.31 CODE bytes.

This checks all game-module indirect JMP sites, table lengths and every
original 32-bit branch target. It does not demonstrate reachable runtime
states or decompile the case bodies.
"""
from collections import defaultdict
from pathlib import Path
import argparse
import csv
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"

def read_rows(name):
    with (ROOT/"decompilation"/name).open(newline="") as file:
        return list(csv.DictReader(file))

def audit(exe, code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXPECTED_SHA:
        raise ValueError("Original v1.31 image identity mismatch")
    raw=code.read_bytes()
    if len(raw)!=1410709:
        raise ValueError("Raw original LE CODE object size differs")
    funcs={r["name"]:r for r in read_rows("functions.csv")}
    jumps=[r for r in read_rows("indirect_transfers.csv") if r["kind"]=="jump"
           and r["function"] in funcs
           and 0<=int(funcs[r["function"]]["module_index"])<133]
    tables={int(r["site_offset"]):r for r in read_rows("switch_tables.csv")}
    targets=defaultdict(list)
    for row in read_rows("switch_targets.csv"):
        targets[int(row["site_hex"],16)].append(row)
    if len(jumps)!=118 or len({int(r["site_offset"]) for r in jumps})!=118:
        raise ValueError("Game-module jump inventory differs")
    result=[]
    unique=set()
    for jump in sorted(jumps,key=lambda r:int(r["site_offset"])):
        site=int(jump["site_offset"])
        record=tables.get(site)
        if record is None:
            raise ValueError(f"Missing switch table at {site:#x}")
        start=int(record["table_offset"])
        count=int(record["entry_count"])
        cases=targets[site]
        if count<=0 or count>4096 or len(cases)!=count or start+count*4>len(raw):
            raise ValueError(f"Bad table boundary at {site:#x}")
        for index,entry in enumerate(cases):
            val=int.from_bytes(raw[start+4*index:start+4*(index+1)],"little")
            if int(entry["case_index"])!=index or val!=int(entry["target_offset"]):
                raise ValueError(f"Case target mismatch {site:#x} index {index}")
            if val>=len(raw):
                raise ValueError(f"Out of bounds target at {site:#x}")
            unique.add(val)
        result.append({
            "site_offset":hex(site),
            "function":jump["function"],
            "table_offset":hex(start),
            "case_count":count,
            "dispatch_evidence":record["dispatch_evidence"]
        })
    return {
        "original_sha256":EXPECTED_SHA,
        "game_indirect_jump_sites":len(jumps),
        "sites_with_verified_switch_tables":len(result),
        "verified_game_switch_case_entries":sum(x["case_count"] for x in result),
        "distinct_game_switch_case_targets":len(unique),
        "scope":"static table bytes and case inventory only; dynamic reachability, Watcom CFG boundaries, case semantics and full code recovery remain separately unproven",
        "sites":result
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True,
                   help="Raw, unrelocated original LE object 1 (not relocated)")
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=audit(a.exe,a.code)
    if a.output:
        a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="sites"},indent=2))
