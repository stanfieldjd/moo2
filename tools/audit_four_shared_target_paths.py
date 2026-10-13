#!/usr/bin/env python3
"""Original-code closure audit for four previously nontrivial game branch paths.

Walks machine instructions from an *observed target entry* within explicit,
source-verified Watcom symbol intervals and bounded shared tail ranges.
Calls are modeled as fall-through only; this checks possible return paths,
not callee behavior, side effects, calling conventions or dynamic execution.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"decompilation"
SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
TARGET=re.compile(r"^0x([0-9a-f]+)\b",re.I)

CASES=[
    {
        "source":"Draw_Special_Systems_Replacement_Box_",
        "branch_offset":0x558FB,"entry":0x5583A,
        "owner":"Draw_Generic_Replacement_Box_",
        "extra":[(0x56268,0x5626E),(0x58D37,0x58D3D)],
        "required_tail_offsets":[0x56268,0x58D37],
        "meaning":"UI helper invocation followed by two chained shared exits",
    },
    {
        "source":"Fleet_Box_Data_",
        "branch_offset":0x61A57,"entry":0x610CA,
        "owner":"First_Unselected_Icon_","extra":[],
        "required_tail_offsets":[],
        "meaning":"fleet UI shared path with an internal return",
    },
    {
        "source":"Ship_Owner_",
        "branch_offset":0x68003,"entry":0x6892D,
        "owner":"Ship_Icon_Y_","extra":[],
        "required_tail_offsets":[],
        "meaning":"ship record classification subgraph with multiple returns",
    },
    {
        "source":"Officer_Cost_",
        "branch_offset":0x87A56,"entry":0x84807,
        "owner":"Officer_Skill_Value_",
        "extra":[(0x841B5,0x841BB)],
        "required_tail_offsets":[0x841B5],
        "meaning":"officer cost/bonus subgraph leading to a shared return",
    },
]

def read_rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def disassemble(binary,start,end):
    run=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--start-address=0x{start:x}",f"--stop-address=0x{end:x}",str(binary)],
        capture_output=True,text=True,check=True)
    ins={}
    for line in run.stdout.splitlines():
        match=RX.match(line)
        if match:
            ins[int(match[1],16)]=(len(match[2].split()),match[3].lower(),match[4].strip())
    return ins

def resolve_operand(text):
    m=TARGET.match(text)
    return int(m[1],16) if m else None

def walk(binary,entry,allowed):
    ins={}
    for start,end in allowed:
        for key,rec in disassemble(binary,start,end).items():
            if key in ins and ins[key]!=rec:raise ValueError("Conflicting disassembly")
            ins[key]=rec
    queued=[entry]
    visited=set()
    returns=[]
    calls=[]
    edges=[]
    while queued:
        addr=queued.pop()
        if addr in visited:continue
        if addr not in ins:raise ValueError(f"Unresolved branch outside audited regions: {addr:#x}")
        if len(visited)>4000:raise ValueError("Closure traversal limit exceeded")
        visited.add(addr)
        n,mnem,oper=ins[addr]
        fall=addr+n
        if mnem in ("ret","retf","iret","iretd"):
            returns.append(addr)
        elif mnem=="jmp":
            target=resolve_operand(oper)
            if target is None:raise ValueError(f"Unclassified dynamic jump: {addr:#x}")
            edges.append([hex(addr),hex(target)])
            queued.append(target)
        elif (mnem.startswith("j") and mnem!="jmp") or mnem.startswith("loop"):
            target=resolve_operand(oper)
            if target is None:raise ValueError(f"Unknown conditional target: {addr:#x}")
            queued.extend([fall,target])
            edges.append([hex(addr),hex(target)])
        else:
            if mnem.startswith("call"):calls.append(addr)
            queued.append(fall)
    if not returns:raise ValueError("No proven return")
    return visited,returns,calls,edges

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SHA:
        raise ValueError("Not the original verified v1.31 executable")
    if code.stat().st_size!=1410709:
        raise ValueError("Unrelocated LE code size mismatch")
    functions={r["name"]:r for r in read_rows(DATA/"functions.csv")}
    rows=[]
    for case in CASES:
        owner=functions[case["owner"]]
        start,end=int(owner["offset"]),int(owner["inferred_end"])
        allowed=[(start,end)]+case["extra"]
        if not start<=case["entry"]<end:
            raise ValueError("Target entry outside reported owner")
        source=functions[case["source"]]
        source_ins=disassemble(code,int(source["offset"]),int(source["inferred_end"]))
        branch=source_ins.get(case["branch_offset"])
        if branch is None or not branch[1].startswith("j") or resolve_operand(branch[2])!=case["entry"]:
            raise ValueError("Source branch no longer matches target")
        visited,exits,calls,edges=walk(code,case["entry"],allowed)
        for addr in case["required_tail_offsets"]:
            if addr not in visited:
                raise ValueError(f"Required shared-tail entry not visited: {addr:#x}")
        rows.append({
            "source_function":case["source"],
            "conditional_source_offset":hex(case["branch_offset"]),
            "target_entry":hex(case["entry"]),
            "target_owner":case["owner"],
            "visited_instructions":len(visited),
            "direct_calls_treated_as_fallthrough":len(calls),
            "observed_return_offsets":[hex(x) for x in sorted(exits)],
            "verified_shared_tail_entries":[hex(x) for x in case["required_tail_offsets"]],
            "meaning":case["meaning"],
        })
    if len(rows)!=4:raise ValueError("Expected four cases")
    return {
        "original_sha256":SHA,
        "source_verified_target_paths":len(rows),
        "all_targets_have_bounded_return_paths":all(x["observed_return_offsets"] for x in rows),
        "scope":"bounded source instruction graph and named shared tails; calls not followed; source-level semantics/stack correctness remain unverified",
        "paths":rows,
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
