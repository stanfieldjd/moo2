#!/usr/bin/env python3
"""Authenticate original v1.31 homeworld balance field producer/consumer chain.

Full official original function bodies, exact decoder/instruction anchors,
source direct call sites and controlled signed WORD/unsigned BYTE checks.
No dynamic original game execution or frozen-state engine parity asserted.
"""
import argparse,csv,hashlib,json
from itertools import product
from pathlib import Path
from audit_remaining_colony_production_callers_v131 import parse
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BODIES=[
 ("Pre_Import_Computing_",0xD1D59,198,"7aa1ea0d54d5e89f82905724eb7fc1609c1e2b9a715c828f557fb4a9224d6628"),
 ("Pass_Out_Imports_",0xCF8F0,1238,"e35af6d4ee3106edd7af2f4f6377a18453e107323c620993b3f577871eff4234"),
 ("Colony_Food2_Per_Farmer_",0xCE03E,136,"6aef5f245db959b949a22eb0cfccd03b65db2c103a18c4dc47f5bbabcf9a04e4"),
 ("Colony_Food_Production_",0xCE664,1209,"cfd054077a2fa2a0b676a7cda660388de06c3b63a46f8a3f516bc5e245555aac"),
 ("Colony_Industry_Production_",0xCEE1B,1789,"e68780a7e7632b271363fa37540d0428dd0c57c20ac173ac1ccee4ebe9e45f1d"),
 ("Colony_Research_Production_",0xCFF74,1103,"8d893da4d56dcd193a65a5db6d642ea8b375543797047ed6b149db71fb201341"),
 ("Twiddle_Initial_Homeworld_",0xD55BE,530,"63231cd00c846d3dc955e8144437ae7deb45d76525ee8d52866b275a2173e891")]
OP={
 "Pre_Import_Computing_":{
  0xD1D5E:("mov","ebx,0x4"),
  0xD1D63:("add","eax,0xef"),
  0xD1D68:("xor","edx,edx"),
  0xD1D6A:("call","0x119c70"),
  0xD1D76:("call","0xce03e"),
  0xD1D7B:("mov","byte ptr [ecx+0xdd],al"),
  0xD1D8F:("call","0xcec95"),
  0xD1D99:("mov","byte ptr [ecx+0xde],al"),
  0xD1DA1:("call","0xcfdc6"),
  0xD1DA8:("mov","byte ptr [ecx+0xdf],al"),
  0xD1DC0:("call","0xcee1b"),
  0xD1DC9:("call","0xce664"),
  0xD1DDC:("movzx","ax,byte ptr [ecx+0xf0]"),
  0xD1DE4:("cmp","ax,word ptr [ecx+0xe9]"),
  0xD1DEB:("jl","0xd1df4"),
  0xD1DED:("mov","ax,word ptr [ecx+0xe9]"),
  0xD1DF4:("mov","word ptr [ecx+0xf5],ax"),
  0xD1DFD:("xor","edx,edx"),
  0xD1DFF:("call","0xcff74")},
 "Pass_Out_Imports_":{
  0xCF978:("movzx","ax,byte ptr [ecx+0xef]"),
  0xCF980:("mov","dx,word ptr [ecx+0xe7]"),
  0xCF9A0:("mov","word ptr [ecx+0xf3],0x0"),
  0xCF9E9:("mov","word ptr [ecx+0xf3],dx"),
  0xCF9F8:("neg","word ptr [ecx+0xf3]"),
  0xCFA72:("sub","si,word ptr [eax+0xe7]"),
  0xCFA7A:("mov","word ptr [eax+0xf3],si"),
  0xCFCCF:("movsx","edx,word ptr [eax+0xe7]"),
  0xCFCE2:("movzx","edx,byte ptr [eax+0xef]")},
 "Colony_Food2_Per_Farmer_":{},
 "Colony_Food_Production_":{
  0xCE676:("mov","word ptr [eax+0xe7],0x0"),
  0xCE69D:("mov","word ptr [esi+0xe7],0x0"),
  0xCE6C9:("cmp","byte ptr [esi+0xdd],0x0"),
  0xCE727:("mov","word ptr [esi+0xe7],bx"),
  0xCEAE4:("add","word ptr [esi+0xe7],ax")},
 "Colony_Industry_Production_":{
  0xCEE3C:("mov","word ptr [eax+0xe9],0x0"),
  0xCEE63:("mov","word ptr [esi+0xe9],0x0"),
  0xCF0F0:("mov","word ptr [esi+0xe9],ax"),
  0xCF4A3:("sub","word ptr [esi+0xe9],ax"),
  0xCF4D9:("sub","word ptr [esi+0xe9],ax")},
 "Colony_Research_Production_":{
  0xCFF86:("mov","word ptr [eax+0xeb],0x0"),
  0xCFFAD:("mov","word ptr [esi+0xeb],0x0"),
  0xD0050:("mov","word ptr [esi+0xeb],dx")},
 "Twiddle_Initial_Homeworld_":{
  0xD561A:("call","0xd1d59"),
  0xD5626:("call","0xcf8f0"),
  0xD5637:("cmp","ax,word ptr [ebx+0xe9]"),
  0xD564C:("call","0xd1d59"),
  0xD566E:("cmp","ax,word ptr [ebx+0xe7]"),
  0xD567E:("call","0xd1d59"),
  0xD568B:("call","0xcf8f0"),
  0xD569D:("cmp","ax,word ptr [ebx+0xeb]"),
  0xD56B2:("call","0xd1d59"),
  0xD56BD:("call","0xcf8f0"),
  0xD56CB:("cmp","ax,word ptr [ebx+0xe9]"),
  0xD56E4:("call","0xd1d59"),
  0xD56EC:("call","0xcf8f0")}
}
CALLS=[
 ("Pre_Import_Computing_",0xD1D76,"Colony_Food2_Per_Farmer_"),
 ("Pre_Import_Computing_",0xD1DC0,"Colony_Industry_Production_"),
 ("Pre_Import_Computing_",0xD1DC9,"Colony_Food_Production_"),
 ("Pre_Import_Computing_",0xD1DFF,"Colony_Research_Production_"),
 ("Twiddle_Initial_Homeworld_",0xD561A,"Pre_Import_Computing_"),
 ("Twiddle_Initial_Homeworld_",0xD5626,"Pass_Out_Imports_"),
 ("Twiddle_Initial_Homeworld_",0xD564C,"Pre_Import_Computing_"),
 ("Twiddle_Initial_Homeworld_",0xD567E,"Pre_Import_Computing_"),
 ("Twiddle_Initial_Homeworld_",0xD568B,"Pass_Out_Imports_"),
 ("Twiddle_Initial_Homeworld_",0xD56B2,"Pre_Import_Computing_"),
 ("Twiddle_Initial_Homeworld_",0xD56BD,"Pass_Out_Imports_"),
 ("Twiddle_Initial_Homeworld_",0xD56E4,"Pre_Import_Computing_"),
 ("Twiddle_Initial_Homeworld_",0xD56EC,"Pass_Out_Imports_")]
def sha(data):return hashlib.sha256(data).hexdigest()
def s16(x):
    if not 0<=x<=65535:raise ValueError("original WORD range")
    return x if x<32768 else x-65536
def capped_industry_byte(f0,e9):
    """Source WORD +f5 = signed min(zero-extended BYTE+f0, signed WORD+e9)."""
    if not 0<=f0<=255:raise ValueError("original BYTE out of range")
    return (min(f0,s16(e9)))&65535
def fixtures():
    cases=0
    for supply,ind in product(range(256),(0,1,99,255,256,32767,32768,65535)):
        actual=capped_industry_byte(supply,ind)
        assert actual in range(65536)
        assert s16(actual)==min(supply,s16(ind))
        cases+=2
    # Carefully differentiate signed vs unsigned: WORD 0xffff => -1.
    assert capped_industry_byte(12,0xFFFF)==0xFFFF
    assert capped_industry_byte(12,0x8000)==0x8000
    assert capped_industry_byte(12,0x7FFF)==12
    cases+=3
    return cases
def audit(exe,code):
    b=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("canonical original executable or Watcom CODE changed")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    full=[];lookups={};ins_count=0
    for name,addr,length,digest in BODIES:
        f=fs[name]
        if (int(f["offset"]),int(f["inferred_size"]))!=(addr,length) or sha(b[addr:addr+length])!=digest:
            raise ValueError("Original full named-body identity mismatch "+name)
        ins,continued=parse(code,addr,length)
        if sum(len(raw) for a,raw,op,arg in ins)!=length:
            raise ValueError("Original named-body instruction coverage incomplete "+name)
        m={a:(op,arg) for a,raw,op,arg in ins}
        for a,raw,op,arg in ins:
            if b[a:a+len(raw)]!=raw:raise ValueError("Original source decode differs")
        for a,want in OP[name].items():
            if m.get(a)!=want:raise ValueError(f"Source opcode {name} {a:#x} {m.get(a)} != {want}")
        ins_count+=len(ins);lookups[name]=m
        full.append({"name":name,"CODE_offset":hex(addr),"bytes":length,"SHA256":digest,
          "fully_decoded_original_instructions":len(ins),"disassembly_continuation_rows":len(continued),
          "original_opcode_anchors":len(OP[name])})
    with (ROOT/"decompilation/game_call_edges.csv").open(newline="") as f:
        edges={(r["caller"],r["callee"]) for r in csv.DictReader(f)}
    for caller,site,callee in CALLS:
        dest=int(fs[callee]["offset"])
        if (caller,callee) not in edges or lookups[caller].get(site)!=("call",hex(dest)):
            raise ValueError("Original direct named CALL site differs "+caller+" -> "+callee)
        if b[site]!=0xE8 or site+5+int.from_bytes(b[site+1:site+5],"little",signed=True)!=dest:
            raise ValueError("Original direct machine CALL displacement differs")
    testcount=fixtures()
    return {"status":"source-verified-homeworld-rebalance-food-industry-research-producers",
      "canonical_EXE_SHA256":EXE_SHA,"original_LE_CODE_SHA256":CODE_SHA,
      "complete_source_original_bodies":full,
      "source_instruction_count":ins_count,
      "exact_opcode_site_checks":sum(map(len,OP.values())),
      "source_direct_named_CALL_count":len(CALLS),
      "producer_routes":{
        "colony_BYTE_0xDD":"Pre_Import_Computing_ directly CALLs Colony_Food2_Per_Farmer_ at CODE 0xd1d76, stores AL at 0xd1d7b; Colony_Food_Production_ checks this original byte at CODE 0xce6c9",
        "colony_WORD_0xE7":"Colony_Food_Production_ writes original food result in WORD+0xe7 (0xce676,0xce69d,0xce727,0xceae4)",
        "colony_WORD_0xE9":"Colony_Industry_Production_ writes original industry result WORD+0xe9 (0xcee3c,0xcee63,0xcf0f0,0xcf4a3,0xcf4d9)",
        "colony_WORD_0xEB":"Colony_Research_Production_ writes original research result WORD+0xeb (0xcff86,0xcffad,0xd0050)",
        "colony_WORD_0xF5":"Pre_Import_Computing_ calculates source signed-16 minimum of zero-extended BYTE+0xf0 and WORD+0xe9 after industry and food production, CODE 0xd1ddc..0xd1df4",
        "colony_WORD_0xF3":"Pass_Out_Imports_ reads food BYTE+0xef and WORD+0xe7 then conditionally writes or adjusts WORD+0xf3, including 0xcf9a0, 0xcf9e9, 0xcf9f8, 0xcfa7a and later adjustment sites"},
      "source_original_pre_import_CALL_order":["Colony_Food2_Per_Farmer_","Colony_Industry_Production_","Colony_Food_Production_","Colony_Research_Production_"],
      "bounded_signed_saturation_assertions":testcount,
      "limitations":[
        "Other original calls inside Pre_Import_Computing_ are not asserted pure; +0xf0 writer may be through additional nested calls or aliases",
        "Input fields are mutated and recomputed between multiple Twiddle_Initial_Homeworld_ stages, so no static final population-job distribution or runtime totals are claimed",
        "No original DOS dynamic savegame differential or research display bug established",
        "No native browser game implementation or whole executable completion percentage recalculated"]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
