#!/usr/bin/env python3
"""v1.31 Colony_BC_Production_ complete-byte/control-flow static audit.

Handles disassembler byte continuation lines (up to 9-byte x86 opcodes).
Verifies original named callee bytes and direct control-flow targets, and
performs controlled bounded arithmetic fixtures. NOT a DOS differential test.
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
MAIN=("Colony_BC_Production_",0xD03F1,1239,"4ea7459e0e93d44fa342b14b568351a51a2ff317c3291cc98500da0639edc4ac")
CALLEES=[
("Event_Check_Space_Anomaly_",0x1341E,80,"dd82062b1a3404b5917ee04dceea3459291b8f96f1fda2b0b9ded5e7041932b4"),
("Colony_Officer_",0xCD9F2,68,"a573f1396f45fe66f4484dfc1965704989b7a3af6301a75b173c13ec9a98afcc"),
("Owned_Officer_Level_",0x84951,86,"c067e6142cc3347a958ff8a7d868a10f4039296419eb9acf5b989f0b7f438586"),
("sprintf_",0x1165F2,48,"f46feba187f8dac98b214d9f95e9f7de8d387731802675ace60857d61d0f3b38")]
TABLE_OFFSET=0xCD4E6
TABLE_BYTES=bytes([0,0,1,2,3,25,25,25])
TABLE_SHA="59f534fc4d2ed728a8bd38cf136dea4a78ac39176d0d941ef82ef3d2be8450e8"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
RX_CONT=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s*)+)$",re.I)
TAILS={0xCEB17,0xCEB08}
ANCHORS={
 0xD03F1:("push","ebx"),
 0xD03F5:("enter","0x40,0x0"),
 0xD03FD:("cmp","byte ptr [eax+0xa],0x0"),
 0xD0403:("mov","word ptr [eax+0xed],0x0"),
 0xD040C:("jmp","0xceb17"),
 0xD0411:("sub","eax,dword ptr ds:0x1ab18"),
 0xD041D:("idiv","ebx"),
 0xD0420:("call","0x1341e"),
 0xD0428:("je","0xd0450"),
 0xD042A:("mov","word ptr [esi+0xed],0x0"),
 0xD0435:("je","0xceb17"),
 0xD043B:("mov","esi,dword ptr ds:0x3231c"),
 0xD0442:("lods","al,byte ptr ds:[esi]"),
 0xD0443:("mov","byte ptr [edi],al"),
 0xD0448:("jne","0xd0442"),
 0xD044B:("jmp","0xceb17"),
 0xD0450:("movsx","eax,byte ptr [esi]"),
 0xD0453:("imul","eax,eax,0xea9"),
 0xD0459:("mov","ebx,dword ptr ds:0x1ff98"),
 0xD0468:("call","0xcd9f2"),
 0xD0470:("movsx","eax,byte ptr [ebx+0x8a4]"),
 0xD047A:("add","eax,eax"),
 0xD047F:("add","eax,0x4"),
 0xD0488:("movzx","eax,byte ptr [esi+0xa]"),
 0xD04B4:("sub","dword ptr [ebp-0x24],0x4"),
 0xD04BB:("mov","eax,dword ptr [eax]"),
 0xD04BD:("and","eax,0xf"),
 0xD04C0:("cmp","eax,0x8"),
 0xD04CD:("cmp","byte ptr [eax+0x8b6],0x0"),
 0xD04DE:("mov","eax,dword ptr [ebp-0x34]"),
 0xD04E4:("jb","0xd04b4"),
 0xD0503:("cmp","byte ptr [eax+0x28],0x64"),
 0xD0510:("movzx","eax,byte ptr [eax+0xcd4e6]"),
 0xD051D:("imul","eax,dword ptr [ebp-0x30]"),
 0xD0521:("inc","eax"),
 0xD0522:("inc","eax"),
 0xD0529:("sar","eax,0x2"),
 0xD052F:("cmp","dword ptr [ebp-0x3c],0x0"),
 0xD0562:("cmp","eax,0x3"),
 0xD0567:("movsx","eax,byte ptr [esi+0x7]"),
 0xD057C:("idiv","ecx"),
 0xD0593:("movsx","eax,word ptr [esi+0x2]"),
 0xD05A2:("mov","al,byte ptr [eax+0xf]"),
 0xD05B1:("mov","dword ptr [ebp-0x4],0x5"),
 0xD05BA:("mov","dword ptr [ebp-0x4],0xa"),
 0xD05C3:("mov","dword ptr [ebp-0x4],0x0"),
 0xD05D1:("cmp","ax,0xffdb"),
 0xD05F2:("movzx","eax,byte ptr [esi+0xf0]"),
 0xD0601:("cmp","byte ptr [ebx+0x8b7],0x0"),
 0xD0613:("sub","eax,edx"),
 0xD0615:("sar","eax,1"),
 0xD0634:("cmp","byte ptr [eax+0x162],0x3"),
 0xD0647:("cmp","byte ptr [esi+0x153],0x0"),
 0xD0653:("cmp","byte ptr [esi+0x15d],0x0"),
 0xD0677:("mov","al,byte ptr [eax+0x89f]"),
 0xD06A1:("cmp","dword ptr [ebp-0x1c],0xffffffff"),
 0xD06B3:("test","byte ptr [eax+0x2a],0x20"),
 0xD06BC:("call","0x84951"),
 0xD06D3:("test","byte ptr [eax+0x2a],0x10"),
 0xD06DC:("call","0x84951"),
 0xD06EE:("cdq", ""),
 0xD06EF:("idiv","ebx"),
 0xD06F4:("mov","eax,dword ptr [ebp-0x40]"),
 0xD070E:("add","ax,word ptr [esi+0x127]"),
 0xD0717:("mov","word ptr [esi+0xed],dx"),
 0xD071E:("test","edi,edi"),
 0xD0720:("je","0xceb17"),
 0xD0731:("call","0x1165f2"),
 0xD08AC:("call","0x1165f2"),
 0xD08BC:("movsx","eax,word ptr [esi+0xed]"),
 0xD08C3:("jmp","0xceb08"),
}
def sha(b):return hashlib.sha256(b).hexdigest()

def parse(code_path,start,length):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
       f"--start-address=0x{start:x}",f"--stop-address=0x{start+length:x}",str(code_path)],
       capture_output=True,text=True,check=True)
    entries=[];next_addr=start;extra_lines=[]
    for raw_line in p.stdout.splitlines():
        m=RX.match(raw_line)
        if m:
            address=int(m[1],16)
            bs=bytes.fromhex(m[2].strip())
            if address!=next_addr:
                raise ValueError(f"Source instruction discontiguous at {address:#x}, expected {next_addr:#x}")
            entries.append([address,bs,m[3].lower(),m[4].strip().lower()])
            next_addr+=len(bs)
            continue
        m=RX_CONT.match(raw_line)
        if m:
            address=int(m[1],16)
            bs=bytes.fromhex(m[2].strip())
            if not entries or next_addr!=address:
                raise ValueError(f"Unattached source opcode continuation {address:#x}")
            entries[-1][1]+=bs
            next_addr+=len(bs)
            extra_lines.append({"address":hex(address),"continuation_bytes":len(bs),
                                "op_start":hex(entries[-1][0])})
    if next_addr!=start+length:
        raise ValueError(f"Decoded range incomplete {next_addr:#x} != {start+length:#x}")
    return entries,extra_lines

def controlled_population_split(entries,player_flag_8b6):
    """Full source-anchored reverse-loop tag/count split, bounded synthetic data."""
    if len(player_flag_8b6)!=8 or len(entries)>255:
        raise ValueError("bad synthetic input")
    active=inactive=0
    for entry in reversed(entries):
        tag=entry&15
        if tag>=8:continue
        if player_flag_8b6[tag]:active+=1
        else:inactive+=1
    return {"flag_nonzero":active,"flag_zero":inactive,"total":active+inactive}

def controlled_positive_quarter_round(n,base):
    """EAX=n*base+2; CDQ; SHL EDX,2; SBB EAX,EDX; SAR EAX,2 for positive fixtures."""
    if not 0<=n<=255 or not 0<=base<=1000 or n*base+2 >= (1<<31):
        raise ValueError("out of supported positive fixture domain")
    return (n*base+2)//4

def fixture_count():
    flags=[0,1,0,1,0,1,0,1]
    cases=[
      ([],(0,0,0)),
      ([0],(0,1,1)),
      ([1],(1,0,1)),
      ([0,1,8,9,10,15],(1,1,2)),
      ([0,0,3,3],(2,2,4)),
      ([0x410,0x401],(1,1,2)), # low nibble 0 and 1; bit10 ignored here
    ]
    for entries,expected in cases:
        out=controlled_population_split(entries,flags)
        assert (out["flag_nonzero"],out["flag_zero"],out["total"])==expected,(entries,out)
    for n,base,expected in [(0,4,0),(1,4,1),(1,2,1),(1,1,0),(3,4,3),(3,7,5)]:
        assert controlled_positive_quarter_round(n,base)==expected
    return len(cases)+6

def audit(exe,code):
    game,blob=exe.read_bytes(),code.read_bytes()
    if sha(game)!=EXE_SHA or len(blob)!=1410709 or sha(blob)!=CODE_SHA:
        raise ValueError("Canonical DOS EXE or Watcom LE CODE image differs")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    bodies=[]
    for name,start,length,expected in [MAIN,*CALLEES]:
        r=fs[name]
        if (int(r["offset"]),int(r["inferred_size"]))!=(start,length):
            raise ValueError(f"Original named-body extent mismatch {name}")
        if sha(blob[start:start+length])!=expected:
            raise ValueError(f"Full original named-body hash mismatch {name}")
        bodies.append({"name":name,"offset":hex(start),"bytes":length,"sha256":expected})
    syms={(r["name"],r["segment"]):int(r["offset"])
          for r in csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    for key,offset in {
      ("_colony","2"):0x1AB18,("_player","2"):0x1FF98,
      ("_planet","2"):0x1B0D4,("_leaders","2"):0x1B0DC,
      ("_anomaly_msg","2"):0x3231C
    }.items():
        if syms.get(key)!=offset:raise ValueError(f"Watcom DATA global mismatch: {key}")
    if blob[TABLE_OFFSET:TABLE_OFFSET+len(TABLE_BYTES)]!=TABLE_BYTES or sha(TABLE_BYTES)!=TABLE_SHA:
        raise ValueError("Original CODE table at 0xcd4e6 differs")
    start,length=MAIN[1:3]
    entries,split=parse(code,start,length)
    ipmap={a:(op,arg) for a,raw,op,arg in entries}
    for at,raw,op,arg in entries:
        if blob[at:at+len(raw)]!=raw:raise ValueError("Decoded body raw bytes mismatch "+hex(at))
    for at,expected in ANCHORS.items():
        if ipmap.get(at)!=expected:
            raise ValueError(f"Opcode anchor mismatch {at:#x}: {ipmap.get(at)} != {expected}")
    transfers=[];calls={}
    for at,raw,op,arg in entries:
        if op=="call" or op.startswith("j"):
            if not re.fullmatch(r"0x[0-9a-f]+",arg):
                raise ValueError("Unresolved relative transfer at "+hex(at))
            target=int(arg,16)
            if op=="call":
                calls.setdefault(target,[]).append(at)
                if target not in {name[1] for name in CALLEES}:
                    raise ValueError("Unexpected callee at "+hex(at))
            elif target not in ipmap and target not in TAILS:
                raise ValueError("Direct jump targets non-entry / unknown "+hex(at)+"->"+hex(target))
            transfers.append({"instruction":hex(at),"operation":op,"target":hex(target)})
    expected_call_counts={0x1341E:1,0xCD9F2:1,0x84951:2,0x1165F2:14}
    if {k:len(v) for k,v in calls.items()}!=expected_call_counts:
        raise ValueError("Original call inventory changed")
    n=fixture_count()
    return {
      "status":"source-verified-static-control-flow-and-selected-production-paths",
      "original_game_SHA256":EXE_SHA,"LE_CODE_SHA256":CODE_SHA,
      "full_named_bodies":bodies,"complete_decoded_body_bytes":length,
      "decoded_instruction_count":len(entries),
      "objdump_continuation_lines_reconstructed":split,
      "verified_opcode_anchors":len(ANCHORS),
      "direct_transfer_inventory":transfers,
      "named_direct_callees":[{"name":name,"target":hex(at),
                         "calls":[hex(x) for x in calls[at]]} for name,at,_,_ in CALLEES],
      "authenticated_CODE_indexed_table":{"offset":hex(TABLE_OFFSET),
                                    "bytes":list(TABLE_BYTES),"sha256":TABLE_SHA},
      "controlled_synthetic_fixtures":n,
      "source_observations":[
        "BYTE+0x0a ==0 -> store 0 at colony WORD+0xed and return through shared tail",
        "nonzero Event_Check_Space_Anomaly_ -> store 0 at colony WORD+0xed; optional EDI text gets _anomaly_msg",
        "original owner-player BYTE+0x8a4 doubled plus 4 contributes to base",
        "reverse packed colony entries low nibble <8; look up player BYTE+0x8b6 to split two counts",
        "positive-domain raw base count product uses +2 and signed quarter arithmetic",
        "government-group==3 bypasses BYTE+0x07 morale correction",
        "colony WORD+0x127 added before final WORD+0xed production write at CODE 0xd0717",
        "optional breakdown formatting after WORD+0xed write, with shared return at 0xceb17 and final shared formatter at 0xceb08",
      ],
      "limits":[
        "No DOS dynamic differential execution",
        "All source-wide numeric/signed domain and production modifier semantics not established",
        "Controlled fixtures demonstrate selected paths, not full native gameplay equivalence",
      ],
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
