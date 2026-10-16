#!/usr/bin/env python3
"""Source-verified v1.31 colony per-population function-table dispatch.

Audits separate Watcom LE CODE/DATA address spaces, the 3-entry original DATA
dispatch, all three target named full bodies & direct CFGs, source call sites,
and signed low-WORD fallback of Colony_Pop_Base_Prod_Produced_. Also verifies
the gravity factor's bounded original two-flag branch table.

Static analysis only: original DOS execution and full modifier semantics remain
unverified, especially for out-of-range original player/planet indexes.
"""
import argparse
import csv
import json
import re
import struct
from collections import Counter
from pathlib import Path
from audit_remaining_colony_production_callers_v131 import ROOT, EXE_SHA, CODE_SHA, parse, sha

DATA_SHA="082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b"
DISPATCH_OFFSET=0xB55C
DISPATCH_SHA="75647e47f704410f38e1a68dfcfee8d47d9af95c90669291aa441d597244b1b9"
BASE=("Colony_Pop_Base_Prod_Produced_",0xCE22C,84,
      "964117fde615677bbecb22bd682edf239015961f1ef758b03b67aaec5c0e0661")
GRAVITY=("Gravity_Player_Production_Factor_",0xCDF2C,167,
      "a0660fd4edfd3b57bb91c406ca614e6c445ff509fb191eb5b757bdc254142200")
DISPATCH=[
 ("Colony_Empire_Base_Food2_Produced_",0xCE0C6,358,"705a9348d1b7e97003bd711a8553e114d453b5fbe745b0706c47dffe1de913c2"),
 ("Colony_Empire_Base_Industry_Produced_",0xCED47,212,"35aa50fa88250f254ba329b69bc8ed99ba7b9d647fe29f1fcffa1e7ecb4c24d8"),
 ("Colony_Empire_Base_Research_Produced_",0xCFE77,253,"1e72e37daea066aa98c587b71c86f1faae81775b60886693b9a3d33b8888e0f9"),
]
NESTED={
 "Colony_Food2_Per_Farmer_":(0xCE03E,136,"6aef5f245db959b949a22eb0cfccd03b65db2c103a18c4dc47f5bbabcf9a04e4"),
 "Colony_Industry_Per_Worker_":(0xCEC95,178,"1e58a5b42e7d04cbc1d412b55ba007dbee502d5f0c257a96890c93d5689d8aa9"),
 "Colony_Research_Per_Scientist_":(0xCFDC6,177,"7d9e54a024e600115cf99d1d299806ceaf74f93c1aa95638a135b97e2efadd14"),
 "memset_":(0x119C70,24,"e1bb125f736118af8cb392e308cbf68630169cada23d288f5adad0c3eb4fdc8c"),
}
SHARED_EXTERNAL = {0xCEE10,0xCEE14,0xCEE17}
# Original named function call begins at CODE+0xCE24E, and 2 conditional
# outcomes jump into common return tail immediately before industry production.
ANCHORS={
 "Colony_Pop_Base_Prod_Produced_":{
   0xCE22C:("push","esi"),0xCE22E:("enter","0x8,0x0"),
   0xCE237:("mov","eax,dword ptr [edx]"),
   0xCE239:("movsx","edi,bx"),
   0xCE23C:("and","eax,0xf"),
   0xCE247:("mov","dword ptr [ebp-0x4],0x0"),
   0xCE24E:("call","dword ptr [edi*4+0xb55c]"),
   0xCE255:("test","ax,ax"),
   0xCE258:("jg","0xce271"),
   0xCE25A:("cmp","word ptr [ebp-0x8],0x0"),
   0xCE261:("cmp","byte ptr [esi+0xdd],0x0"),
   0xCE26A:("mov","dword ptr [ebp-0x4],0x1"),
   0xCE271:("cmp","ax,word ptr [ebp-0x4]"),
   0xCE275:("jge","0xcee17"),
   0xCE27B:("jmp","0xcee14"),
 },
 "Gravity_Player_Production_Factor_":{
   0xCDF2C:("push","ebx"),0xCDF2E:("cmp","byte ptr [eax+0x14f],0x0"),
   0xCDF35:("jne","0xcdfc9"),
   0xCDF3B:("cmp","dx,0x8"),0xCDF3F:("jge","0xcdfc9"),
   0xCDF45:("movsx","eax,word ptr [eax+0x2]"),
   0xCDF56:("cmp","al,0x1"),
   0xCDF69:("movsx","ebx,dx"),0xCDF77:("cmp","byte ptr [ebx+eax*1+0x8a9],0x0"),
   0xCDF81:("mov","ebx,0x3"),
   0xCDF8B:("movsx","eax,dx"),0xCDF9A:("cmp","byte ptr [ebx+eax*1+0x8a9],0x0"),
   0xCDFA6:("movsx","eax,dx"),0xCDFB5:("cmp","byte ptr [ebx+eax*1+0x8aa],0x0"),
   0xCDFBF:("mov","ebx,0x2"),0xCDFC9:("mov","ebx,0x4"),
   0xCDFD2:("ret",""),
 }
}
def sx16(x):
    return (x&65535)-65536 if (x&32768) else x&65535

def controlled_fallback(selector,colony_dd,orig_return_ax):
    if not 0<=selector<=2 or not 0<=colony_dd<=255:
        raise ValueError("controlled original selector, BYTE domains only")
    result=sx16(orig_return_ax)
    fallback=0
    if result<=0 and (selector!=0 or colony_dd>0):
        fallback=1
    return max(result,fallback)

def controlled_gravity(colony_14f,tag,planet_g,player_8a9,player_8aa):
    """Only observed standard gravity 0..2 and valid tag 0..7 are modeled."""
    if not 0<=tag<=8 or planet_g not in (0,1,2):
        raise ValueError("unverified original input domain")
    if colony_14f or tag>=8:return 4
    if planet_g==0:return 4 if player_8a9 else 3
    if planet_g==1:return 3 if player_8a9 else 4
    return 4 if player_8aa else 2

def fixtures():
    assert [controlled_fallback(0,0,v) for v in (-4,0,3)]==[0,0,3]
    assert [controlled_fallback(0,1,v) for v in (-4,0,3)]==[1,1,3]
    assert [controlled_fallback(1,0,v) for v in (-4,0,3)]==[1,1,3]
    assert [controlled_fallback(2,0,v) for v in (-4,0,3)]==[1,1,3]
    assert [controlled_gravity(0,2,g,False,False) for g in (0,1,2)]==[3,4,2]
    assert [controlled_gravity(0,2,g,True,True) for g in (0,1,2)]==[4,3,4]
    assert controlled_gravity(1,2,1,False,False)==4
    assert controlled_gravity(0,8,1,False,False)==4
    return 8

def audit(exe,code,data):
    image=exe.read_bytes();binary=code.read_bytes();db=data.read_bytes()
    if sha(image)!=EXE_SHA or len(binary)!=1410709 or sha(binary)!=CODE_SHA:
        raise ValueError("original source identity changed")
    if len(db)!=81920 or sha(db)!=DATA_SHA:
        raise ValueError("original initialized LE DATA identity changed")
    names={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    for name,off,size,digest in [BASE,GRAVITY,*DISPATCH,*[(k,*v) for k,v in NESTED.items()]]:
        found=names[name]
        if (int(found["offset"]),int(found["inferred_size"]))!=(off,size):
            raise ValueError("original symbol extent mismatch: "+name)
        if sha(binary[off:off+size])!=digest:raise ValueError("original named body changed: "+name)
    sym={(r["name"],r["segment"]):int(r["offset"]) for r in csv.DictReader(
        (ROOT/"decompilation/symbols.csv").open(newline=""))}
    if sym.get(("_colony_empire_base_functions","2"))!=DISPATCH_OFFSET:
        raise ValueError("original dispatch table is not at its DATA symbol")
    for n,a in [("_player",0x1FF98),("_planet",0x1B0D4)]:
        if sym.get((n,"2"))!=a:raise ValueError("original DATA global mismatch: "+n)
    table=db[DISPATCH_OFFSET:DISPATCH_OFFSET+12]
    if sha(table)!=DISPATCH_SHA:
        raise ValueError("3-slot original DATA dispatch changed")
    slots=[struct.unpack_from("<I",table,i*4)[0] for i in range(3)]
    if slots!=[x[1] for x in DISPATCH]:
        raise ValueError("original DATA references do not target named CODE functions")
    all_bodies=[]
    for name,off,size,digest in [BASE,GRAVITY,*DISPATCH]:
        ins,more=parse(code,off,size)
        imap={at:(op,arg) for at,raw,op,arg in ins}
        for at,raw,op,arg in ins:
            if binary[at:at+len(raw)]!=raw:raise ValueError(f"raw CODE byte mismatch {at:#x}")
        for at,expected in ANCHORS.get(name,{}).items():
            if imap.get(at)!=expected:
                raise ValueError(f"opcode anchor {name} {at:#x}: {imap.get(at)} != {expected}")
        direct=[];indirect=[]
        for at,raw,op,arg in ins:
            if op=="call" or op.startswith("j"):
                if not re.fullmatch(r"0x[0-9a-f]+",arg):
                    if (name==BASE[0] and at==0xCE24E and op=="call" and
                        arg=="dword ptr [edi*4+0xb55c]"):
                        indirect.append({"at":hex(at),"table_DATA_offset":hex(DISPATCH_OFFSET),
                                         "slot_targets":[hex(a) for a in slots]})
                        continue
                    raise ValueError(f"unexpected indirect transfer {name} {at:#x} {op} {arg}")
                dest=int(arg,16)
                known_callees={v[0] for v in NESTED.values()}
                if op=="call":
                    if dest not in known_callees:
                        raise ValueError(f"unresolved named helper {name} at {at:#x} -> {dest:#x}")
                elif dest not in imap and dest not in SHARED_EXTERNAL:
                    raise ValueError(f"out-of-body/unresolved transfer {name} {at:#x}->{dest:#x}")
                direct.append({"at":hex(at),"op":op,"dest":hex(dest)})
        all_bodies.append({"name":name,"start":hex(off),"bytes":size,"sha256":digest,
            "complete_instruction_count":len(ins),"complete_decoded_bytes":sum(len(r[1]) for r in ins),
            "extra_byte_rows":more,"direct_transfers":direct,"indirect_dispatch_sites":indirect,
            "exact_opcode_anchors":len(ANCHORS.get(name,{}))})
    # Indirect function endpoints are in CODE, but table pointer is in DATA:
    # explicitly identify every byte of the source shared two-exit tail.
    expected_tail=bytes.fromhex("668945fc8b45fcc95f5ec3")
    tail=binary[0xCEE10:0xCEE1B]
    if tail!=expected_tail:raise ValueError("original shared function epilogue differs")
    return {
       "status":"source-verified-static-indirect-job-dispatch",
       "EXE_sha256":EXE_SHA,"LE_CODE_sha256":CODE_SHA,"LE_INITIALIZED_DATA_sha256":DATA_SHA,
       "dispatch_symbol":"_colony_empire_base_functions",
       "dispatch_DATA_offset":hex(DISPATCH_OFFSET),"dispatch_3xDWORD_SHA256":DISPATCH_SHA,
       "dispatch_slots":[{"job_selector":i,"original_CODE_target":hex(loc),
                           "verified_function":name,"function_bytes":size,
                           "function_sha256":digest}
                         for i,(name,loc,size,digest) in enumerate(DISPATCH)],
       "verified_function_body_procedures":all_bodies,
       "extra_authenticated_named_callees":[{"name":name,"offset":hex(v[0]),
          "bytes":v[1],"sha256":v[2]} for name,v in NESTED.items()],
       "source_shared_return_tail":{"CODE_start":"0xcee10","bytes":tail.hex(),
                       "external_branch_endpoints":["0xcee10","0xcee14","0xcee17"]},
       "controlled_selected_branch_fixtures":fixtures(),
       "limits":["No DOS dynamic execution or comprehensive native-game equivalence",
                 "Three empire-base targets are source-authenticated and full-byte decoded; their modifier meanings remain to be reconstructed",
                 "The indirect selector's behavior is only traced for the three original table slots (0,1,2)",
                 "Gravity helper's behavior for unexpected gravity BYTE values and malformed player tags is not established"],
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--data",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit(args.exe,args.code,args.data)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
