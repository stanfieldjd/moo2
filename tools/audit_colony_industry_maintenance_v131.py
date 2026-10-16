#!/usr/bin/env python3
"""Verify v1.31 Colony_Industry_Maintenance_ and reconstruct its dispatch.

Static original-machine-code evidence only. Controlled fixtures are not
original DOS runtime execution or validated in-game state ranges.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
ENTRY=0xCF546
SIZE=297
BODY_SHA="a3d24386fbaa9dfe229d88dcb34c2c661f3dc2169cdec44481c558542e0fb0ed"
EVENT=0x1341E
EVENT_SHA="dd82062b1a3404b5917ee04dceea3459291b8f96f1fda2b0b9ded5e7041932b4"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
    0xCF546:("push","ebx"), 0xCF54B:("enter","0x8,0x0"),
    0xCF551:("movsx","ax,byte ptr [eax]"),
    0xCF55A:("sub","eax,dword ptr ds:0x1ab18"),
    0xCF560:("mov","esi,0x169"), 0xCF566:("idiv","esi"),
    0xCF568:("cwde",""), 0xCF569:("call","0x1341e"),
    0xCF571:("je","0xcf57f"),
    0xCF573:("mov","byte ptr [ecx+0xf0],0x0"),
    0xCF57A:("jmp","0xd1f97"),
    0xCF57F:("mov","ebx,0x8"),
    0xCF584:("lea","eax,[ecx+0x10c]"),
    0xCF58A:("xor","edx,edx"),0xCF58C:("call","0x119c70"),
    0xCF591:("mov","byte ptr [ecx+0x100],0x0"),
    0xCF598:("mov","byte ptr [ecx+0x101],0x0"),
    0xCF59F:("mov","byte ptr [ecx+0x103],0x0"),
    0xCF5A6:("lea","edi,[ecx+0xc]"),
    0xCF5A9:("mov","byte ptr [ecx+0x102],0x0"),
    0xCF5BA:("mov","edx,dword ptr [edi+eax*4]"),
    0xCF5BD:("mov","eax,dword ptr [edi+eax*4]"),
    0xCF5C0:("shl","eax,0x15"),
    0xCF5C3:("shr","eax,0x1f"),
    0xCF5C6:("and","edx,0xf"),
    0xCF5CC:("cmp","dx,0x8"),
    0xCF5D5:("imul","eax,eax,0xea9"),
    0xCF5DB:("mov","esi,dword ptr ds:0x1ff98"),
    0xCF5E1:("cmp","byte ptr [esi+eax*1+0x8b0],0x0"),
    0xCF5E9:("setne","al"),
    0xCF5F0:("cmp","dx,word ptr [ebp-0x8]"),
    0xCF5F6:("add","byte ptr [ecx+0x100],al"),
    0xCF5FE:("cmp","word ptr [ebp-0x4],0x0"),
    0xCF605:("add","byte ptr [ecx+0x103],al"),
    0xCF60D:("add","byte ptr [ecx+0x102],al"),
    0xCF616:("add","byte ptr [ecx+edx*1+0x10c],al"),
    0xCF61F:("jne","0xcf62c"),
    0xCF621:("mov","eax,0x2"),
    0xCF626:("add","byte ptr [ecx+0x101],al"),
    0xCF62C:("inc","ebx"),
    0xCF62D:("movzx","ax,byte ptr [ecx+0xa]"),
    0xCF635:("jl","0xcf5b7"),
    0xCF637:("movzx","dx,byte ptr [ecx+0x100]"),
    0xCF63F:("movzx","ax,byte ptr [ecx+0x101]"),
    0xCF649:("movzx","ax,byte ptr [ecx+0x103]"),
    0xCF653:("movzx","ax,byte ptr [ecx+0x102]"),
    0xCF65D:("cwde",""),0xCF65E:("inc","eax"),
    0xCF65F:("cdq",""),0xCF660:("sub","eax,edx"),
    0xCF662:("sar","eax,1"),
    0xCF664:("mov","byte ptr [ecx+0xf0],al"),
    0xCF66A:("jmp","0xd1f97"),
    0xD1F97:("leave",""),0xD1F9D:("ret",""),
}
def sha(b):
    return hashlib.sha256(b).hexdigest()

def check_opcode(path,offset):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
       f"--start-address=0x{offset:x}",f"--stop-address=0x{offset+16:x}",str(path)],
       text=True,capture_output=True,check=True)
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==offset:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"instruction absent at {offset:#x}")

def word_ceil_half(raw_count):
    """Unsigned non-overflowing fixture input; source uses signed register operations."""
    return ((raw_count+1)//2)&0xff

def controlled_counts(entries,owner,player_flags):
    """Model of the non-anomaly path for controlled, valid synthetic entries."""
    if len(player_flags)!=8:raise ValueError("8 player flag entries required")
    counters=[0,0,0,0]  # +0x100,+0x101,+0x102,+0x103
    per_owner=[0]*8      # colony +0x10c..+0x113
    for raw in entries:
        tag=raw&0xf
        bit_10=(raw>>10)&1
        if tag<8:
            value=int(player_flags[tag]!=0)
            if tag==owner: slot=0
            elif bit_10: slot=3
            else: slot=2
            counters[slot]=(counters[slot]+value)&0xff
            per_owner[tag]=(per_owner[tag]+value)&0xff
        elif tag==8:
            counters[1]=(counters[1]+2)&0xff
    return counters,per_owner,word_ceil_half(sum(counters))

def audit(exe,code):
    raw=exe.read_bytes();body=code.read_bytes()
    if sha(raw)!=EXE_SHA or sha(body)!=CODE_SHA or len(body)!=1410709:
        raise ValueError("original EXE/LE CODE identity mismatch")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open())}
    for name,off,size,digest in (
        ("Colony_Industry_Maintenance_",ENTRY,SIZE,BODY_SHA),
        ("Event_Check_Space_Anomaly_",EVENT,80,EVENT_SHA),
    ):
        r=fs[name]
        if (int(r["offset"]),int(r["inferred_size"]))!=(off,size):
            raise ValueError("source named extent changed for "+name)
        if sha(body[off:off+size])!=digest:
            raise ValueError("entire original function changed for "+name)
    syms={(r["name"],r["segment"]):int(r["offset"])
           for r in csv.DictReader((ROOT/"decompilation/symbols.csv").open())}
    for key,off in {( "_colony","2"):0x1AB18,("_player","2"):0x1FF98}.items():
        if syms.get(key)!=off:raise ValueError("original global identity changed "+str(key))
    for offset,expected in OPS.items():
        actual=check_opcode(code,offset)
        if actual!=expected:raise ValueError(f"original {offset:#x} {actual} != {expected}")
    assert controlled_counts([],0,[1]*8)==([0,0,0,0],[0]*8,0)
    assert controlled_counts([0],0,[1]*8)==([1,0,0,0],[1,0,0,0,0,0,0,0],1)
    assert controlled_counts([1],0,[1]*8)[0]==[0,0,1,0]
    assert controlled_counts([1|(1<<10)],0,[1]*8)[0]==[0,0,0,1]
    assert controlled_counts([8],0,[0]*8)[0]==[0,2,0,0]
    assert controlled_counts([9],0,[1]*8)[0]==[0,0,0,0]
    assert controlled_counts([0,1,8,8],0,[1]*8)[2]==3
    return {
      "status":"source-verified-static-reconstruction",
      "EXE_sha256":EXE_SHA,"LE_CODE_sha256":CODE_SHA,
      "named_complete_bodies":[{"name":"Colony_Industry_Maintenance_","offset":hex(ENTRY),
            "size":SIZE,"sha256":BODY_SHA},
          {"name":"Event_Check_Space_Anomaly_","offset":hex(EVENT),
            "size":80,"sha256":EVENT_SHA}],
      "verified_instruction_checkpoints":len(OPS),
      "tested_synthetic_fixtures":7,
      "observed_exception":"nonzero Event_Check_Space_Anomaly_ zeroes colony BYTE+0xf0 and jumps directly to shared return (other counters not reset on this branch)",
      "observed_non_exception":"clear 8 per-owner bytes and four category bytes; inspect colony +0x0c 4-byte entries up to unsigned count BYTE+0x0a; classify low nibble and bit 10; use player[low nibble].BYTE+0x8b0 flag for ids 0..7; id 8 always counts +2",
      "observed_output":"add four category BYTE counters, signed Watcom ceil-half for nonnegative totals; store low 8 bits to BYTE+0xf0",
      "shared_epilogue":"branch to CODE 0xd1f97, leave/pop edi/esi/edx/ecx/ebx/ret",
      "limitations":["No original DOS differential execution","No verified in-game array length limit","No semantic interpretation established for player BYTE+0x8b0 or each category beyond machine-observed effects"]
    }
if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe",required=True,type=Path)
    parser.add_argument("--code",required=True,type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    out=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
