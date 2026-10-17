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
DATA_BIN=D/"data_object_2_initialized.bin"
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
 (0xFFF18,0xFFF90),
]
# Original Watcom startup CODE begins with JMP short +0x76 over its own
# 118-byte embedded vendor/copyright/metadata literal. The entire interval
# is source-authenticated and deliberately non-executed on entry. Excluding
# it is narrower than suppressing arbitrary ASCII or unresolved CODE bytes.
# (first source data address, first actual code address, complete data SHA256)
AUTHENTICATED_INLINE_LITERAL=[
 (0xFFF1A,0xFFF90,"5e20cacba0c278bbb54d1bb3e3c7d8f7a53fce416d3be31fe83a73b4210b5572"),
]

def audited_literal_spans(code,starts,end_by_start,tables,branches):
    result={}
    for lo,hi,expected_hash in AUTHENTICATED_INLINE_LITERAL:
        if (hi-lo)!=118 or hashlib.sha256(code[lo:hi]).hexdigest()!=expected_hash:
            raise ValueError('Watcom original 118-byte startup identification record mismatch')
        if (code[lo:lo+7]!=b'WATCOM ' or
            b'Run-Time system.' not in code[lo:hi] or
            code[hi-4:hi]!=b'con\x00' or
            code[hi:hi+4]!=bytes.fromhex('fb83e4fc')):
            raise ValueError('Watcom startup vendor record contents/source code marker changed')
        jmp=lo-2
        if code[jmp:lo]!=bytes.fromhex('eb76') or jmp+2+0x76!=hi:
            raise ValueError('Original Watcom JMP does not skip identified inline startup record')
        owners=[x for x in starts if x<=jmp<end_by_start[x]]
        if len(owners)!=1 or jmp!=owners[0] or hi not in branches.get(jmp,set()):
            raise ValueError('Authenticated CODE restart is not the original owner source entry')
        for t0,t1,_ in tables:
            if lo<t1 and t0<hi:
                raise ValueError('Original source startup record overlaps independent switch-table data')
        result.setdefault(jmp,[]).append((lo,hi,'Watcom startup header (non-executed on original entry)'))
    return result

CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
ORIGINAL_DATA_SHA="082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b"


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

def audited_initialized_callback_restarts(code,starts,end_by_start):
    """Re-authenticate Watcom's 3rd six-byte init record and CALL EAX loop."""
    if not DATA_BIN.exists():
        raise ValueError('Original v1.31 initialized DATA object required: decompilation/data_object_2_initialized.bin')
    data=DATA_BIN.read_bytes()
    if len(data)!=81920 or hashlib.sha256(data).hexdigest()!=ORIGINAL_DATA_SHA:
        raise ValueError('Original v1.31 Watcom LE initialized DATA fingerprint changed')
    # Third 6-byte initializer record: state=0, priority=0x20, pointer
    # unrelocated CODE offset 0x12F1D8. This pointer is a real runnable
    # initializer, not a guessed synthetic Watcom named function.
    record=0x12FF2;target=0x12F1D8
    if data[record:record+6]!=bytes.fromhex('0020d8f11200'):
        raise ValueError('Original DOS Watcom initializers no longer point at exact helper')
    if code[0x12EF6C:0x12EFB7].hex()!='565753520689c23ebee62f01003ebf1030010089fb88d039fe7314803e02740a384601770589f38a460183c606ebe839fb74128b430209c074061e0752ffd05ac60302ebc2075a5b5f5ec3':
        raise ValueError('Original Watcom __InitRtns full source machine-code dispatcher changed')
    for addr,expected in {
      0x12EF73:'3ebee62f0100',  # Original initialized DATA loop start 0x12FE6
      0x12EF79:'3ebf10300100',  # Original initialized DATA loop end 0x13010
      0x12EF96:'83c606',        # Original 6-byte table stride
      0x12EF9F:'8b4302',        # Original DWORD callback fetch from [EBX+2]
      0x12EFA9:'ffd0',          # Source CALL EAX indirect initializer
    }.items():
        raw=bytes.fromhex(expected)
        if code[addr:addr+len(raw)]!=raw:
            raise ValueError(f'Original Watcom initializer dispatcher anchor failed {addr:#x}')
    if code[target:target+8]!=bytes.fromhex('668c1534ca0000c3'):
        raise ValueError('Original eight-byte initializer 32-bit CODE body changed')
    # This source target sits inside the named _SplitParms_ provisional
    # interval, which contains its own original 32-bit code and padding.
    i=bisect.bisect_right(starts,target)-1
    owner=starts[i]
    if not (owner<=target and target+8<=end_by_start[owner]):
        raise ValueError('Original initializer target outside its CODE symbol interval')
    if owner!=0x12F0C8 or end_by_start[owner]!=0x12F1E0:
        raise ValueError('Watcom CODE function index changed near initializer callback')
    table_rows=list(csv.DictReader((D/'runtime_init_targets.csv').open(newline='')))
    matching=[r for r in table_rows if r['function']=='__InitRtns' and r['record_index']=='2']
    if len(matching)!=1 or matching[0]['target_hex']!='0x12f1d8' or matching[0]['record_hex']!='0x12ff2':
        raise ValueError('Existing original Watcom initializer inventory disagrees')
    return {owner:{target}}

def generate():
    code,starts,end_by_start,owned,ranges=audited_segments()
    initialization=audited_initialized_callback_restarts(code,starts,end_by_start)
    branches=audited_direct_branch_restart_points(code,starts,end_by_start,ranges)
    literal_spans=audited_literal_spans(code,starts,end_by_start,ranges,branches)
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
        literals=literal_spans.get(start,[])
        cuts={start,end,*branches.get(start,set()),*initialization.get(start,set())}
        for lo,hi,label in literals:
            cuts.add(lo);cuts.add(hi)
        for lo,hi,site in tables:
            cuts.add(lo);cuts.add(hi)
            skipped+=hi-lo
        ordered=sorted(cuts)
        intervals=[]
        for left,right in zip(ordered,ordered[1:]):
            if any(lo<=left and right<=hi for lo,hi,_ in tables):continue
            if any(lo<=left and right<=hi for lo,hi,_ in literals):continue
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
      "source_authenticated_initializer_callback_restarts":sum(map(len,initialization.values())),
      "source_authenticated_initializer_callback_CODE":"0x12f1d8",
      "source_original_initialized_DATA_SHA256":ORIGINAL_DATA_SHA,
      "source_authenticated_embedded_literal_spans":len(AUTHENTICATED_INLINE_LITERAL),
      "source_authenticated_embedded_literal_bytes":sum(hi-lo for lo,hi,_ in AUTHENTICATED_INLINE_LITERAL),
      "failed_segments":len(failures),
      "method":"Original Watcom v1.31 CODE-bytes-checked segmentation: authoritative function entries, original-byte-verified inline switch table data exclusions, and source-decoded direct-branch targets. No inferred machine branches or guesswork."}
    MAN.write_text(json.dumps(result,indent=2)+"\n")
    print(MAN.read_text(),end="")

if __name__=="__main__":generate()
