#!/usr/bin/env python3
"""Reconcile authenticated v1.31 Watcom switch inventories without rewriting sources.

The old linear-export switch CSV was incomplete. This merges its 135
source-byte-verified tables with independent audits of 68 CS-indexed game
sites and two CS-prescaled (one game, one support) sites, confirming no
duplicates and every original jump-table DWORD. Original executable is
kept private; output contains counts and provenance only.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"decompilation"
SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"

def readcsv(p):
    with p.open(newline="") as f:return list(csv.DictReader(f))

def loadreport(name):
    return json.loads((D/"reports"/name).read_text())

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SHA:
        raise ValueError("Not the verified source v1.31 executable")
    blob=code.read_bytes()
    if len(blob)!=1410709:
        raise ValueError("Original unrelocated game code image differs")
    funcs={r["name"]:r for r in readcsv(D/"functions.csv")}
    old=readcsv(D/"switch_tables.csv")
    oldcases={}
    for r in readcsv(D/"switch_targets.csv"):
        oldcases.setdefault(int(r["site_hex"],16),[]).append(int(r["target_offset"]))
    old_sites={}
    old_game=0;old_support=0;old_game_cases=0;old_support_cases=0
    for r in old:
        site=int(r["site_offset"])
        name=next((x["function"] for x in readcsv(D/"indirect_transfers.csv")
                   if x["kind"]=="jump" and int(x["site_offset"])==site),None)
        if name is None or name not in funcs:
            raise ValueError(f"Old switch site lacks source symbol {site:#x}")
        game=int(funcs[name]["module_index"])<133
        table=int(r["table_offset"])
        length=int(r["entry_count"])
        vals=[int.from_bytes(blob[table+4*i:table+4*i+4],"little") for i in range(length)]
        if vals!=oldcases.get(site,[]) or any(not 0<=v<len(blob) for v in vals):
            raise ValueError(f"Legacy table original bytes mismatch {site:#x}")
        if site in old_sites:raise ValueError("Duplicate old switch")
        old_sites[site]=len(vals)
        if game:old_game+=1;old_game_cases+=len(vals)
        else:old_support+=1;old_support_cases+=len(vals)
    if (len(old_sites),old_game,old_support,sum(old_sites.values()),
        old_game_cases)!=(135,118,17,1080,943):
        raise ValueError("Legacy source export baseline changed")
    new=loadreport("omitted_game_switches_v131_2026-10-13.json")
    pre=loadreport("omitted_prescaled_dispatches_v131_2026-10-13.json")
    if (new["source_sha256"]!=SHA or pre["source_sha256"]!=SHA):
        raise ValueError("Audit report identity differs")
    extra={}
    for r in new["additional_switches"]:
        site=int(r["site_offset"],16)
        tab=int(r["original_code_table_offset"],16)
        targets=[int(x,16) for x in r["original_case_target_offsets"]]
        count=r["case_count"]
        if count!=len(targets) or site in extra or site in old_sites:
            raise ValueError("New game table overlaps existing evidence")
        actual=[int.from_bytes(blob[tab+4*i:tab+4*i+4],"little") for i in range(count)]
        if targets!=actual or r["watcom_module_index"]>=133:
            raise ValueError(f"New game table original data differs at {site:#x}")
        extra[site]=(count,"game")
    for r in pre["sites"]:
        site=int(r["site_offset"],16)
        tab=int(r["original_table_offset"],16)
        targets=[int(x,16) for x in r["target_offsets"]]
        count=r["case_count"]
        if site in extra or site in old_sites or len(targets)!=count:
            raise ValueError("Prescaled table overlaps existing evidence")
        actual=[int.from_bytes(blob[tab+4*i:tab+4*i+4],"little") for i in range(count)]
        if targets!=actual:
            raise ValueError(f"Prescaled table original data differs at {site:#x}")
        extra[site]=(count,r["module_scope"])
    if (len(new["additional_switches"]),new["additional_original_table_entries"],
        len(pre["sites"]))!=(68,537,2):
        raise ValueError("New inventory differs")
    new_game=sum(1 for n,s in extra.values() if s=="game")
    new_support=sum(1 for n,s in extra.values() if s=="support")
    game_cases=old_game_cases+sum(n for n,s in extra.values() if s=="game")
    support_cases=old_support_cases+sum(n for n,s in extra.values() if s=="support")
    if (new_game,new_support,game_cases,support_cases)!=(69,1,1484,141):
        raise ValueError("Reconciled known game/support counts differ")
    return {
        "source_sha256":SHA,
        "source_inventory":"Watcom original v1.31, original unrelocated LE code bytes",
        "legacy_verified_switch_sites":len(old_sites),
        "legacy_verified_case_entries":sum(old_sites.values()),
        "added_game_sites":new_game,
        "added_support_sites":new_support,
        "added_total_sites":len(extra),
        "reconciled_known_switch_sites":len(old_sites)+len(extra),
        "reconciled_known_game_sites":old_game+new_game,
        "reconciled_known_support_sites":old_support+new_support,
        "reconciled_known_game_case_entries":game_cases,
        "reconciled_known_support_case_entries":support_cases,
        "reconciled_known_case_entries":game_cases+support_cases,
        "inventory_is_exhaustive":False,
        "caveat":"These are distinct original-byte-verified table sites in the three audited representations, not complete executable switch coverage or equivalent C semantics. Some other indirect transfers remain unresolved.",
        "inputs":[
            "decompilation/switch_tables.csv",
            "decompilation/switch_targets.csv",
            "decompilation/reports/omitted_game_switches_v131_2026-10-13.json",
            "decompilation/reports/omitted_prescaled_dispatches_v131_2026-10-13.json"
        ]
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
