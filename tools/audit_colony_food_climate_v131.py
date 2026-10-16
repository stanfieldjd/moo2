#!/usr/bin/env python3
"""Source-authenticate v1.31 food empire-base climate correction, its DATA table,
original branch paths and signed production/breakdown arithmetic.

This is a bounded static reconstruction against official game bytes, NOT a
dynamic original-DOS differential test or full-state native implementation.
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
DATA_SHA="082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b"
START,SIZE=0xCE0C6,358
BODY_SHA="705a9348d1b7e97003bd711a8553e114d453b5fbe745b0706c47dffe1de913c2"
TABLE_OFF=0x581C
TABLE=(0,0,0,1,1,2,2,1,2,3)
TABLE_SHA="00723b29c9735d5b593affde81837443b627641360d56ca40823caf383978979"
NEIGHBOR_OFF=0x5817
NEIGHBOR=(0,0,0,246,236)
NEIGHBOR_SHA="d742b1a62b60c33d63c043e624f700af96f1fdf38b2d67638922274f1e60179f"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
CONT=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s*)+)$",re.I)
OPS={
 0xCE0FC:("test","ax,ax"),
 0xCE0FF:("jle","0xce225"),
 0xCE105:("cmp","esi,dword ptr ds:0xb568"),
 0xCE11B:("test","ecx,ecx"),
 0xCE11D:("je","0xce141"),
 0xCE124:("mov","edx,0x63"),
 0xCE129:("mov","eax,0x32358"),
 0xCE12E:("call","0x119c70"),
 0xCE136:("mov","dword ptr ds:0xb568,esi"),
 0xCE13C:("mov","ds:0xb56c,al"),
 0xCE144:("cmp","byte ptr [esi+0x32358],0x63"),
 0xCE14B:("jne","0xce219"),
 0xCE151:("xor","edx,edx"),
 0xCE153:("xor","ebx,ebx"),
 0xCE155:("cmp","di,0x8"),
 0xCE159:("jge","0xce1dd"),
 0xCE16A:("movsx","edx,byte ptr [esi+eax*1+0x8a1]"),
 0xCE172:("cmp","byte ptr [esi+eax*1+0x8ab],0x0"),
 0xCE17A:("je","0xce1f1"),
 0xCE180:("mov","eax,ds:0xb568"),
 0xCE185:("mov","al,byte ptr [eax+0xe2]"),
 0xCE18B:("cmp","al,0x5"),
 0xCE18D:("jb","0xce19b"),
 0xCE18F:("jbe","0xce1c0"),
 0xCE191:("cmp","al,0x6"),
 0xCE193:("jbe","0xce19f"),
 0xCE195:("cmp","al,0x8"),
 0xCE197:("je","0xce1c0"),
 0xCE199:("jmp","0xce1f1"),
 0xCE19B:("cmp","al,0x4"),
 0xCE19D:("jne","0xce1f1"),
 0xCE19F:("mov","ebx,dword ptr ds:0xb568"),
 0xCE1A5:("movzx","ebx,byte ptr [ebx+0xe2]"),
 0xCE1AC:("movzx","eax,byte ptr [ebx+0x581c]"),
 0xCE1B3:("movzx","ebx,byte ptr ds:0x5824"),
 0xCE1BA:("sub","ebx,eax"),
 0xCE1BC:("add","ebx,ebx"),
 0xCE1BE:("jmp","0xce1f1"),
 0xCE1C0:("mov","ebx,dword ptr ds:0xb568"),
 0xCE1C6:("movzx","ebx,byte ptr [ebx+0xe2]"),
 0xCE1CD:("movzx","eax,byte ptr [ebx+0x581c]"),
 0xCE1D4:("movzx","ebx,byte ptr ds:0x5825"),
 0xCE1DB:("jmp","0xce1ba"),
 0xCE1DD:("jne","0xce1e6"),
 0xCE1DF:("mov","edx,0x6"),
 0xCE1E6:("cmp","di,0x9"),
 0xCE1EC:("mov","edx,0x4"),
 0xCE1F1:("test","ecx,ecx"),
 0xCE1F8:("mov","word ptr [ecx+esi*2+0x4],dx"),
 0xCE1FD:("mov","dword ptr [ecx+0x222],ebx"),
 0xCE203:("add","word ptr [ebp-0x8],dx"),
 0xCE207:("add","word ptr [ebp-0x8],bx"),
 0xCE211:("mov","byte ptr [eax+0x32358],dl"),
 0xCE219:("movsx","ax,byte ptr [esi+0x32358]"),
}
def sha(b):
    return hashlib.sha256(b).hexdigest()

def disassemble(code):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
         f"--start-address=0x{START:x}",f"--stop-address=0x{START+SIZE:x}",str(code)],
          capture_output=True,text=True,check=True)
    out=[];next_at=START;continued=0
    for ln in p.stdout.splitlines():
        m=RX.match(ln)
        if m:
            at=int(m[1],16);raw=bytes.fromhex(m[2].strip())
            if at!=next_at:raise ValueError(f"Original instruction gap {next_at:#x}->{at:#x}")
            out.append([at,bytearray(raw),m[3].lower(),m[4].strip().lower()])
            next_at+=len(raw)
        else:
            m=CONT.match(ln)
            if m:
                at=int(m[1],16);raw=bytes.fromhex(m[2].strip())
                if not out or next_at!=at:raise ValueError("Unexpected continuation")
                out[-1][1].extend(raw);next_at+=len(raw);continued+=1
    if next_at!=START+SIZE:raise ValueError("Full source body not decoded")
    return out,continued

def signed_byte(x):
    x=x&0xff
    return x if x<128 else x-256

def climate_delta(climate_index, enabled):
    """Source-exact small valid index domain. This is not _climate_modifier_table."""
    if not isinstance(climate_index,int) or not 0<=climate_index<=255:
        raise ValueError("climate state must be one unsigned source BYTE")
    if not enabled:return 0
    if climate_index in (4,6):ref=TABLE[8] # original DATA BYTE 0x5824
    elif climate_index in (5,8):ref=TABLE[9] # original DATA BYTE 0x5825
    else:return 0
    return 2*(ref-TABLE[climate_index])

def food_miss(base_word, tag, *, player_byte_8a1=0,player_byte_8ab=0,
              climate_index=0, has_breakdown=False):
    """Bounded clean snapshot of the original cache-miss adjustment only.

    Caller already selected the initial base and took source's early exit for
    signed base <=0. The CACHE HIT path does not run the climate branch.
    """
    if not 0<=tag<10:raise ValueError("tag outside source array slots")
    if not 1<=base_word<=1000:raise ValueError("bounded positive base fixture required")
    if not -128<=player_byte_8a1<=127:raise ValueError("source player field is signed BYTE")
    if not 0<=player_byte_8ab<=255:raise ValueError("flag byte outside source domain")
    if not 0<=climate_index<=255:raise ValueError("invalid source climate BYTE")
    owner_bonus=signed_byte(player_byte_8a1) if tag<8 else (6 if tag==8 else 4)
    modifier=climate_delta(climate_index,player_byte_8ab!=0) if tag<8 else 0
    value=(base_word+owner_bonus+modifier)&0xffff
    breakdown=({0x04+tag*2:("word",owner_bonus&0xffff),0x222:("dword",modifier&0xffffffff)}
               if has_breakdown else {})
    return {"low_WORD":value,"cache_BYTE":value&255,
            "population_bonus_signed":owner_bonus,"climate_bonus_signed":modifier,
            "breakdown_writes":breakdown}

def test_models():
    n=0
    def check(actual,expected):
        nonlocal n
        assert actual==expected,(actual,expected)
        n+=1
    # Independent table-derived expected climate result for all ten indices.
    expected=[0,0,0,0,2,2,0,0,2,0]
    for climate,result in enumerate(expected):
        check(climate_delta(climate,True),result)
        check(climate_delta(climate,False),0)
    for climate in (10,11,127,255):
        # Source branches to final aggregation without indexing table.
        check(climate_delta(climate,True),0)
    check(food_miss(10,0,player_byte_8a1=3,player_byte_8ab=1,climate_index=4),
          {"low_WORD":15,"cache_BYTE":15,"population_bonus_signed":3,
           "climate_bonus_signed":2,"breakdown_writes":{}})
    check(food_miss(10,0,player_byte_8a1=-3,player_byte_8ab=1,climate_index=5,
          has_breakdown=True),
          {"low_WORD":9,"cache_BYTE":9,"population_bonus_signed":-3,
           "climate_bonus_signed":2,"breakdown_writes":{
             0x04:("word",0xfffd),0x222:("dword",2)}})
    check(food_miss(10,0,player_byte_8a1=4,player_byte_8ab=0,climate_index=4,
          has_breakdown=True),
          {"low_WORD":14,"cache_BYTE":14,"population_bonus_signed":4,
           "climate_bonus_signed":0,"breakdown_writes":{
             0x04:("word",4),0x222:("dword",0)}})
    check(food_miss(10,8,player_byte_8ab=1,climate_index=4,has_breakdown=True),
          {"low_WORD":16,"cache_BYTE":16,"population_bonus_signed":6,
           "climate_bonus_signed":0,"breakdown_writes":{
             0x14:("word",6),0x222:("dword",0)}})
    check(food_miss(10,9,player_byte_8ab=1,climate_index=8),
          {"low_WORD":14,"cache_BYTE":14,"population_bonus_signed":4,
           "climate_bonus_signed":0,"breakdown_writes":{}})
    check(food_miss(1,0,player_byte_8a1=-5,player_byte_8ab=1,climate_index=4),
          {"low_WORD":65534,"cache_BYTE":254,"population_bonus_signed":-5,
           "climate_bonus_signed":2,"breakdown_writes":{}})
    # Other climates not in dispatch have no modifier even when source table
    # would yield a different value; this guards branch misinterpretations.
    check(food_miss(9,0,player_byte_8a1=0,player_byte_8ab=1,climate_index=7)["climate_bonus_signed"],0)
    return n

def audit(exe,code,data):
    if sha(exe.read_bytes())!=EXE_SHA:raise ValueError("Original DOS EXE mismatch")
    image=code.read_bytes();init=data.read_bytes()
    if len(image)!=1410709 or sha(image)!=CODE_SHA:
        raise ValueError("Original Watcom CODE digest mismatch")
    if len(init)!=81920 or sha(init)!=DATA_SHA:
        raise ValueError("Original initialized Watcom DATA digest mismatch")
    with (ROOT/"decompilation/functions.csv").open(newline="") as f:
        fns={x["name"]:x for x in csv.DictReader(f)}
    f=fns["Colony_Empire_Base_Food2_Produced_"]
    if (int(f["offset"]),int(f["inferred_size"]))!=(START,SIZE):
        raise ValueError("Original named body/extent differs")
    if sha(image[START:START+SIZE])!=BODY_SHA:
        raise ValueError("Original source function-body digest differs")
    with (ROOT/"decompilation/symbols.csv").open(newline="") as f:
        syms={(x["name"],x["segment"]):int(x["offset"]) for x in csv.DictReader(f)}
    for key,off in {
      ("_food_per_farmer_table","2"):TABLE_OFF,
      ("_climate_modifier_table","2"):NEIGHBOR_OFF,
      ("_player","2"):0x1ff98,
    }.items():
        if syms.get(key)!=off:raise ValueError(f"Original DATA symbol differs {key}")
    table=init[TABLE_OFF:TABLE_OFF+len(TABLE)]
    neighbor=init[NEIGHBOR_OFF:NEIGHBOR_OFF+len(NEIGHBOR)]
    if tuple(table)!=TABLE or sha(table)!=TABLE_SHA:
        raise ValueError("Initialized food DATA lookup differs")
    if tuple(neighbor)!=NEIGHBOR or sha(neighbor)!=NEIGHBOR_SHA:
        raise ValueError("Adjacent climate-modifier DATA differs")
    instructions,continuations=disassemble(code)
    mp={addr:(op,arg) for addr,raw,op,arg in instructions}
    for addr,raw,op,arg in instructions:
        if image[addr:addr+len(raw)]!=raw:raise ValueError("Decoded instruction differs")
    for addr,expected in OPS.items():
        if mp.get(addr)!=expected:
            raise ValueError(f"Original CODE anchor {addr:#x}: {mp.get(addr)} != {expected}")
    branch_count=0
    for addr,raw,op,arg in instructions:
        if op.startswith("j"):
            if not re.fullmatch(r"0x[0-9a-f]+",arg):
                raise ValueError("Unresolved indirect branch")
            dst=int(arg,16)
            if dst not in mp:raise ValueError(f"Branch to non-instruction {addr:#x}->{dst:#x}")
            branch_count+=1
    fixtures=test_models()
    return {
      "status":"source-authenticated-bounded-food-climate-adjustment",
      "original_EXE_SHA256":EXE_SHA,"CODE_SHA256":CODE_SHA,"initialized_DATA_SHA256":DATA_SHA,
      "verified_named_body":{"name":"Colony_Empire_Base_Food2_Produced_",
                             "offset":hex(START),"bytes":SIZE,"sha256":BODY_SHA},
      "source_decoded_instructions":len(instructions),"decoder_continuation_rows":continuations,
      "validated_direct_internal_branches":branch_count,
      "exact_opcode_anchors":len(OPS),
      "original_DATA_food_table":{"symbol":"_food_per_farmer_table","offset":hex(TABLE_OFF),
                                  "bytes":list(TABLE),"sha256":TABLE_SHA,
                                  "reference_8_DATA":hex(TABLE_OFF+8),
                                  "reference_9_DATA":hex(TABLE_OFF+9)},
      "different_adjacent_DATA_table":{"symbol":"_climate_modifier_table",
                             "offset":hex(NEIGHBOR_OFF),"bytes":list(NEIGHBOR),
                             "sha256":NEIGHBOR_SHA},
      "climate_formula":"if tag<8 and player BYTE+0x8ab !=0: climate 4 or 6 =>2*(food_table[8]-food_table[climate]); climate 5 or 8 =>2*(food_table[9]-food_table[climate]); otherwise 0",
      "cache_miss_effects":"for tag<8: signed player BYTE+0x8a1 plus climate; tag==8 adds 6; tag==9 adds 4; write low 8 bits of WORD result to food cache",
      "optional_breakdown_writes":"WORD at +4+2*tag is signed player bonus (or 6/4), DWORD at +0x222 is climate increment (including zero)",
      "bounded_synthetic_fixtures":fixtures,
      "scope_limitations":["Original DOS runtime differential not performed",
           "Source climate BYTE branch gates table indexing to codes 4/5/6/8; no invalid pointer domains modeled",
           "All source globals/caller lifetimes and invalid-state cases not established",
           "This audits cache miss only; original cache-hit return path is separately audited"]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--data",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit(a.exe,a.code,a.data)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
