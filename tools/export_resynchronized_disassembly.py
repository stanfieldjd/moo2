#!/usr/bin/env python3
"""Regenerate original v1.31 Watcom CODE disassembly at verified boundaries.

Every known original CODE function starts a fresh x86 disassembly. Additional
source-authenticated in-CODE switch tables are *data*, not instructions:
split their containing function spans at exact verified table boundaries,
and restart disassembly at the first byte after each table. Never invent
case targets, instruction bytes or boundaries not proven by original CODE.
"""
import bisect
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"decompilation"
BIN=D/"code_object_1.bin"
FUN=D/"functions.csv"
OUT=D/"code_object_1_resynced.disasm"
MAN=D/"resynced_disassembly.json"
SOURCE=D/"switch_targets_reconciled.json"
ROWS=D/"switch_targets_reconciled.csv"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"

def audited_segments():
    code=BIN.read_bytes()
    if len(code)!=1410709 or hashlib.sha256(code).hexdigest()!=CODE_SHA:
        raise ValueError("Canonical original Watcom v1.31 CODE image mismatch")
    if not SOURCE.is_file() or not ROWS.is_file():
        raise ValueError("Cannot safely skip tables without proven original source inventory")
    proof=json.loads(SOURCE.read_text())
    if (proof.get("original_CODE_SHA256"),proof.get("original_EXE_SHA256"),
        proof.get("merged_site_count"),proof.get("verified_original_case_entries"))!=(
        CODE_SHA,EXE_SHA,205,1625):
        raise ValueError("Original source-verified switch table manifest changed")

    cases={}
    with ROWS.open(newline="") as f:
        for r in csv.DictReader(f):
            site=int(r["site_hex"],16)
            idx=int(r["case_index"])
            case=int(r["target_offset"])
            if int(r["target_hex"],16)!=case or idx in cases.setdefault(site,{}):
                raise ValueError("Original Watcom switch case index/target differs")
            cases[site][idx]=case
    if len(cases)!=205 or sum(map(len,cases.values()))!=1625:
        raise ValueError("Original source switch CSV incomplete")
    starts=sorted({int(r["offset"]) for r in csv.DictReader(FUN.open(newline=""))})
    end_by_start={start: starts[i+1] if i+1<len(starts) else len(code)
                  for i,start in enumerate(starts)}
    owned={}
    ranges=[]
    for meta in proof["site_provenance"]:
        site=int(meta["site_offset"],16)
        table=int(meta["table_offset"],16)
        count=int(meta["case_count"])
        finish=table+4*count
        i=bisect.bisect_right(starts,table)-1
        if i<0:raise ValueError("Verified original switch table precedes named CODE entry")
        owner=starts[i]
        if not owner<=table<finish<=end_by_start[owner]:
            raise ValueError("Source-original inline table extends beyond its function interval")
        if not 0<=site<len(code):raise ValueError("Original switch instruction out of CODE")
        if set(cases[site])!=set(range(count)):
            raise ValueError("Missing original indexed Watcom switch target")
        for idx in range(count):
            ptr=table+4*idx
            value=int.from_bytes(code[ptr:ptr+4],"little")
            if value!=cases[site][idx] or not 0<=value<len(code):
                raise ValueError("Original source CODE switch bytes or destination changed")
        owned.setdefault(owner,[]).append((table,finish,site))
        ranges.append((table,finish,site))
    if len(ranges)!=205:raise ValueError("Source-verified table count changed")
    ranges.sort()
    for prev,next_ in zip(ranges,ranges[1:]):
        if prev[1]>next_[0]:
            raise ValueError("Ambiguous overlapping original Watcom CODE switch tables")
    return code,starts,end_by_start,owned,ranges

def generate():
    code,starts,end_by_start,owned,ranges=audited_segments()
    parts=[]
    failures=[]
    parsed_spans=0
    skipped=0
    for start in starts:
        end=end_by_start[start]
        cursor=start
        intervals=[]
        for lo,hi,site in sorted(owned.get(start,[])):
            if cursor<lo:intervals.append((cursor,lo))
            skipped+=hi-lo
            cursor=hi
        if cursor<end:intervals.append((cursor,end))
        for left,right in intervals:
            p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
                 f"--start-address={left}",f"--stop-address={right}",str(BIN)],
                 text=True,capture_output=True)
            if p.returncode:
                failures.append([hex(left),hex(right),p.stderr[:200]])
                continue
            lines=[line for line in p.stdout.splitlines()
                   if line.lstrip().startswith(tuple("0123456789abcdefABCDEF")) and ":" in line]
            parts.append(f";; SOURCE_CODE_SEGMENT 0x{left:x} END 0x{right:x}\n"+"\n".join(lines)+"\n")
            parsed_spans+=1
    if failures:raise RuntimeError(f"Failed to disassemble source-validated CODE spans: {failures[:5]}")
    OUT.write_text("\n".join(parts))
    result={
      "source_original_CODE_SHA256":CODE_SHA,
      "unique_CODE_symbol_entries":len(starts),
      "independent_disassembly_segments":parsed_spans,
      "source_verified_switch_tables_skipped":len(ranges),
      "source_verified_switch_case_targets":1625,
      "source_verified_table_data_bytes_not_disassembled":skipped,
      "failed_segments":len(failures),
      "method":"Original Watcom v1.31 CODE-bytes-checked nested segmentation: authoritative function entries plus original-byte-verified inline switch table boundaries. Data intervals omitted, code disassembly restarted after every verified table."}
    MAN.write_text(json.dumps(result,indent=2)+"\n")
    print(MAN.read_text(),end="")

if __name__=="__main__":generate()
