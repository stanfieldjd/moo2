#!/usr/bin/env python3
"""Classify source-reachable game cross-function branch destinations.

Uses the verified official v1.31 executable, unrelocated original code
object, and the preceding entry-reachability audit. A return-path
recognition is a constrained machine-instruction shape, NOT stack-frame
compatibility, executable reachability proof, or source-code equivalence.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
REGS={"eax","ax","al","ebx","bx","ecx","cx","edx","dx","esi","edi","ebp","si","di"}

def strict_return_bytes(blob,addr):
    if not(0<=addr<len(blob)): return False
    p=addr
    if blob[p]==0xc9:p+=1
    n=0
    while p<len(blob) and n<8 and 0x58<=blob[p]<=0x5f:p+=1;n+=1
    return bool(n or blob[addr]==0xc9) and p<len(blob) and (
        blob[p]==0xc3 or (blob[p]==0xc2 and p+2<len(blob))
    )

def decode_at(code,addr):
    completed=subprocess.run(["objdump","-D","-M","intel","-b","binary",
         "-m","i386",f"--start-address=0x{addr:x}",
         f"--stop-address=0x{addr+55:x}",str(code)],
         text=True,capture_output=True,check=True)
    result={}
    for line in completed.stdout.splitlines():
        m=RX.match(line)
        if m:result[int(m[1],16)]=(len(m[2].split()),m[3].lower(),m[4].strip())
    return result

def recognize_exit(blob,decoded,addr):
    p=addr
    for index in range(13):
        inst=decoded.get(p)
        if inst is None:return None
        count,op,args=inst
        if op in ("ret","retf"):
            return "straight_line_return_sequence"
        if op in ("pop","leave") and (op=="leave" or args in REGS):
            pass
        elif op=="lea" and args.startswith("esp,[ebp"):
            pass
        elif op in ("mov","movsx","movzx"):
            a=args.replace("DWORD PTR ","").replace("WORD PTR ","").replace("BYTE PTR ","")
            parts=a.split(",",1)
            if len(parts)!=2 or parts[0] not in REGS or not (
                parts[1] in REGS or parts[1].startswith("[ebp") or parts[1].startswith("0x")
            ):return None
        elif op=="xor" and args in ("eax,eax","ax,ax","edx,edx"):
            pass
        elif op=="jmp" and args.startswith("0x"):
            target=int(args,16)
            return "one_hop_to_return_epilogue" if strict_return_bytes(blob,target) else None
        else:
            return None
        p+=count
    return None

def audit(exe,code,reachability):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError("Official game executable SHA mismatch")
    blob=code.read_bytes()
    if len(blob)!=1410709:raise ValueError("Original LE code object size differs")
    prior=json.loads(reachability.read_text())
    if prior.get("original_sha256")!=SOURCE_SHA or prior.get("previous_non_simple_epilogue_game_branches")!=92:
        raise ValueError("Prior reachability evidence changed")
    entries=prior["entries"]
    counts=Counter()
    result=[]
    cache={}
    for row in entries:
        site=int(row["destination_offset"],16)
        if row["status"]=="not_established_by_bounded_walk":
            cls="source_not_established_by_bounded_walk"
        elif row["status"]=="reachable_from_symbol_entry":
            if row["destination_relation"]=="entry":
                cls="destination_is_another_named_function_entry"
            else:
                if site not in cache:cache[site]=decode_at(code,site)
                cls=recognize_exit(blob,cache[site],site) or "reachable_nontrivial_cfg_target"
        else:raise ValueError("Unexpected source reachability status")
        counts[cls]+=1
        result.append({"source_function":row["source_function"],
                       "branch_source_offset":row["source_branch_offset"],
                       "branch_target_offset":row["destination_offset"],
                       "target_symbol":row["destination_owner"],
                       "classification":cls})
    expected={
        "source_not_established_by_bounded_walk":29,
        "destination_is_another_named_function_entry":8,
        "straight_line_return_sequence":32,
        "one_hop_to_return_epilogue":10,
        "reachable_nontrivial_cfg_target":13
    }
    if dict(counts)!=expected:raise ValueError(f"Unexpected classification totals: {dict(counts)}")
    return {
        "original_sha256":SOURCE_SHA,
        "input_candidates":92,
        "classifications":dict(counts),
        "summary":"50 source-reachable sites have statically recognizable exit or other-entry shapes; 13 are other reachable CFG paths; 29 not established by bounded traversal",
        "limit":"structural machine-code classification only; no stack correctness, case semantics, or false-positive/dead-code determination",
        "entries":result,
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--reachability",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    data=audit(args.exe,args.code,args.reachability)
    if args.output:args.output.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({k:v for k,v in data.items() if k!="entries"},indent=2))
