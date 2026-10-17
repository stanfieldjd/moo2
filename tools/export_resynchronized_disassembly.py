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
# Original x86 direct branch displacements independently verified against
# the official CODE image. These targets are source-proven instruction entries
# inside their own named Watcom function, not inferred new routine entries.
# (source branch instruction, source-encoded branch target)
BRANCH_RESYNC_ANCHORS=[
 (0x10733F,0x107351),(0x10759A,0x1075E1),(0x115442,0x11545F),
 (0x116565,0x116572),(0x11659A,0x1165A7),(0x116E39,0x116E51),
 (0x11A164,0x11A221),(0x11A77F,0x11A791),(0x11B935,0x11B949),
 (0x11CE55,0x11CE73),(0x11D095,0x11D0B3),(0x11D55A,0x11D56F),
 (0x1271E0,0x1271FF),(0x12747D,0x12749F),(0x12774B,0x12776B),
 (0x12E2BE,0x12E2D6),
]
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

def audited_direct_branch_restart_points(code,starts,end_by_start,ranges):
    """Trust only x86 direct branches whose raw displacement encodes target."""
    result={}
    for site,dest in BRANCH_RESYNC_ANCHORS:
        op=code[site]
        if op in (*range(0x70,0x80),0xEB,0xE3):
            instr_len=2;disp=int.from_bytes(code[site+1:site+2],'little',signed=True)
        elif op==0xE9:
            instr_len=5;disp=int.from_bytes(code[site+1:site+5],'little',signed=True)
        elif op==0x0F and 0x80<=code[site+1]<=0x8F:
            instr_len=6;disp=int.from_bytes(code[site+2:site+6],'little',signed=True)
        else:
            raise ValueError(f'Original CODE address is not a supported direct x86 jump: {site:#x}')
        if site+instr_len+disp!=dest:
            raise ValueError(f'Original authenticated direct branch target differs: {site:#x}')
        i=bisect.bisect_right(starts,site)-1
        if i<0 or not (starts[i]<=site<dest<end_by_start[starts[i]]):
            raise ValueError(f'Original jump target not forward inside same named Watcom routine {site:#x}')
        owner=starts[i]
        for lo,hi,_ in ranges:
            if lo<=dest<hi or lo<=site<hi:
                raise ValueError('Verified direct code branch wrongly points into original inline table data')
        result.setdefault(owner,set()).add(dest)
    if sum(map(len,result.values()))!=len(BRANCH_RESYNC_ANCHORS):
        raise ValueError('Duplicate original branch restart sites')
    return result

def generate():
    code,starts,end_by_start,owned,ranges=audited_segments()
    branches=audited_direct_branch_restart_points(code,starts,end_by_start,ranges)
    parts=[]
    failures=[]
    parsed_spans=0
    skipped=0
    for start in starts:
        end=end_by_start[start]
        # Segment known code at original authenticated direct-branch targets,
        # as well as the start and end of each source-proven inline table.
        # A branch into the middle of a previously linear byte stream must
        # restart decoding there instead of using an accidental alignment.
        tables=sorted(owned.get(start,[]))
        cuts={start,end,*branches.get(start,set())}
        for lo,hi,site in tables:
            cuts.add(lo);cuts.add(hi)
            skipped+=hi-lo
        ordered=sorted(cuts)
        intervals=[]
        for left,right in zip(ordered,ordered[1:]):
            if any(lo<=left and right<=hi for lo,hi,_ in tables):continue
            if left<right:intervals.append((left,right))
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
      "source_authenticated_direct_branch_restarts":len(BRANCH_RESYNC_ANCHORS),
      "source_authenticated_branch_function_spans":len(branches),
      "failed_segments":len(failures),
      "method":"Original Watcom v1.31 CODE-bytes-checked segmentation: authoritative function entries, original-byte-verified inline switch table data exclusions, and source-decoded direct-branch targets. No inferred machine branches or guesswork."}
    MAN.write_text(json.dumps(result,indent=2)+"\n")
    print(MAN.read_text(),end="")

if __name__=="__main__":generate()
