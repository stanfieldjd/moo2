#!/usr/bin/env python3
"""Original MOO2 v1.31 source-based food/industry maintenance counter routes.

Whole-function SHA and instruction coverage, branch/counter opcode proofs,
bounded packed-tag and flag classification fixtures. This is not an execution
of original DOS program and does not prove legal race/colony combinations.
"""
import argparse,csv,hashlib,json
from itertools import product
from pathlib import Path
from audit_remaining_colony_production_callers_v131 import parse
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BODIES=[
 ("Colony_Food_Maintenance_",0xCEB4B,330,"005961c516ea2f30e4534b7e7c5eb4ede279dc9c53d89a49fd2f5214b5f84030"),
 ("Colony_Industry_Maintenance_",0xCF546,297,"a3d24386fbaa9dfe229d88dcb34c2c661f3dc2169cdec44481c558542e0fb0ed"),
 ("Convert_Player_To_Flags_",0x4AD97,161,"e84d39178d6ef63e679d205d734a991add5d774997653e3edba64b2a371f9d95"),
 ("Convert_Flags_To_Player_",0x4AE38,188,"55e168ee1847ba7de6868476a4acff3811b89d1b996c8555c0dec08666eb0fd5"),
]
OPS={
 "Colony_Food_Maintenance_":{
 0xCEBBF:("mov","edx,dword ptr [edi+eax*4]"),
 0xCEBC2:("mov","eax,dword ptr [edi+eax*4]"),
 0xCEBC5:("shl","eax,0x15"),
 0xCEBC8:("shr","eax,0x1f"),
 0xCEBCB:("and","edx,0xf"),
 0xCEBD1:("cmp","dx,0x8"),
 0xCEBD5:("jge","0xcec3d"),
 0xCEBDE:("imul","eax,eax,0xea9"),
 0xCEBE4:("mov","ebx,dword ptr ds:0x1ff98"),
 0xCEBEC:("cmp","byte ptr [eax+0x8b0],0x0"),
 0xCEBF3:("je","0xcebfc"),
 0xCEBF5:("mov","eax,0x1"),
 0xCEBFC:("cmp","byte ptr [eax+0x8b1],0x0"),
 0xCEC03:("je","0xcec09"),
 0xCEC05:("xor","eax,eax"),
 0xCEC09:("mov","eax,0x2"),
 0xCEC0E:("cmp","dx,word ptr [ebp-0x4]"),
 0xCEC14:("add","byte ptr [ecx+0xfc],al"),
 0xCEC1C:("cmp","word ptr [ebp-0x8],0x0"),
 0xCEC23:("add","byte ptr [ecx+0xfe],al"),
 0xCEC2B:("add","byte ptr [ecx+0xfd],al"),
 0xCEC34:("add","byte ptr [ecx+edx*1+0x104],al"),
 0xCEC3D:("cmp","dx,0x9"),
 0xCEC41:("jne","0xcec4e"),
 0xCEC43:("mov","eax,0x2"),
 0xCEC48:("add","byte ptr [ecx+0xff],al")},
 "Colony_Industry_Maintenance_":{
 0xCF5BA:("mov","edx,dword ptr [edi+eax*4]"),
 0xCF5BD:("mov","eax,dword ptr [edi+eax*4]"),
 0xCF5C0:("shl","eax,0x15"),
 0xCF5C3:("shr","eax,0x1f"),
 0xCF5C6:("and","edx,0xf"),
 0xCF5CC:("cmp","dx,0x8"),
 0xCF5D0:("jge","0xcf61f"),
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
 0xCF626:("add","byte ptr [ecx+0x101],al")},
 "Convert_Player_To_Flags_":{
 0x4ADA0:("lea","ebx,[eax+0x89f]"),
 0x4ADDD:("movsx","ax,byte ptr [ecx+ebx*1]"),
 0x4ADE8:("add","eax,ecx"),
 0x4ADED:("mov","word ptr [eax*2+0x236c8],di"),
 0x4AE27:("mov","esi,0x1")},
 "Convert_Flags_To_Player_":{
 0x4AE4F:("lea","esi,[eax+0x89f]"),
 0x4AECF:("inc","eax"),
 0x4AEDB:("sub","edx,ecx"),
 0x4AEDD:("mov","bl,byte ptr [ebx*2+0x236c8]"),
 0x4AEE4:("mov","byte ptr [edx+esi*1],bl")}
}
def sha(v):return hashlib.sha256(v).hexdigest()
def food(tag,owner,bit10,flag8b0,flag8b1):
    if not (0<=tag<=15 and 0<=owner<=7):raise ValueError("source tag range")
    if tag>=8:
        return {"bucket":"FF" if tag==9 else None,"weight":2 if tag==9 else 0,"race_scratch":None}
    w=1 if flag8b0 else (0 if flag8b1 else 2)
    bucket="FC" if tag==owner else ("FE" if bit10 else "FD")
    return {"bucket":bucket,"weight":w,"race_scratch":f"0x{0x104+tag:x}"}
def industry(tag,owner,bit10,flag8b0):
    if not (0<=tag<=15 and 0<=owner<=7):raise ValueError("source tag range")
    if tag>=8:
        return {"bucket":"101" if tag==8 else None,"weight":2 if tag==8 else 0,"race_scratch":None}
    w=1 if flag8b0 else 0
    bucket="100" if tag==owner else ("103" if bit10 else "102")
    return {"bucket":bucket,"weight":w,"race_scratch":f"0x{0x10c+tag:x}"}
def source_option_array_index(player_field):
    if player_field not in (0x8B0,0x8B1):raise ValueError("only checked source field offsets")
    field_index=player_field-0x89F
    post_special_index=field_index+1
    return (0x236C8+post_special_index*2-0x236DC)//2
def fixtures():
    n=0
    for tag,owner,bit,fa,fb in product(range(16),range(8),(0,1),(0,1),(0,1)):
        f=food(tag,owner,bit,fa,fb)
        x=industry(tag,owner,bit,fa)
        if tag<8:
            assert f["weight"]==(1 if fa else (0 if fb else 2))
            assert x["weight"]==(1 if fa else 0)
            assert f["bucket"]==("FC" if tag==owner else ("FE" if bit else "FD"))
            assert x["bucket"]==("100" if tag==owner else ("103" if bit else "102"))
            assert f["race_scratch"]==f"0x{0x104+tag:x}"
            assert x["race_scratch"]==f"0x{0x10c+tag:x}"
            n+=6
        else:
            assert f["bucket"]==("FF" if tag==9 else None)
            assert x["bucket"]==("101" if tag==8 else None)
            assert f["weight"]==(2 if tag==9 else 0)
            assert x["weight"]==(2 if tag==8 else 0)
            n+=4
    assert source_option_array_index(0x8B0)==8
    assert source_option_array_index(0x8B1)==9
    n+=2
    # Source ADD BYTE is wrapping, rather than a C int accumulator.
    for total in (0,1,100,255,256,257,510,511):
        assert (total&255)==total%256
        n+=1
    return n
def audit(exe,code):
    b=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("original exe and CODE identity mismatch")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    ins_count=0;audited=[]
    for name,addr,length,digest in BODIES:
        f=fs[name]
        if (int(f["offset"]),int(f["inferred_size"]))!=(addr,length) or sha(b[addr:addr+length])!=digest:
            raise ValueError("original complete named-body source mismatch "+name)
        ins,continued=parse(code,addr,length)
        if sum(len(raw) for a,raw,op,arg in ins)!=length:
            raise ValueError("source byte decode incomplete "+name)
        lookup={a:(op,arg) for a,raw,op,arg in ins}
        for at,raw,op,arg in ins:
            if b[at:at+len(raw)]!=raw:raise ValueError("original decoded bytes differ")
        for at,want in OPS[name].items():
            if lookup.get(at)!=want:
                raise ValueError(f"original {name} {at:#x}: {lookup.get(at)} expected {want}")
        ins_count+=len(ins)
        audited.append({"name":name,"CODE_offset":hex(addr),"bytes":length,"sha256":digest,
                        "decoded_instructions":len(ins),"source_disasm_continuation_rows":len(continued),
                        "exact_opcode_checkpoints":len(OPS[name])})
    syms={(r["name"],r["segment"]):int(r["offset"]) for r in csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    for sym,expected in [("_player",0x1FF98),("_option_toggle",0x236DC)]:
        if syms.get((sym,"2"))!=expected:raise ValueError("original DATA symbol mismatch "+sym)
    cases=fixtures()
    return {"status":"source-verified-original-food-industry-counter-category-routes",
     "official_EXE_sha256":EXE_SHA,"original_CODE_sha256":CODE_SHA,
     "full_original_function_bodies":audited,"total_original_instructions_decoded":ins_count,
     "original_opcode_checkpoints":sum(len(x) for x in OPS.values()),
     "original_source_owner_population_logic":"tag = packed DWORD&0xf; bit10 = packed DWORD bit10; owner = colony BYTE+0x00; tag<8 derives weight from tag player original +0x8b0 and +0x8b1",
     "food_rule":"flag+0x8b0 => weight1; else flag+0x8b1 => weight0; else weight2. Bucket owner:FC, foreign packed bit10:FE, else FD; tag9 adds2 to FF; tag8 and tags10..15 excluded",
     "industry_rule":"flag+0x8b0 => weight1 else0. Bucket owner:100, foreign packed bit10:103, else102; tag8 adds2 to 101; tag9 and tags10..15 excluded",
     "source_original_race_option_zero_based_indexes":{"player_BYTE_0x8B0":source_option_array_index(0x8B0),"player_BYTE_0x8B1":source_option_array_index(0x8B1)},
     "bounded_source_classification_assertions":cases,
     "limits":["Source audit models per packed colonist categorical contributions, not all population loops' later maintenance gameplay or original DOS runtime",
       "The complete legal player race-option combinations or colonist tags and original saved-state witnesses remain unresolved",
       "For tag>=10, the source category contribution is absent; the source does not assert such tags legal",
       "No dynamic parity for original research-display condition or native browser game completion"]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
