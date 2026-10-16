#!/usr/bin/env python3
"""Reconstruct and test all three source-original v1.31 per-job BASE formulas.

Verifies original ORION2.EXE, extracted Watcom LE CODE, complete full helper
bytes, unbroken decoded machine instructions and all internal branches, the
5-byte original CODE minerals-per-mine table, and original DATA pointers.
Controlled model validates exact source input cases and optional breakdown
field *writes*, not a native DOS dynamic differential execution.
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
BODIES=[
    ("Colony_Food2_Per_Farmer_",0xCE03E,136,"6aef5f245db959b949a22eb0cfccd03b65db2c103a18c4dc47f5bbabcf9a04e4"),
    ("Colony_Industry_Per_Worker_",0xCEC95,178,"1e58a5b42e7d04cbc1d412b55ba007dbee502d5f0c257a96890c93d5689d8aa9"),
    ("Colony_Research_Per_Scientist_",0xCFDC6,177,"7d9e54a024e600115cf99d1d299806ceaf74f93c1aa95638a135b97e2efadd14"),
]
MINERALS=(1,2,3,5,8)
MINERALS_OFF=0xCD4B5
MINERALS_SHA="0a834026e5178e5a668be1e368aeb321b6acdd1d651a3eb141541de4531c6c20"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
RX_CONT=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s*)+)$",re.I)
ANCHORS={
 "Colony_Food2_Per_Farmer_":{
 0xCE050:("movzx","dx,byte ptr [edx+eax*1+0xb]"),
 0xCE056:("add","edx,edx"),
 0xCE074:("cmp","byte ptr [esi+eax*1+0x134],0x3"),
 0xCE07E:("mov","edx,0x2"),
 0xCE087:("mov","word ptr [ebx+0x52],dx"),
 0xCE090:("cmp","byte ptr [ecx+0x164],0x0"),
 0xCE099:("add","edx,0x4"),
 0xCE0A0:("mov","word ptr [ebx+0x21c],0x4"),
 0xCE0A9:("cmp","byte ptr [ecx+0x13a],0x0"),
 0xCE0B2:("inc","edx"),
 0xCE0B3:("inc","edx"),
 0xCE0B8:("mov","word ptr [ebx+0x1c8],0x2"),
 0xCE0C1:("mov","eax,edx"),
 },
 "Colony_Industry_Per_Worker_":{
 0xCEC97:("mov","ecx,eax"),
 0xCEC9B:("movsx","eax,word ptr [eax+0x2]"),
 0xCECAC:("movzx","dx,byte ptr [eax+0xcd4b5]"),
 0xCECBD:("cmp","byte ptr [ecx+0x13a],0x0"),
 0xCECC6:("inc","edx"),
 0xCECCB:("mov","word ptr [ebx+0x1c8],0x1"),
 0xCECD4:("cmp","byte ptr [ecx+0x13d],0x0"),
 0xCECDD:("inc","edx"),
 0xCECE2:("mov","word ptr [ebx+0x1ce],0x1"),
 0xCECEB:("cmp","byte ptr [ecx+0x15a],0x0"),
 0xCECF4:("inc","edx"),
 0xCECF5:("inc","edx"),
 0xCECFA:("mov","word ptr [ebx+0x208],0x2"),
 0xCED03:("cmp","byte ptr [ecx+0x142],0x0"),
 0xCED0C:("add","edx,0x3"),
 0xCED13:("mov","word ptr [ebx+0x1d8],0x3"),
 0xCED2A:("cmp","byte ptr [ecx+eax*1+0x183],0x3"),
 0xCED34:("inc","edx"),
 0xCED39:("mov","word ptr [ebx+0xf0],0x1"),
 0xCED42:("mov","eax,edx"),
 },
 "Colony_Research_Per_Scientist_":{
 0xCFDC7:("mov","edx,0x3"),
 0xCFDD6:("cmp","byte ptr [eax+0x13a],0x0"),
 0xCFDDF:("inc","edx"),
 0xCFDE4:("mov","word ptr [ebx+0x1c8],0x1"),
 0xCFDED:("cmp","byte ptr [eax+0x154],0x0"),
 0xCFDF6:("inc","edx"),
 0xCFDF7:("inc","edx"),
 0xCFDFC:("mov","word ptr [ebx+0x1fc],0x2"),
 0xCFE05:("cmp","byte ptr [eax+0x149],0x0"),
 0xCFE0E:("add","edx,0x3"),
 0xCFE15:("mov","word ptr [ebx+0x1e6],0x3"),
 0xCFE1E:("cmp","byte ptr [eax+0x159],0x0"),
 0xCFE27:("inc","edx"),
 0xCFE2C:("mov","word ptr [ebx+0x206],0x1"),
 0xCFE42:("mov","al,byte ptr [ecx+eax*1+0xf]"),
 0xCFE46:("cmp","al,0xa"),
 0xCFE54:("inc","edx"),
 0xCFE55:("inc","edx"),
 0xCFE5A:("add","dword ptr [ebx+0x226],0x2"),
 0xCFE65:("add","edx,0x5"),
 0xCFE6C:("add","dword ptr [ebx+0x226],0x5"),
 0xCFE73:("mov","eax,edx"),
 }
}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def decode(code_path,start,length):
    cmd=["objdump","-D","-b","binary","-m","i386","-M","intel",
         f"--start-address=0x{start:x}",f"--stop-address=0x{start+length:x}",str(code_path)]
    r=subprocess.run(cmd,capture_output=True,text=True,check=True)
    entries=[];next_addr=start;continuations=[]
    for line in r.stdout.splitlines():
        m=RX.match(line)
        if m:
            at=int(m[1],16);raw=bytes.fromhex(m[2].strip())
            if at!=next_addr:raise ValueError(f"CODE gap at {next_addr:#x}, next {at:#x}")
            entries.append([at,raw,m[3].lower(),m[4].strip().lower()])
            next_addr+=len(raw)
            continue
        m=RX_CONT.match(line)
        if m:
            at=int(m[1],16);raw=bytes.fromhex(m[2].strip())
            if not entries or next_addr!=at:
                raise ValueError(f"Disassembler continuation error {at:#x}")
            entries[-1][1]+=raw
            next_addr+=len(raw)
            continuations.append({"at":hex(at),"starts_instruction":hex(entries[-1][0]),"bytes":len(raw)})
    if next_addr!=start+length:
        raise ValueError(f"Incomplete body {start:#x}: {next_addr-start} != {length}")
    return entries,continuations

def flag(flags,addr):
    return int(bool(flags.get(addr,False)))

def farmer(planet_byte_b,player_flag_134,flags,breakdown=False):
    """Original normal v1.31 per-farmer base; synthetic valid planet/player."""
    if not 0<=planet_byte_b<=255:raise ValueError("planet byte must be unsigned")
    total=2*planet_byte_b
    writes={0x00:("dword",total)} if breakdown else {}
    if total==0 and player_flag_134==3:
        total=2
        if breakdown:writes[0x52]=("word",2)
    if total>0:
        if flag(flags,0x164):
            total+=4
            if breakdown:writes[0x21c]=("word",4)
        if flag(flags,0x13a):
            total+=2
            if breakdown:writes[0x1c8]=("word",2)
    return {"return":total,"writes":writes}

def worker(mineral_idx,flags,player_flag_183,breakdown=False):
    """Original source CODE _minerals_per_mine table and original ordered adds."""
    if not 0<=mineral_idx<5:raise ValueError("source table has five entries; no OOB modeling")
    total=MINERALS[mineral_idx]
    writes={0x00:("dword",total)} if breakdown else {}
    for colony_flag,delta,offset in (
        (0x13a,1,0x1c8),(0x13d,1,0x1ce),(0x15a,2,0x208),(0x142,3,0x1d8)):
        if flag(flags,colony_flag):
            total+=delta
            if breakdown:writes[offset]=("word",delta)
    if player_flag_183==3:
        total+=1
        if breakdown:writes[0xf0]=("word",1)
    return {"return":total,"writes":writes}

def scientist(planet_byte_f,flags,breakdown=False,initial_bonus_226=0):
    """Original 3-base, four flags, planet index 10/11 adjustment."""
    if not 0<=planet_byte_f<=255:raise ValueError("planet byte must be unsigned")
    if not 0<=initial_bonus_226<=(1<<31)-6:
        raise ValueError("breakdown fixture would overflow signed DWORD")
    total=3
    writes={0x00:("dword",3)} if breakdown else {}
    for colony_flag,delta,offset in (
        (0x13a,1,0x1c8),(0x154,2,0x1fc),(0x149,3,0x1e6),(0x159,1,0x206)):
        if flag(flags,colony_flag):
            total+=delta
            if breakdown:writes[offset]=("word",delta)
    planet_delta=2 if planet_byte_f==10 else (5 if planet_byte_f==11 else 0)
    if planet_delta:
        total+=planet_delta
        if breakdown:writes[0x226]=("dword_add",planet_delta)
    return {"return":total,"writes":writes}

def controlled_fixtures():
    # Each controlled fixture is independently implied by exact original branch code.
    checks=0
    def check(found,expected):
        nonlocal checks
        assert found==expected,(found,expected)
        checks+=1
    check(farmer(0,0,{}),{"return":0,"writes":{}})
    check(farmer(0,3,{}),{"return":2,"writes":{}})
    check(farmer(0,3,{0x164:True,0x13a:True},True),
          {"return":8,"writes":{0:("dword",0),0x52:("word",2),
                       0x21c:("word",4),0x1c8:("word",2)}})
    check(farmer(0,0,{0x164:True,0x13a:True},True),
          {"return":0,"writes":{0:("dword",0)}})
    check(farmer(3,0,{},True),{"return":6,"writes":{0:("dword",6)}})
    check(farmer(3,0,{0x164:True,0x13a:True},True),
          {"return":12,"writes":{0:("dword",6),0x21c:("word",4),0x1c8:("word",2)}})
    for i,base in enumerate(MINERALS):
        check(worker(i,{},0,True),{"return":base,"writes":{0:("dword",base)}})
    check(worker(2,{0x13a:True,0x13d:True,0x15a:True,0x142:True},3,True),
          {"return":11,"writes":{0:("dword",3),0x1c8:("word",1),
                0x1ce:("word",1),0x208:("word",2),0x1d8:("word",3),0xf0:("word",1)}})
    check(worker(4,{0x142:True},0),{"return":11,"writes":{}})
    check(scientist(0,{},True),{"return":3,"writes":{0:("dword",3)}})
    check(scientist(10,{},True),
          {"return":5,"writes":{0:("dword",3),0x226:("dword_add",2)}})
    check(scientist(11,{},True),
          {"return":8,"writes":{0:("dword",3),0x226:("dword_add",5)}})
    check(scientist(12,{},True),{"return":3,"writes":{0:("dword",3)}})
    check(scientist(11,{0x13a:True,0x154:True,0x149:True,0x159:True},True),
          {"return":15,"writes":{0:("dword",3),0x1c8:("word",1),
              0x1fc:("word",2),0x1e6:("word",3),0x206:("word",1),
              0x226:("dword_add",5)}})
    check(scientist(0,{0x13a:True,0x154:True,0x149:True,0x159:True}),
          {"return":10,"writes":{}})
    return checks

def audit(exe_path,code_path):
    exe,code=exe_path.read_bytes(),code_path.read_bytes()
    if sha(exe)!=EXE_SHA or len(code)!=1410709 or sha(code)!=CODE_SHA:
        raise ValueError("Authenticated original binary/LE CODE changed")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    syms={(r["name"],r["segment"]):int(r["offset"])
          for r in csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    for symbol,segment,addr in (
        ("_minerals_per_mine","1",MINERALS_OFF),
        ("_player","2",0x1FF98),
        ("_planet","2",0x1B0D4)):
        if syms.get((symbol,segment))!=addr:
            raise ValueError(f"Original CODE/DATA symbol mismatch {symbol}")
    if code[MINERALS_OFF:MINERALS_OFF+5]!=bytes(MINERALS) or sha(bytes(MINERALS))!=MINERALS_SHA:
        raise ValueError("Original Watcom mineral table changed")
    bodies=[];count_instr=0;count_edges=0;count_anchors=0
    for name,start,length,expected in BODIES:
        f=fs[name]
        if (int(f["offset"]),int(f["inferred_size"]))!=(start,length):
            raise ValueError("Source named-body size/location differs: "+name)
        if sha(code[start:start+length])!=expected:
            raise ValueError("Original full function bytes changed "+name)
        ins,cont=decode(code_path,start,length)
        ipmap={at:(op,arg) for at,raw,op,arg in ins}
        for at,raw,op,arg in ins:
            if code[at:at+len(raw)]!=raw:
                raise ValueError("Instruction byte mismatch "+hex(at))
        for at,expected_op in ANCHORS[name].items():
            if ipmap.get(at)!=expected_op:
                raise ValueError(f"{name} {at:#x}: {ipmap.get(at)} != {expected_op}")
        branches=[]
        for at,raw,op,arg in ins:
            if op=="call":
                raise ValueError(f"Unexpected nested CALL in {name} at {at:#x}")
            if op.startswith("j"):
                if not re.fullmatch(r"0x[0-9a-f]+",arg):
                    raise ValueError(f"Unresolved transfer {name} {at:#x}")
                dst=int(arg,16)
                if dst not in ipmap:
                    raise ValueError(f"Unexpected branch target {name} {at:#x}->{dst:#x}")
                branches.append({"from":hex(at),"opcode":op,"to":hex(dst)})
        bodies.append({"name":name,"CODE_offset":hex(start),"length":length,"SHA256":expected,
                       "machine_instructions":len(ins),
                       "decoder_continuations":cont,
                       "original_branch_inventory":branches,
                       "source_opcode_anchors":len(ANCHORS[name])})
        count_instr+=len(ins);count_edges+=len(branches);count_anchors+=len(ANCHORS[name])
    fixtures=controlled_fixtures()
    return {"status":"source-verified-per-job-base-behavior-with-controlled-fixtures",
       "canonical_EXE_SHA256":EXE_SHA,"original_LE_CODE_SHA256":CODE_SHA,
       "authenticated_functions":bodies,
       "total_decoded_instructions":count_instr,
       "total_direct_branch_transfers":count_edges,
       "total_exact_opcode_anchors":count_anchors,
       "original_CODE_mineral_table":{"offset":hex(MINERALS_OFF),"values":list(MINERALS),"SHA256":MINERALS_SHA},
       "controlled_synthetic_fixture_count":fixtures,
       "observed_formulas":{
        "food":"2*planet BYTE+0x0b; if zero and pop-owner player BYTE+0x134==3 use 2; only when positive add +4 if colony BYTE+0x164 and +2 if colony BYTE+0x13a",
        "industry":"CODE _minerals_per_mine[planet BYTE+0x0a] plus colony flags +1 (0x13a), +1 (0x13d), +2 (0x15a), +3 (0x142), plus +1 if pop-owner player BYTE+0x183==3",
        "research":"3 plus colony flags +1 (0x13a), +2 (0x154), +3 (0x149), +1 (0x159), plus +2 if planet BYTE+0x0f==10 or +5 if equals 11"},
       "optional_breakdown_writes_verified_by_anchors":True,
       "limitations":["Neither runtime DOS differential execution nor engine-wide native-game equivalence",
                       "Out-of-bounds minerals table indices and invalid planet/player pointers not modeled",
                       "All field names denote byte offsets; complex gameplay meaning and global state lifecycle unproven"]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
