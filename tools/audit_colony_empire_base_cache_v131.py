#!/usr/bin/env python3
"""Authenticate the original v1.31 per-job empire-base cache and return paths.

Static original machine-code bytes, branch targets, CODE/DATA distinctions and
controlled fixtures only. Input caches model in-range selectors 0..9; invalid
pointers, real DOS execution and all caller state lifecycles are not covered.
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
    ("Colony_Empire_Base_Food2_Produced_",0xCE0C6,358,"705a9348d1b7e97003bd711a8553e114d453b5fbe745b0706c47dffe1de913c2"),
    ("Colony_Empire_Base_Industry_Produced_",0xCED47,212,"35aa50fa88250f254ba329b69bc8ed99ba7b9d647fe29f1fcffa1e7ecb4c24d8"),
    ("Colony_Empire_Base_Research_Produced_",0xCFE77,253,"1e72e37daea066aa98c587b71c86f1faae81775b60886693b9a3d33b8888e0f9"),
]
# Byte-for-byte branch and state-identifying source addresses for each routine.
ANCHORS={
 "Colony_Empire_Base_Food2_Produced_":{
    0xCE0D4:("movsx","ax,byte ptr [eax]"),
    0xCE0D8:("cmp","ax,dx"),
    0xCE0DD:("test","ecx,ecx"),
    0xCE0E1:("movzx","eax,byte ptr [esi+0xdd]"),
    0xCE0F2:("call","0xce03e"),
    0xCE0FC:("test","ax,ax"),
    0xCE0FF:("jle","0xce225"),
    0xCE105:("cmp","esi,dword ptr ds:0xb568"),
    0xCE115:("cmp","ax,word ptr [ebp-0x4]"),
    0xCE11B:("test","ecx,ecx"),
    0xCE11F:("mov","ebx,0xa"),
    0xCE124:("mov","edx,0x63"),
    0xCE129:("mov","eax,0x32358"),
    0xCE12E:("call","0x119c70"),
    0xCE136:("mov","dword ptr ds:0xb568,esi"),
    0xCE13C:("mov","ds:0xb56c,al"),
    0xCE144:("cmp","byte ptr [esi+0x32358],0x63"),
    0xCE14B:("jne","0xce219"),
    0xCE153:("xor","ebx,ebx"),
    0xCE155:("cmp","di,0x8"),
    0xCE165:("mov","eax,ds:0x1ff98"),
    0xCE16A:("movsx","edx,byte ptr [esi+eax*1+0x8a1]"),
    0xCE1DD:("jne","0xce1e6"),
    0xCE1DF:("mov","edx,0x6"),
    0xCE1E6:("cmp","di,0x9"),
    0xCE1EC:("mov","edx,0x4"),
    0xCE1F1:("test","ecx,ecx"),
    0xCE203:("add","word ptr [ebp-0x8],dx"),
    0xCE207:("add","word ptr [ebp-0x8],bx"),
    0xCE211:("mov","byte ptr [eax+0x32358],dl"),
    0xCE219:("movsx","ax,byte ptr [esi+0x32358]"),
    0xCE221:("mov","word ptr [ebp-0x8],ax"),
    0xCE225:("mov","eax,dword ptr [ebp-0x8]"),
 },
 "Colony_Empire_Base_Industry_Produced_":{
    0xCED55:("movsx","ax,byte ptr [eax]"),
    0xCED59:("cmp","ax,dx"),
    0xCED5E:("test","ecx,ecx"),
    0xCED62:("movzx","eax,byte ptr [esi+0xde]"),
    0xCED73:("call","0xcec95"),
    0xCED7D:("cmp","esi,dword ptr ds:0xb56d"),
    0xCED8D:("cmp","ax,word ptr [ebp-0x8]"),
    0xCED93:("test","ecx,ecx"),
    0xCED97:("mov","ebx,0xa"),
    0xCED9C:("mov","edx,0x63"),
    0xCEDA1:("mov","eax,0x32362"),
    0xCEDA6:("call","0x119c70"),
    0xCEDAE:("mov","dword ptr ds:0xb56d,esi"),
    0xCEDB4:("mov","ds:0xb571,al"),
    0xCEDBC:("cmp","byte ptr [esi+0x32362],0x63"),
    0xCEDC3:("jne","0xcee08"),
    0xCEDC7:("cmp","di,0x8"),
    0xCEDD9:("movsx","eax,byte ptr [edx+eax*1+0x8a2]"),
    0xCEDE3:("jne","0xcedea"),
    0xCEDE5:("mov","eax,0x3"),
    0xCEDF6:("add","word ptr [ebp-0x4],ax"),
    0xCEE00:("mov","byte ptr [eax+0x32362],dl"),
    0xCEE08:("movsx","ax,byte ptr [esi+0x32362]"),
    0xCEE10:("mov","word ptr [ebp-0x4],ax"),
    0xCEE14:("mov","eax,dword ptr [ebp-0x4]"),
 },
 "Colony_Empire_Base_Research_Produced_":{
    0xCFE85:("movsx","ax,byte ptr [eax]"),
    0xCFE89:("cmp","ax,dx"),
    0xCFE8E:("test","ecx,ecx"),
    0xCFE92:("movzx","eax,byte ptr [esi+0xdf]"),
    0xCFEA3:("call","0xcfdc6"),
    0xCFEAD:("cmp","esi,dword ptr ds:0xb572"),
    0xCFEBD:("cmp","ax,word ptr [ebp-0x8]"),
    0xCFEC3:("test","ecx,ecx"),
    0xCFEC7:("mov","ebx,0xa"),
    0xCFECC:("mov","edx,0x63"),
    0xCFED1:("mov","eax,0x3236c"),
    0xCFED6:("call","0x119c70"),
    0xCFEDE:("mov","dword ptr ds:0xb572,esi"),
    0xCFEE4:("mov","ds:0xb576,al"),
    0xCFEE9:("movsx","eax,di"),
    0xCFEEC:("cmp","byte ptr [eax+0x3236c],0x63"),
    0xCFEF3:("jne","0xcff67"),
    0xCFEFE:("cmp","di,0x8"),
    0xCFF15:("movsx","edx,byte ptr [eax+0x8a3]"),
    0xCFF21:("cmp","byte ptr [eax+0x16b],0x3"),
    0xCFF2A:("mov","dword ptr [ebp-0xc],0x1"),
    0xCFF35:("mov","edx,0x3"),
    0xCFF3A:("test","ecx,ecx"),
    0xCFF4F:("add","edx,dword ptr [ebp-0xc]"),
    0xCFF52:("add","word ptr [ebp-0x4],dx"),
    0xCFF5C:("mov","byte ptr [eax+0x3236c],dl"),
    0xCFF67:("movsx","ax,byte ptr [eax+0x3236c]"),
    0xCFF6F:("jmp","0xcee10"),
 },
}
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
CONT=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s*)+)$",re.I)
ALLOWED_OUT={0xCEE10,0xCEE14}

def sha(b):return hashlib.sha256(b).hexdigest()

def decode(code,start,length):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
        f"--start-address=0x{start:x}",f"--stop-address=0x{start+length:x}",str(code)],
         capture_output=True,text=True,check=True)
    out=[];next_at=start;cont=0
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m:
            at=int(m[1],16);raw=bytes.fromhex(m[2].strip())
            if at!=next_at:raise ValueError(f"CODE gap {next_at:#x}->{at:#x}")
            out.append((at,bytearray(raw),m[3].lower(),m[4].strip().lower()))
            next_at+=len(raw)
            continue
        m=CONT.match(line)
        if m:
            at=int(m[1],16);raw=bytes.fromhex(m[2].strip())
            if at!=next_at or not out:raise ValueError(f"Unassigned opcode continuation {at:#x}")
            out[-1][1].extend(raw);next_at+=len(raw);cont+=1
    if next_at!=start+length:raise ValueError("Incomplete decoder span")
    return out,cont

def signed_byte(v):
    b=v&255
    return b if b<128 else b-256

class SourceCache:
    """Per-original-job BYTE cache keyed by colony pointer, tag and null breakdown."""
    def __init__(self):
        self.key_colony=None
        self.key_tag=None
        self.slots=[99]*10
        self.reset_count=0
    def invoke(self,job,colony_ptr,tag,owner,breakdown,owner_field,helper_base,
               flag_player=0,flag_16b=0,extra_food=0):
        if not 0<=tag<10:raise ValueError("original cache capacity 10, invalid tag excluded")
        if not -128<=owner<=127:raise ValueError("original signed owner BYTE out of range")
        if job not in ("food","industry","research"):raise ValueError("unknown original job")
        # Normal branch calls helper unless signed population tag == signed
        # colony owner and no breakdown pointer was provided.
        base=int(owner_field if tag==owner and not breakdown else helper_base)
        # Food returns before cache initialization if signed AX base <=0.
        if job=="food" and base<=0:return {"word":base&65535,"cache":"bypass"}
        if self.key_colony!=colony_ptr or self.key_tag!=(tag&255) or breakdown:
            self.slots=[99]*10
            self.key_colony=colony_ptr
            self.key_tag=tag&255
            self.reset_count+=1
        slot=self.slots[tag]
        if slot!=99:
            # Original MOVSX AX,BYTE; low 16 bits of result are authoritative.
            return {"word":signed_byte(slot)&65535,"cache":"hit"}
        if job=="food":
            contribution=flag_player if tag<8 else (6 if tag==8 else 4)
            contribution+=extra_food
        elif job=="industry":
            contribution=flag_player if tag<8 else (3 if tag==8 else 0)
        else:
            contribution=flag_player if tag<8 else (3 if tag==8 else 0)
            if tag<8 and tag==owner and flag_16b==3:
                contribution+=1
        total=(base+contribution)&65535
        self.slots[tag]=total&255
        return {"word":total,"cache":"miss"}

def fixtures():
    n=0
    def ck(actual,expected):
        nonlocal n
        assert actual==expected,(actual,expected)
        n+=1
    c=SourceCache()
    ck(c.invoke("industry",10,2,2,False,5,12,flag_player=2),
       {"word":7,"cache":"miss"})
    ck(c.invoke("industry",10,2,2,False,88,99,flag_player=50),
       {"word":7,"cache":"hit"})
    ck(c.reset_count,1)
    ck(c.invoke("industry",10,2,2,True,88,12,flag_player=2),
       {"word":14,"cache":"miss"})
    ck(c.reset_count,2)
    ck(c.invoke("industry",11,2,2,False,9,12,flag_player=1),
       {"word":10,"cache":"miss"})
    ck(c.reset_count,3)
    ck(c.invoke("industry",11,8,2,False,9,12,flag_player=0),
       {"word":15,"cache":"miss"})
    ck(c.invoke("industry",11,9,2,False,9,12,flag_player=1),
       {"word":12,"cache":"miss"})
    food=SourceCache()
    ck(food.invoke("food",22,3,3,False,0,6),{"word":0,"cache":"bypass"})
    ck(food.reset_count,0)
    ck(food.invoke("food",22,3,3,True,0,6,flag_player=2),
       {"word":8,"cache":"miss"})
    ck(food.invoke("food",22,8,3,False,0,6),
       {"word":12,"cache":"miss"})
    ck(food.invoke("food",22,9,3,False,0,6),
       {"word":10,"cache":"miss"})
    r=SourceCache()
    ck(r.invoke("research",42,1,1,False,3,14,flag_player=2,flag_16b=3),
       {"word":6,"cache":"miss"})
    ck(r.invoke("research",42,1,1,False,8,20,flag_player=3,flag_16b=0),
       {"word":6,"cache":"hit"})
    ck(r.invoke("research",42,1,1,True,8,20,flag_player=3,flag_16b=3),
       {"word":24,"cache":"miss"})
    ck(r.invoke("research",42,8,1,False,0,8),{"word":11,"cache":"miss"})
    ck(r.invoke("research",42,9,1,False,0,8),{"word":8,"cache":"miss"})
    # Explicit potential byte-truncation caveat; not a valid game-state claim:
    w=SourceCache()
    ck(w.invoke("industry",100,0,0,False,120,120,flag_player=20),
       {"word":140,"cache":"miss"})
    ck(w.invoke("industry",100,0,0,False,120,120,flag_player=20),
       {"word":(-116)&65535,"cache":"hit"})
    # Sentinel value 99 collision: a computed 99 is indistinguishable from
    # an untouched cache slot and recomputes on the next request.
    sent=SourceCache()
    ck(sent.invoke("industry",55,0,0,False,99,99),
       {"word":99,"cache":"miss"})
    ck(sent.invoke("industry",55,0,0,False,100,100),
       {"word":100,"cache":"miss"})
    return n

def audit(exe_path,code_path):
    game,code=exe_path.read_bytes(),code_path.read_bytes()
    if sha(game)!=EXE_SHA or len(code)!=1410709 or sha(code)!=CODE_SHA:
        raise ValueError("canonical original game or CODE identity mismatch")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    bodies=[];total_ins=0;total_transfers=0;total_opcode_checks=0
    for name,start,size,digest in BODIES:
        r=fs[name]
        if (int(r["offset"]),int(r["inferred_size"]))!=(start,size):
            raise ValueError("Watcom symbol location mismatch: "+name)
        if sha(code[start:start+size])!=digest:raise ValueError("Full body hash changed: "+name)
        ins,cont=decode(code_path,start,size)
        m={addr:(op,arg) for addr,raw,op,arg in ins}
        for addr,raw,op,arg in ins:
            if code[addr:addr+len(raw)]!=raw:
                raise ValueError("Original decoded opcode bytes differ "+hex(addr))
        for addr,expected in ANCHORS[name].items():
            if m.get(addr)!=expected:
                raise ValueError(f"{name} source opcode at {addr:#x}: got {m.get(addr)}, expected {expected}")
        transfer=[]
        for addr,raw,op,arg in ins:
            if op=="call" or op.startswith("j"):
                if not re.fullmatch(r"0x[0-9a-f]+",arg):raise ValueError("Indirect transfer newly found")
                dest=int(arg,16)
                if op.startswith("j") and dest not in m and dest not in ALLOWED_OUT:
                    raise ValueError(f"Unknown direct jump {addr:#x}->{dest:#x}")
                transfer.append({"at":hex(addr),"opcode":op,"target":hex(dest)})
        body_calls=[int(x["target"],16) for x in transfer if x["opcode"]=="call"]
        expected_helper={"Colony_Empire_Base_Food2_Produced_":0xCE03E,
                         "Colony_Empire_Base_Industry_Produced_":0xCEC95,
                         "Colony_Empire_Base_Research_Produced_":0xCFDC6}[name]
        if sorted(body_calls)!=sorted([0x119C70,expected_helper]):
            raise ValueError(f"Original cache helper/memset call inventory differs: {name} {body_calls}")
        bodies.append({"name":name,"CODE_offset":hex(start),"full_bytes":size,"SHA256":digest,
                       "decoded_machine_instructions":len(ins),"source_transfer_count":len(transfer),
                       "continuation_rows":cont,"exact_opcode_checks":len(ANCHORS[name]),
                       "direct_transfer_inventory":transfer})
        total_ins+=len(ins);total_transfers+=len(transfer);total_opcode_checks+=len(ANCHORS[name])
    tests=fixtures()
    return {
       "status":"source-verified-original-per-job-empire-base-cache-behavior",
       "source_executable_SHA256":EXE_SHA,"original_LE_CODE_SHA256":CODE_SHA,
       "source_bodies":bodies,"all_source_instructions":total_ins,
       "all_direct_calls_and_branches":total_transfers,
       "exact_instruction_anchors":total_opcode_checks,
       "controlled_cache_fixtures":tests,
       "cache_addresses":{
         "food":{"key_colony_DATA":"0xb568","key_tag_DATA":"0xb56c","cache_DATA":"0x32358","colony_owned_cached_BYTE":"0xdd"},
         "industry":{"key_colony_DATA":"0xb56d","key_tag_DATA":"0xb571","cache_DATA":"0x32362","colony_owned_cached_BYTE":"0xde"},
         "research":{"key_colony_DATA":"0xb572","key_tag_DATA":"0xb576","cache_DATA":"0x3236c","colony_owned_cached_BYTE":"0xdf"}},
       "cache_sentinel":99,"cache_slots":10,
       "invalidated_on":["colony pointer mismatch","tag byte mismatch","non-null breakdown pointer"],
       "cache_hit":"signed BYTE cache slot value is sign extended into AX; upper 16-bit EAX not claimed",
       "cache_miss":"normal parent helper return plus tag-specific original contribution is stored as low BYTE in slot",
       "food_exception":"base <=0 returns early without updating cache keys or sentinel array",
       "limitations":["No original DOS execution or actual valid-state differential comparison",
                      "This models low WORD return only, not potentially undefined EAX upper register bits",
                      "Source-verified static model restricted to original ten slot indexes 0..9",
                      "Additional food climate-component subbranches not modeled except as controlled input"]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
