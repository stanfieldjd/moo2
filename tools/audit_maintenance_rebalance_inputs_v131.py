#!/usr/bin/env python3
"""Original v1.31 colony food/industry/BC maintenance -> worker balance inputs.

Source-backed exact function hashes, complete contiguous original x86 decode,
original direct calls and bounded byte-array arithmetic; no DOS execution,
no savegame reachability or unrestricted native parity claims.
"""
import argparse,csv,hashlib,json
from itertools import product
from pathlib import Path
from audit_remaining_colony_production_callers_v131 import parse
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BODIES=[
 ("memset_",0x119C70,24,"e1bb125f736118af8cb392e308cbf68630169cada23d288f5adad0c3eb4fdc8c"),
 ("Colony_Food_Maintenance_",0xCEB4B,330,"005961c516ea2f30e4534b7e7c5eb4ede279dc9c53d89a49fd2f5214b5f84030"),
 ("Colony_Industry_Maintenance_",0xCF546,297,"a3d24386fbaa9dfe229d88dcb34c2c661f3dc2169cdec44481c558542e0fb0ed"),
 ("Colony_BC_Maintenance_",0xD094F,197,"2a9e964cfbd9c9068ba9998f3d4e8c55ddc39bb4546107fc097a915b6133bfe5"),
 ("Pre_Import_Computing_",0xD1D59,198,"7aa1ea0d54d5e89f82905724eb7fc1609c1e2b9a715c828f557fb4a9224d6628"),
 ("Twiddle_Initial_Homeworld_",0xD55BE,530,"63231cd00c846d3dc955e8144437ae7deb45d76525ee8d52866b275a2173e891"),
 ("Pass_Out_Imports_",0xCF8F0,1238,"e35af6d4ee3106edd7af2f4f6377a18453e107323c620993b3f577871eff4234"),
]
OPS={
 "memset_":{
  0x119C72:("mov","dh,dl"),
  0x119C7E:("mov","ecx,ebx"),
  0x119C80:("call","0x138220"),
  0x119C87:("ret","")},
 "Colony_Food_Maintenance_":{
  0xCEB6E:("call","0x1341e"),
  0xCEB73:("test","ax,ax"),
  0xCEB78:("mov","byte ptr [ecx+0xef],0x0"),
  0xCEB84:("mov","ebx,0x8"),
  0xCEB89:("lea","eax,[ecx+0x104]"),
  0xCEB8F:("xor","edx,edx"),
  0xCEB91:("call","0x119c70"),
  0xCEC5D:("movzx","dx,byte ptr [ecx+0xfc]"),
  0xCEC65:("movzx","ax,byte ptr [ecx+0xff]"),
  0xCEC6F:("movzx","ax,byte ptr [ecx+0xfe]"),
  0xCEC79:("movzx","dx,byte ptr [ecx+0xfd]"),
  0xCEC84:("inc","eax"),
  0xCEC88:("sar","eax,1"),
  0xCEC8A:("mov","byte ptr [ecx+0xef],al")},
 "Colony_Industry_Maintenance_":{
  0xCF569:("call","0x1341e"),
  0xCF573:("mov","byte ptr [ecx+0xf0],0x0"),
  0xCF57F:("mov","ebx,0x8"),
  0xCF584:("lea","eax,[ecx+0x10c]"),
  0xCF58A:("xor","edx,edx"),
  0xCF58C:("call","0x119c70"),
  0xCF637:("movzx","dx,byte ptr [ecx+0x100]"),
  0xCF63F:("movzx","ax,byte ptr [ecx+0x101]"),
  0xCF649:("movzx","ax,byte ptr [ecx+0x103]"),
  0xCF653:("movzx","ax,byte ptr [ecx+0x102]"),
  0xCF65D:("cwde",""),
  0xCF65E:("inc","eax"),
  0xCF662:("sar","eax,1"),
  0xCF664:("mov","byte ptr [ecx+0xf0],al")},
 "Colony_BC_Maintenance_":{
  0xD095A:("cmp","byte ptr [eax+0xa],0x0"),
  0xD0960:("mov","byte ptr [eax+0xf2],0x0"),
  0xD0985:("mov","byte ptr [ebx+0xf2],0x0"),
  0xD09F1:("mov","byte ptr [ebx+0xf2],al"),
  0xD09F7:("movzx","ax,byte ptr [ebx+0xf2]")},
 "Pre_Import_Computing_":{
  0xD1D5E:("mov","ebx,0x4"),
  0xD1D63:("add","eax,0xef"),
  0xD1D68:("xor","edx,edx"),
  0xD1D6A:("call","0x119c70"),
  0xD1DB7:("call","0xcf546"),
  0xD1DC0:("call","0xcee1b"),
  0xD1DC9:("call","0xce664"),
  0xD1DD0:("call","0xceb4b"),
  0xD1DD7:("call","0xcf66f"),
  0xD1DDC:("movzx","ax,byte ptr [ecx+0xf0]"),
  0xD1DE4:("cmp","ax,word ptr [ecx+0xe9]"),
  0xD1DF4:("mov","word ptr [ecx+0xf5],ax"),
  0xD1DFF:("call","0xcff74"),
  0xD1E16:("call","0xd094f")},
 "Twiddle_Initial_Homeworld_":{
  0xD561A:("call","0xd1d59"),
  0xD5626:("call","0xcf8f0"),
  0xD562F:("movzx","ax,byte ptr [ebx+0xf0]"),
  0xD5637:("cmp","ax,word ptr [ebx+0xe9]"),
  0xD5666:("movzx","ax,byte ptr [ebx+0xef]"),
  0xD566E:("cmp","ax,word ptr [ebx+0xe7]")},
 "Pass_Out_Imports_":{
  0xCF978:("movzx","ax,byte ptr [ecx+0xef]"),
  0xCF980:("mov","dx,word ptr [ecx+0xe7]"),
  0xCFA6A:("movzx","si,byte ptr [eax+0xef]"),
  0xCFCE2:("movzx","edx,byte ptr [eax+0xef]")}
}
DIRECT=[
 ("Pre_Import_Computing_",0xD1D6A,"memset_"),
 ("Pre_Import_Computing_",0xD1DB7,"Colony_Industry_Maintenance_"),
 ("Pre_Import_Computing_",0xD1DD0,"Colony_Food_Maintenance_"),
 ("Pre_Import_Computing_",0xD1E16,"Colony_BC_Maintenance_"),
 ("Colony_Industry_Maintenance_",0xCF58C,"memset_"),
 ("Colony_Food_Maintenance_",0xCEB91,"memset_"),
 ("Twiddle_Initial_Homeworld_",0xD561A,"Pre_Import_Computing_"),
 ("Twiddle_Initial_Homeworld_",0xD5626,"Pass_Out_Imports_")]
def sha(b):return hashlib.sha256(b).hexdigest()
def rounded_half_byte(counters):
    """The original post-counter CWDE;INC;CDQ;SUB;SAR1;store-AL path.

    All four nonnegative BYTE counters sum <=1020; signed 16-bit sign is 0.
    """
    if len(counters)!=4 or any(not isinstance(x,int) or not 0<=x<=255 for x in counters):
        raise ValueError("four source BYTE counters required")
    return ((sum(counters)+1)//2)&255
def fixtures():
    count=0
    samples=(0,1,2,7,127,128,254,255)
    for vals in product(samples,repeat=4):
        original=(sum(vals)+1)//2
        got=rounded_half_byte(vals)
        assert got==(original&255)
        assert 0<=got<=255
        count+=2
    for vals,expected in [
        ((0,0,0,0),0),((1,0,0,0),1),((1,1,0,0),1),
        ((0,0,1,0),1),((255,0,0,0),128),
        ((255,255,255,255),254),((255,255,0,0),255),
        ((255,255,1,0),0)]:
        assert rounded_half_byte(vals)==expected
        count+=1
    return count
def audit(exe,code):
    b=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("original official executable/code identity mismatch")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    bodies=[];decoder={};all_count=0
    for name,at,length,digest in BODIES:
        r=fs[name]
        if (int(r["offset"]),int(r["inferred_size"]))!=(at,length) or sha(b[at:at+length])!=digest:
            raise ValueError("original named function extent or body hash differs "+name)
        instructions,continuations=parse(code,at,length)
        if sum(len(raw) for a,raw,op,arg in instructions)!=length:
            raise ValueError("original named function not fully decoded "+name)
        m={a:(op,arg) for a,raw,op,arg in instructions}
        for a,raw,op,arg in instructions:
            if b[a:a+len(raw)]!=raw:
                raise ValueError("machine-code bytes do not match original")
        for addr,want in OPS[name].items():
            if m.get(addr)!=want:
                raise ValueError(f"source opcode mismatch: {name} {addr:#x} {m.get(addr)} != {want}")
        decoder[name]=m;all_count+=len(instructions)
        bodies.append({"name":name,"CODE_offset":hex(at),"original_bytes":length,
                       "sha256":digest,"decoded_instructions":len(instructions),
                       "recombined_continuation_rows":len(continuations),
                       "exact_opcode_checks":len(OPS[name])})
    with (ROOT/"decompilation/game_call_edges.csv").open(newline="") as f:
        edges={(r["caller"],r["callee"]) for r in csv.DictReader(f)}
    for caller,at,dest in DIRECT:
        # The project index lists original game-to-game edges, but does not
        # include original Watcom RTL memset_ calls. Those remain provable
        # directly from source CALL bytes and target body hashes.
        if dest!="memset_" and (caller,dest) not in edges:
            raise ValueError("game-to-game named original callgraph mismatch")
        addr=int(fs[dest]["offset"])
        if decoder[caller].get(at)!=("call",hex(addr)):
            raise ValueError(f"original source CALL mismatch {caller} {at:#x}")
        if b[at]!=0xE8 or at+5+int.from_bytes(b[at+1:at+5],"little",signed=True)!=addr:
            raise ValueError("raw original x86 CALL displacement mismatch")
    fixtures_count=fixtures()
    return {
        "status":"original-source-verified-maintenance-byte-producers-and-homeworld-rebalance-inputs",
        "original_EXE_sha256":EXE_SHA,"original_CODE_sha256":CODE_SHA,
        "fully_authenticated_source_functions":bodies,
        "original_instructions_fully_decoded":all_count,
        "opcode_anchors_verified":sum(len(x) for x in OPS.values()),
        "named_direct_CALL_edges_verified":len(DIRECT),
        "source_reset":"Pre_Import_Computing_ passes EAX=colony+0xef, EBX=4, EDX=0 to named memset_ at CODE 0xd1d6a. memset_ passes count in ECX to original helper 0x138220",
        "food_byte_0xEF":"Colony_Food_Maintenance_ clears eight bytes at colony+0x104, counts four counters colony+0xfc..0xff, then stores low BYTE ceil(sum/2) at CODE 0xcec8a (anomaly branch stores 0 at 0xceb78)",
        "industry_byte_0xF0":"Colony_Industry_Maintenance_ clears eight bytes at colony+0x10c, counts four counters colony+0x100..0x103, then stores low BYTE ceil(sum/2) at CODE 0xcf664 (anomaly branch stores 0 at 0xcf573)",
        "bc_byte_0xF2":"Colony_BC_Maintenance_ writes colony BYTE+0xf2 in source zero and computed branches; original CODE 0xd0960,0xd0985,0xd09f1",
        "source_call_order":"Pre_Import_Computing_: reset EF..F2, then industry maintenance before industry production, food production before food maintenance, replicators, industry cap and research production, then BC maintenance",
        "original_consumers":"Twiddle_Initial_Homeworld_ reads BYTE+0xf0 and BYTE+0xef at 0xd562f and 0xd5666; Pass_Out_Imports_ reads food BYTE+0xef at 0xcf978,0xcfa6a,0xcfce2",
        "controlled_byte_rounding_assertions":fixtures_count,
        "limits":[
            "The source rounds four nonnegative counters up to half, then stores only the low BYTE: larger synthetic sums can wrap modulo 256; real counter-value reachability not proven",
            "Original helper 0x138220 and counter accumulation semantics outside named maintenance summaries are not fully independently audited here",
            "Per-colony import and maintenance calls mutate fields between job-assignment comparisons",
            "No final original DOS game-state worker distribution or runtime research discrepancy proven",
            "Native browser game, original executable coverage percentage and whole save-state parity remain incomplete",
        ],
    }
if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe",required=True,type=Path)
    ap.add_argument("--code",required=True,type=Path)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    r=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
