#!/usr/bin/env python3
"""Audit two missed original Watcom prescaled CS:[EAX+TABLE] JMP dispatches.

Original v1.31 source hash, exact opcode, guard and DWORD targets verified
against the unrelocated LE CODE object. These are supplemental to existing
global disassembly/indirect-transfer inventories; no game data is modified.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
SPECS=[
    {
        "site":0xACF3E,"table":0xACE92,
        "watcom_function":"Do_Colony_Info_Military_Stuff_For_",
        "guard_cmp":(0xACF35,"cmp","dword ptr [ebp-0x10],0x3"),
        "guard_ja":(0xACF39,"ja","0xacf9d"),
        "scale":(0xACF2A,"shl","eax,0x2"),
        "targets":[0xACF45,0xACF9D,0xACF9D,0xACF9D],
        "scope":"game",
    },
    {
        "site":0x117190,"table":0x117145,
        "watcom_function":"Farload_Library_Data_",
        "guard_cmp":(0x117180,"cmp","dword ptr [ebp-0x38],0x3"),
        "guard_ja":(0x117184,"ja","0x11720c"),
        "scale":(0x11718D,"shl","eax,0x2"),
        "targets":[0x117197,0x1171BA,0x1171E0,0x117206],
        "scope":"support",
    },
]

def decode(code,start,end):
    run=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--start-address=0x{start:x}",f"--stop-address=0x{end:x}",str(code)],
        capture_output=True,text=True,check=True).stdout
    result={}
    for l in run.splitlines():
        m=RX.match(l)
        if m:result[int(m[1],16)]=(m[3].lower(),m[4].strip().lower())
    return result

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXPECTED:
        raise ValueError("Original v1.31 executable identity mismatch")
    blob=code.read_bytes()
    if len(blob)!=1410709:raise ValueError("Wrong unrelocated LE code object")
    with (ROOT/"decompilation/functions.csv").open(newline="") as f:
        funcs={r["name"]:r for r in csv.DictReader(f)}
    with (ROOT/"decompilation/indirect_transfers.csv").open(newline="") as f:
        known={int(r["site_offset"]) for r in csv.DictReader(f) if r["kind"]=="jump"}
    with (ROOT/"decompilation/switch_tables.csv").open(newline="") as f:
        known_tables={int(r["site_offset"]) for r in csv.DictReader(f)}
    out=[]
    for spec in SPECS:
        site=spec["site"]
        if site in known or site in known_tables:
            raise ValueError(f"Previously omitted dispatch unexpectedly appears in exported inventory: {site:#x}")
        fun=funcs[spec["watcom_function"]]
        if not(int(fun["offset"])<=site<int(fun["inferred_end"])):
            raise ValueError(f"Dispatch site outside source CODE symbol: {site:#x}")
        if (int(fun["module_index"])<133)!=(spec["scope"]=="game"):
            raise ValueError(f"Watcom module classification changed: {site:#x}")
        if blob[site:site+3]!=bytes.fromhex("2e ff a0"):
            raise ValueError(f"Original CS-jmp-EAX opcode changed: {site:#x}")
        tab=int.from_bytes(blob[site+3:site+7],"little")
        if tab!=spec["table"]:
            raise ValueError("Encoded original jump table offset changed")
        checks=[spec["guard_cmp"],spec["guard_ja"],spec["scale"]]
        for at,op,arg in checks:
            actual=decode(code,at,at+12)
            if actual.get(at)!=(op,arg):
                raise ValueError(f"Original guard/scale instruction mismatch at {at:#x}: {actual.get(at)}")
        actual=decode(code,site,site+7)
        if actual.get(site)!=("jmp",f"dword ptr cs:[eax+0x{tab:x}]"):
            raise ValueError(f"Actual JMP disassembly mismatch {site:#x}")
        cases=[int.from_bytes(blob[tab+4*i:tab+4*i+4],"little") for i in range(4)]
        if cases!=spec["targets"] or any(not(0<=v<len(blob)) for v in cases):
            raise ValueError("Original four-case table mismatch")
        out.append({
            "site_offset":hex(site),"watcom_symbol":spec["watcom_function"],
            "watcom_module_index":int(fun["module_index"]),
            "module_scope":spec["scope"],"original_table_offset":hex(tab),
            "scale_instruction_offset":hex(spec["scale"][0]),
            "guard_cmp_offset":hex(spec["guard_cmp"][0]),
            "guard_ja_offset":hex(spec["guard_ja"][0]),
            "case_count":4,
            "target_offsets":[hex(v) for v in cases],
            "switch_inventory_omitted":True
        })
    return {
        "source_sha256":EXPECTED,
        "omitted_prescaled_sites":len(out),
        "omitted_game_sites":1,
        "omitted_support_sites":1,
        "case_entries":8,
        "scope":"exact original CS indexed indirect JMPs, nearby scale and bounds guards, four original DWORD targets per site; not full function equivalence",
        "sites":out,
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
