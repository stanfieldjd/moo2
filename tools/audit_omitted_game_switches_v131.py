#!/usr/bin/env python3
"""Find original v1.31 CS-indexed switch dispatches missed by linear export.

Read-only, original-executable-hash-guarded analysis. Scans the raw LE CODE
object for CS: FF /4 indirect JMP with scale-4 SIB and absolute table address,
filters known exported sites, then validates each new site's actual i386
instruction, nearest local unsigned upper-bound check or original Watcom
REPNE SCAS case-dispatch idiom, and every selected original table DWORD.

The observed guard and original target addresses establish bounded *static
table provenance*, not whole-function reachability or equivalent source C.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"decompilation"
SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
BOUNDED_MAX=256
PREFIX=b"\x2e\xff\x24"
SPECIAL_SITE=0xE3C1
SPECIAL_TABLE=0xDEB0
SPECIAL_COUNT=14

def readcsv(name):
    with (DATA/name).open(newline="") as fp:
        return list(csv.DictReader(fp))

def local_disassembly(code,site):
    start=max(0,site-96)
    out=subprocess.run([
       "objdump","-D","-M","intel","-b","binary","-m","i386",
       f"--start-address=0x{start:x}",f"--stop-address=0x{site+8:x}",
       str(code)
    ],capture_output=True,text=True,check=True).stdout
    records=[]
    for line in out.splitlines():
        m=RX.match(line)
        if m:
            records.append((int(m[1],16),m[3].lower(),m[4].strip().lower()))
    return records

def verify_site_instruction(code,site,table,reg):
    # Deliberately decode directly from source site; linear disassembly
    # can lose instruction synchronization after embedded jump table data.
    result=subprocess.run([
        "objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--start-address=0x{site:x}",f"--stop-address=0x{site+8:x}",
        str(code)
    ],capture_output=True,text=True,check=True).stdout
    records=[(int(m[1],16),m[3].lower(),m[4].strip().lower())
             for line in result.splitlines() if (m:=RX.match(line))]
    expected=f"dword ptr cs:[{reg}*4+0x{table:x}]"
    if not records or records[0]!=(site,"jmp",expected):
        raise ValueError(f"Original dispatch mismatch {site:#x}: {records[:2]}")

def guarded_case(site,inst):
    hit=next((i for i,x in enumerate(inst) if x[0]==site and x[1]=="jmp"),None)
    if hit is None:raise ValueError(f"Original indexed JMP missing locally at {site:#x}")
    for i in range(hit-1,max(-1,hit-26),-1):
        at,op,operand=inst[i]
        if op not in ("ja","jnbe") or i==0:continue
        prev=inst[i-1]
        if prev[1]!="cmp":continue
        m=re.search(r",0x([0-9a-f]+)$",prev[2])
        if not m:continue
        bound=int(m[1],16)
        if 0<=bound<=BOUNDED_MAX:
            if not operand.startswith("0x"):
                continue
            dest=int(operand,16)
            return {
                "dispatch_evidence":"local-cmp-ja",
                "guard_comparison_offset":hex(prev[0]),
                "guard_jump_offset":hex(at),
                "guard_default_offset":hex(dest),
                "guard_operand":prev[2],
                "case_count":bound+1,
            }
    if site!=SPECIAL_SITE:
        raise ValueError(f"No original local case guard found at {site:#x}")
    if len(inst)<5 or not any(
        x[0]==0xE3AD and x[1]=="mov" and x[2]=="ecx,0xe" for x in inst
    ) or not any(
        x[0]==0xE3BE and x[1]=="repnz" and "scas ax" in x[2] for x in inst
    ):
        raise ValueError("Original Watcom fourteen-way SCAS dispatch changed")
    return {
        "dispatch_evidence":"mov-ecx-14-repnz-scasw",
        "guard_comparison_offset":None,
        "guard_jump_offset":"0xe3be",
        "guard_default_offset":None,
        "guard_operand":"ECX index after bounded REPNE SCASW with original count 14",
        "case_count":SPECIAL_COUNT,
    }

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SHA:
        raise ValueError("Executable SHA-256 does not match original v1.31")
    blob=code.read_bytes()
    if len(blob)!=1410709:
        raise ValueError("Wrong original unrelocated LE CODE object")
    starts=sorted((int(r["offset"]),int(r["module_index"]),r["name"])
                  for r in readcsv("functions.csv"))
    known={int(r["site_offset"]) for r in readcsv("indirect_transfers.csv")
           if r["kind"]=="jump"}
    known_tables={int(r["site_offset"]) for r in readcsv("switch_tables.csv")}
    entries=[]
    previously_known_raw=0
    all_sib=0
    cursor=0
    while (site:=blob.find(PREFIX,cursor))!=-1:
        cursor=site+1
        if site+8>len(blob) or blob[site+3] & 0xC7 != 0x85:
            continue
        j=bisect.bisect_right(starts,(site,10000,"zzzz"))-1
        if j<0 or starts[j][1]>=133:
            continue
        all_sib+=1
        if site in known:
            previously_known_raw+=1
            continue
        table=int.from_bytes(blob[site+4:site+8],"little")
        index_reg=("eax","ecx","edx","ebx","esp","ebp","esi","edi")[(blob[site+3] >> 3) & 7]
        # The SIB operand indexes the original CODE object directly.
        verify_site_instruction(code,site,table,index_reg)
        inst=local_disassembly(code,site)
        guard=guarded_case(site,inst)
        count=guard["case_count"]
        if table+count*4>len(blob):
            raise ValueError(f"Switch table out of source CODE bounds {site:#x}")
        values=[int.from_bytes(blob[table+4*i:table+4*i+4],"little")
                for i in range(count)]
        if any(not(0<=v<len(blob)) for v in values):
            raise ValueError(f"One original switch target leaves CODE object at {site:#x}")
        entries.append({
            "site_offset":hex(site),"watcom_symbol":starts[j][2],
            "watcom_module_index":starts[j][1],"index_register":index_reg,
            "original_code_table_offset":hex(table),
            **guard,
            "distinct_target_count":len(set(values)),
            "original_case_target_offsets":[hex(x) for x in values],
            "existing_indirect_inventory":False,
        })
    if all_sib!=179 or previously_known_raw!=111 or len(entries)!=68:
        raise ValueError(f"Indexed game opcode inventory changed: {all_sib}/{previously_known_raw}/{len(entries)}")
    stats=Counter(x["dispatch_evidence"] for x in entries)
    if (stats["local-cmp-ja"],stats["mov-ecx-14-repnz-scasw"])!=(67,1):
        raise ValueError(f"Bounded switch classification differs: {dict(stats)}")
    if any(int(x["site_offset"],16) in known_tables for x in entries):
        raise ValueError("New table duplicates an existing exported switch")
    return {
        "source_sha256":SHA,
        "scope":"additive original CODE byte-level audit only; does not prove overall switch scan completeness, every dispatch's dynamic reachability or full C-level function equivalents",
        "opcode_family":"CS segment override + FF /4 + scale-four SIB absolute CODE-table",
        "game_raw_sib_candidates":all_sib,
        "previously_recorded_game_sib_candidates":previously_known_raw,
        "additional_game_switch_sites":len(entries),
        "local_cmp_ja_case_bound_sites":stats["local-cmp-ja"],
        "repnz_scas_word_count_bound_sites":stats["mov-ecx-14-repnz-scasw"],
        "additional_original_table_entries":sum(x["case_count"] for x in entries),
        "prior_verified_game_switch_sites_in_older_inventory":118,
        "new_known_game_switch_count_excluding_separate_LBX_prescaled_dispatch":118+len(entries),
        "separately_verified_prescaled_LBX_dispatch":hex(0x117190),
        "additional_switches":entries,
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="additional_switches"},indent=2))
