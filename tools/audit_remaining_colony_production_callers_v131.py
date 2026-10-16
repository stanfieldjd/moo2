#!/usr/bin/env python3
"""Source-authenticated static caller audit for v1.31 production (food/research/industry).

Verifies canonical EXE & Watcom CODE identity, full named procedure lengths,
full contiguous decoded x86 byte streams incl. GNU objdump continuation bytes,
all direct branches/calls, original helper body identity, selected code anchors
and bounded independent caller-only arithmetic fixtures.

DOES NOT claim Colony_Job_Production_ internal semantics, full DOS behavior,
a native port, or runtime equivalence.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
HELPERS={
 "Event_Check_Space_Anomaly_":(0x1341E,80,"dd82062b1a3404b5917ee04dceea3459291b8f96f1fda2b0b9ded5e7041932b4"),
 "Colony_Job_Production_":(0xCE280,996,"853acbdf8e5057e9ad4f3a34c7f5aa98392c668eee1568f8133995ca5d641860"),
 "Format_Quotient_":(0xCDA36,158,"3460b3c71f1cc964a63b1583e2020119e091473cd311af582562386b370e8b12"),
 "Colony_Officer_":(0xCD9F2,68,"a573f1396f45fe66f4484dfc1965704989b7a3af6301a75b173c13ec9a98afcc"),
 "Owned_Officer_Level_":(0x84951,86,"c067e6142cc3347a958ff8a7d868a10f4039296419eb9acf5b989f0b7f438586"),
 "sprintf_":(0x1165F2,48,"f46feba187f8dac98b214d9f95e9f7de8d387731802675ace60857d61d0f3b38"),
 "memset_":(0x119C70,24,"e1bb125f736118af8cb392e308cbf68630169cada23d288f5adad0c3eb4fdc8c"),
}
PROCEDURES={
 "Colony_Research_Production_":{
   "offset":0xCFF74,"bytes":1103,
   "sha256":"8d893da4d56dcd193a65a5db6d642ea8b375543797047ed6b149db71fb201341",
   "external_tails":(0xCEB17,0xCEB08),
   "calls":{"Event_Check_Space_Anomaly_":1,"Colony_Job_Production_":1,"sprintf_":22,"Format_Quotient_":8},
   "anchors":{
     0xCFF74:("push","ebx"),0xCFF78:("enter","0x264,0x0"),
     0xCFF80:("cmp","byte ptr [eax+0xa],0x0"),
     0xCFF86:("mov","word ptr [eax+0xeb],0x0"),
     0xCFF8F:("jmp","0xceb17"),0xCFFA3:("call","0x1341e"),
     0xCFFAD:("mov","word ptr [esi+0xeb],0x0"),
     0xCFFB8:("je","0xceb17"),0xCFFCE:("jmp","0xceb17"),
     0xCFFE1:("mov","edx,0x2"),0xCFFE8:("call","0xce280"),
     0xCFFF0:("cmp","byte ptr [esi+0x159],0x0"),
     0xCFFF9:("mov","eax,0x5"),
     0xD0005:("cmp","byte ptr [esi+0x154],0x0"),
     0xD000E:("mov","eax,0xa"),
     0xD001A:("cmp","byte ptr [esi+0x149],0x0"),
     0xD0023:("mov","ecx,0xf"),
     0xD002C:("cmp","byte ptr [esi+0x13c],0x0"),
     0xD0035:("mov","eax,0x1e"),
     0xD0050:("mov","word ptr [esi+0xeb],dx"),
     0xD0057:("test","edi,edi"),
     0xD0059:("je","0xceb17"),0xD03BE:("jmp","0xceb08"),
   },
   "output":"colony WORD+0xEB",
 },
 "Colony_Food_Production_":{
   "offset":0xCE664,"bytes":1209,
   "sha256":"cfd054077a2fa2a0b676a7cda660388de06c3b63a46f8a3f516bc5e245555aac",
   "external_tails":(),
   "calls":{"Event_Check_Space_Anomaly_":1,"Colony_Job_Production_":1,
            "memset_":1,"sprintf_":23,"Format_Quotient_":9},
   "anchors":{
     0xCE664:("push","ebx"),0xCE668:("enter","0x260,0x0"),
     0xCE670:("cmp","byte ptr [eax+0xa],0x0"),
     0xCE676:("mov","word ptr [eax+0xe7],0x0"),
     0xCE693:("call","0x1341e"),
     0xCE69D:("mov","word ptr [esi+0xe7],0x0"),
     0xCE6C9:("cmp","byte ptr [esi+0xdd],0x0"),
     0xCE6DF:("call","0x119c70"),
     0xCE6FA:("call","0xce280"),
     0xCE6FF:("cmp","byte ptr [esi+0x14b],0x0"),
     0xCE708:("mov","dword ptr [ebp-0x8],0x2"),
     0xCE70F:("cmp","byte ptr [esi+0x161],0x0"),
     0xCE718:("mov","dword ptr [ebp-0x4],0x4"),
     0xCE727:("mov","word ptr [esi+0xe7],bx"),
     0xCE72E:("test","edi,edi"),
   },
   "output":"colony WORD+0xE7",
 },
 "Colony_Industry_Production_":{
   "offset":0xCEE1B,"bytes":1789,
   "sha256":"e68780a7e7632b271363fa37540d0428dd0c57c20ac173ac1ccee4ebe9e45f1d",
   "external_tails":(),
   "calls":{"Event_Check_Space_Anomaly_":1,"Colony_Job_Production_":1,
            "Colony_Officer_":1,"Owned_Officer_Level_":2,
            "sprintf_":26,"Format_Quotient_":9},
   "anchors":{
     0xCEE1B:("push","ebx"),0xCEE1F:("enter","0x2f0,0x0"),
     0xCEE23:("sub","ebp,0x82"),
     0xCEE2D:("movzx","ecx,byte ptr [eax+0xa]"),
     0xCEE31:("mov","byte ptr [eax+0xfb],0x0"),
     0xCEE3C:("mov","word ptr [eax+0xe9],0x0"),
     0xCEE59:("call","0x1341e"),
     0xCEE63:("mov","word ptr [esi+0xe9],0x0"),
     0xCEE97:("mov","edx,0x1"),
     0xCEEA5:("call","0xce280"),
     0xCEED7:("cmp","byte ptr [esi+0x142],0x0"),
   },
   "output":"colony WORD+0xE9; BYTE+0xFB is initially zeroed",
 },
}
# Original CODE shared tails verified by upstream analyses, not additional
# in-function instruction sequences.
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
RX_MORE=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s*)+)$",re.I)
def sha(b):return hashlib.sha256(b).hexdigest()
def parse(code_path,start,length):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
        f"--start-address=0x{start:x}",f"--stop-address=0x{start+length:x}",str(code_path)],
        text=True,capture_output=True,check=True)
    entries=[];extra=[];cur=start
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m:
            at=int(m[1],16);raw=bytes.fromhex(m[2].strip())
            if at!=cur:raise ValueError(f"disassembler hole/overlap at CODE {at:#x} expected {cur:#x}")
            entries.append([at,raw,m[3].lower(),m[4].strip().lower()])
            cur+=len(raw);continue
        m=RX_MORE.match(line)
        if m:
            at=int(m[1],16);raw=bytes.fromhex(m[2].strip())
            if not entries or at!=cur:raise ValueError(f"disasm continuation wrong at {at:#x}")
            entries[-1][1]+=raw;cur+=len(raw)
            extra.append({"at":hex(at),"from":hex(entries[-1][0]),"bytes":len(raw)})
    if cur!=start+length:raise ValueError(f"incomplete source decode: {cur:#x} vs {start+length:#x}")
    return entries,extra

def wrapper_research(base, flags):
    """Controlled selected caller path: original WORD+0xEB store from helper."""
    if not 0<=base<=32767 or len(flags)!=4:raise ValueError("synthetic bounds")
    return (base+sum(v for selected,v in zip(flags,(5,10,15,30)) if selected))&0xffff

def wrapper_food(base, enabled_dd, flags):
    """Controlled selected non-anomaly path: optional shared helper + flags."""
    if not 0<=base<=32767 or len(flags)!=2:raise ValueError("synthetic bounds")
    return ((base if enabled_dd else 0)+(2 if flags[0] else 0)+(4 if flags[1] else 0))&0xffff

def fixture_count():
    assert wrapper_research(0,[0,0,0,0])==0
    assert wrapper_research(2,[1,0,0,0])==7
    assert wrapper_research(2,[0,1,0,0])==12
    assert wrapper_research(2,[0,0,1,0])==17
    assert wrapper_research(2,[0,0,0,1])==32
    assert wrapper_research(2,[1,1,1,1])==62
    assert wrapper_food(5,1,[0,0])==5
    assert wrapper_food(5,0,[0,0])==0
    assert wrapper_food(5,1,[1,0])==7
    assert wrapper_food(5,1,[0,1])==9
    assert wrapper_food(5,0,[1,1])==6
    assert wrapper_food(5,1,[1,1])==11
    return 12

def audit(exe_path,code_path):
    exe=exe_path.read_bytes();blob=code_path.read_bytes()
    if sha(exe)!=EXE_SHA or len(blob)!=1410709 or sha(blob)!=CODE_SHA:
        raise ValueError("official EXE or full Watcom LE CODE identity mismatch")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    symbols={(r["name"],r["segment"]):int(r["offset"]) for r in csv.DictReader(
           (ROOT/"decompilation/symbols.csv").open(newline=""))}
    for name,address in (("_colony",0x1AB18),("_player",0x1FF98),
                         ("_planet",0x1B0D4),("_anomaly_msg",0x3231C)):
        if symbols.get((name,"2"))!=address:
            raise ValueError(f"original DATA symbol mismatch: {name}")
    for name,(off,size,digest) in HELPERS.items():
        row=fs[name]
        if (int(row["offset"]),int(row["inferred_size"]))!=(off,size) or sha(blob[off:off+size])!=digest:
            raise ValueError("authenticated original named callee changed: "+name)
    tests=fixture_count()
    audits={}
    valid_helpers={v[0]:name for name,v in HELPERS.items()}
    for name,params in PROCEDURES.items():
        off=params["offset"];size=params["bytes"]
        row=fs[name]
        if (int(row["offset"]),int(row["inferred_size"]))!=(off,size) or sha(blob[off:off+size])!=params["sha256"]:
            raise ValueError("complete source named body differs: "+name)
        ins,extra=parse(code_path,off,size)
        mmap={at:(op,arg) for at,raw,op,arg in ins}
        for at,raw,op,arg in ins:
            if blob[at:at+len(raw)]!=raw:raise ValueError("raw decoded x86 byte mismatch")
        for at,expected in params["anchors"].items():
            if mmap.get(at)!=expected:raise ValueError(f"{name} CODE {at:#x}: got {mmap.get(at)}, expected {expected}")
        transfers=[];called=Counter()
        for at,raw,op,arg in ins:
            if op=="call" or op.startswith("j"):
                if not re.fullmatch(r"0x[0-9a-f]+",arg):
                    raise ValueError(f"{name}: unexpected relative transfer {at:#x} {op} {arg}")
                dest=int(arg,16)
                if op=="call":
                    if dest not in valid_helpers:raise ValueError(f"uncatalogued target {at:#x}->{dest:#x}")
                    called[valid_helpers[dest]]+=1
                elif dest not in mmap and dest not in params["external_tails"]:
                    raise ValueError(f"off-body or mid-instruction branch {at:#x}->{dest:#x}")
                transfers.append({"at":hex(at),"op":op,"dest":hex(dest)})
        if dict(called)!=params["calls"]:
            raise ValueError(f"direct call count differs for {name}: {called}")
        audits[name]={
            "original_complete_body":{"CODE_start":hex(off),"bytes":size,"sha256":params["sha256"]},
            "complete_decoded_instruction_count":len(ins),
            "complete_decoded_bytes":sum(len(x[1]) for x in ins),
            "rejoined_objdump_byte_continuations":extra,
            "original_direct_call_count":sum(called.values()),
            "callee_count_by_name":dict(called),
            "complete_direct_control_transfer_count":len(transfers),
            "complete_direct_control_transfer_inventory":transfers,
            "exact_machine_opcode_anchors":len(params["anchors"]),
            "verified_output_field":params["output"],
            "off_body_shared_return_targets":[hex(t) for t in params["external_tails"]],
        }
    return {"status":"source-verified-static-caller-control-flow",
       "EXE_sha256":EXE_SHA,"CODE_sha256":CODE_SHA,
       "verified_named_helper_source_bodies":[
           {"name":n,"CODE_start":hex(v[0]),"bytes":v[1],"sha256":v[2]}
           for n,v in HELPERS.items()],
       "verified_production_callers":audits,
       "bounded_selected_caller_arithmetic_fixtures":tests,
       "limitations":[
           "No DOS runtime differential test; no proof of full native port",
           "The 996-byte Colony_Job_Production_ callee has only full-body SHA identity in THIS audit; its internal algorithm is not reconstructed here",
           "The food/industry/research caller reports establish complete source instruction and control-flow coverage, NOT complete semantic proofs for all external globals",
           "Existing analysis disassembly files and proprietary executable remain unchanged",
       ]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    value=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(value,indent=2)+"\n")
    print(json.dumps(value,indent=2))
