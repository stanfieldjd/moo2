#!/usr/bin/env python3
"""Conservative epilogue-byte triage of Watcom cross-function conditional edges.

A target is classified only when the original code bytes at the exact
branch destination form LEAVE? + POP* + RET/RET imm16. This classifies
landing bytes, not full CFG validity or a source-level compiler intent.
"""
from pathlib import Path
from collections import Counter
import argparse
import csv
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
EXPECTED_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"

def readcsv(name):
    with (ROOT/"decompilation"/name).open(newline="") as f:
        return list(csv.DictReader(f))

def decoded_epilogue_length(code,address):
    if address<0 or address>=len(code):
        return 0
    at=address
    if code[at]==0xC9: # LEAVE
        at+=1
    n=0
    while at<len(code) and n<8 and 0x58<=code[at]<=0x5F:
        at+=1
        n+=1
    if not (n or code[address]==0xC9) or at>=len(code):
        return 0
    if code[at]==0xC3:
        return at-address+1
    if code[at]==0xC2 and at+2<len(code):
        return at-address+3
    return 0

def audit(exe,codefile):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXPECTED_SHA:
        raise ValueError("Source executable is not the verified official v1.31")
    blob=codefile.read_bytes()
    if len(blob)!=1410709:
        raise ValueError("LE code image size differs")
    functions={r["name"]:r for r in readcsv("functions.csv")}
    branches=[r for r in readcsv("function_boundary_audit.csv")
              if r["classification"]=="cross_function_conditional"]
    if len(branches)!=311:
        raise ValueError("Unexpected cross-function candidate inventory")
    summaries=Counter()
    results=[]
    for row in branches:
        fn=functions.get(row["name"])
        if fn is None:
            raise ValueError("Branch has no source function")
        module=int(fn["module_index"])
        scope="game" if 0<=module<133 else "support"
        target=int(row["target"])
        length=decoded_epilogue_length(blob,target)
        kind="epilogue-byte-sequence" if length else "requires-cfg-review"
        summaries[scope+"_"+kind]+=1
        results.append({
            "source_function":row["name"],
            "branch_source_offset":hex(int(row["instruction"])),
            "branch_opcode":row["opcode"],
            "target_offset":hex(target),
            "module_scope":scope,
            "target_class":kind,
            "epilogue_bytes":length,
        })
    if (summaries["game_epilogue-byte-sequence"],
        summaries["game_requires-cfg-review"],
        summaries["support_epilogue-byte-sequence"],
        summaries["support_requires-cfg-review"]) != (158,92,1,60):
        raise ValueError("Cross-boundary epilogue classification differs")
    return {
        "original_sha256":EXPECTED_SHA,
        "cross_function_conditional_candidates":len(results),
        "game_module_candidates":250,
        "game_targets_with_epilogue_bytes":158,
        "game_targets_requiring_cfg_review":92,
        "support_module_candidates":61,
        "support_targets_with_epilogue_bytes":1,
        "support_targets_requiring_cfg_review":60,
        "method":"exact original target bytes LEAVE? + POP* + RET or RET imm16; no claim that branches are reachable or calling conventions valid",
        "branches":results,
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path,
                   help="original unrelocated LE object 1 bytes")
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit(a.exe,a.code)
    if a.output:
        a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="branches"},indent=2))
