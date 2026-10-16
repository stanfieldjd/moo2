#!/usr/bin/env python3
"""Source-authenticate null vs nonnull breakdown paths to v1.31 research output.

Checks canonical original EXE, extracted original LE CODE, seven complete
named body digests, decoded instruction identities and direct caller edges.
Controlled algebra fixtures are hypothetical, NOT an original DOS runtime test.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from audit_remaining_colony_production_callers_v131 import parse
from audit_colony_job_breakdown_dependency_v131 import model

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BODIES=[
 ("Evaluate_Screen_Input_",0xAFDEE,1038,"a0579d92fb89aea2a0809b75f01118b3a429b99966d61b683582fb62337d5ff8"),
 ("Pre_Import_Computing_",0xD1D59,198,"7aa1ea0d54d5e89f82905724eb7fc1609c1e2b9a715c828f557fb4a9224d6628"),
 ("Show_Research_Production_",0xD03C3,46,"35af9c760df4df787a67e4bcc0591c0c9d71b70291212916211269aeba5081a8"),
 ("Colony_Research_Production_",0xCFF74,1103,"8d893da4d56dcd193a65a5db6d642ea8b375543797047ed6b149db71fb201341"),
 ("Colony_Job_Production_",0xCE280,996,"853acbdf8e5057e9ad4f3a34c7f5aa98392c668eee1568f8133995ca5d641860"),
 ("Colony_Pop_Base_Prod_Produced_",0xCE22C,84,"964117fde615677bbecb22bd682edf239015961f1ef758b03b67aaec5c0e0661"),
 ("Colony_Empire_Base_Research_Produced_",0xCFE77,253,"1e72e37daea066aa98c587b71c86f1faae81775b60886693b9a3d33b8888e0f9"),
 ("Colony_Research_Per_Scientist_",0xCFDC6,177,"7d9e54a024e600115cf99d1d299806ceaf74f93c1aa95638a135b97e2efadd14"),
]
OPS={
 "Evaluate_Screen_Input_":{
    0xB009B:("cmp","ax,word ptr ds:0xaaef"),
    0xB00A4:("movsx","eax,word ptr ds:0x277a8"),
    0xB00AB:("mov","edx,0x1"),
    0xB00B0:("call","0xd03c3"),
    0xB00B5:("jmp","0xb001e"),
 },
 "Pre_Import_Computing_":{
   0xD1DFD:("xor","edx,edx"),
   0xD1DFF:("call","0xcff74"),
 },
 "Show_Research_Production_":{
   0xD03C4:("enter","0xbb8,0x0"),
   0xD03D6:("lea","edx,[ebp-0xbb8]"),
   0xD03DC:("call","0xcff74"),
   0xD03E1:("lea","edx,[ebp-0xbb8]"),
   0xD03EC:("jmp","0xcdf24"),
 },
 "Colony_Research_Production_":{
   0xCFF7E:("mov","edi,edx"),
   0xCFF80:("cmp","byte ptr [eax+0xa],0x0"),
   0xCFF8F:("jmp","0xceb17"),
   0xCFFB6:("test","edi,edi"),
   0xCFFB8:("je","0xceb17"),
   0xCFFD3:("test","edi,edi"),
   0xCFFD5:("je","0xcffdf"),
   0xCFFD7:("lea","ebx,[ebp-0x264]"),
   0xCFFDF:("xor","ebx,ebx"),
   0xCFFE1:("mov","edx,0x2"),
   0xCFFE8:("call","0xce280"),
   0xCFFED:("movsx","edx,ax"),
   0xD0050:("mov","word ptr [esi+0xeb],dx"),
   0xD0057:("test","edi,edi"),
   0xD0059:("je","0xceb17"),
 },
 "Colony_Job_Production_":{
   0xCE28C:("mov","dword ptr [ebp-0x24],ebx"),
   0xCE3D7:("lea","eax,[ebp-0x4d4]"),
   0xCE3DD:("call","0x119c70"),
   0xCE3E2:("cmp","dword ptr [ebp-0x24],0x0"),
   0xCE3E6:("je","0xce3f0"),
   0xCE3E8:("lea","ecx,[ebp-0x4d4]"),
   0xCE3F0:("xor","ecx,ecx"),
   0xCE3FA:("call","0xce22c"),
   0xCE609:("add","eax,dword ptr [ebp-0x2ae]"),
   0xCE617:("test","edx,edx"),
   0xCE619:("jle","0xce61e"),
   0xCE61B:("add","dword ptr [ebp-0x2a],edx"),
 },
 "Colony_Pop_Base_Prod_Produced_":{
   0xCE24E:("call","dword ptr [edi*4+0xb55c]"),
 },
 "Colony_Empire_Base_Research_Produced_":{
   0xCFE8E:("test","ecx,ecx"),
   0xCFE90:("jne","0xcfe9b"),
   0xCFE9F:("mov","ebx,ecx"),
   0xCFEA3:("call","0xcfdc6"),
 },
 "Colony_Research_Per_Scientist_":{
   0xCFE46:("cmp","al,0xa"),
   0xCFE4E:("je","0xcfe65"),
   0xCFE54:("inc","edx"),
   0xCFE55:("inc","edx"),
   0xCFE56:("test","ebx,ebx"),
   0xCFE58:("je","0xcfe73"),
   0xCFE5A:("add","dword ptr [ebx+0x226],0x2"),
   0xCFE65:("add","edx,0x5"),
   0xCFE68:("test","ebx,ebx"),
   0xCFE6A:("je","0xcfe73"),
   0xCFE6C:("add","dword ptr [ebx+0x226],0x5"),
 },
}
def sha(v):
    return hashlib.sha256(v).hexdigest()

def controlled():
    checks=0
    cases=[]
    for planet in (0,10,11):
        for caller,breakdown in (("Pre_Import_Computing_",False),
                                 ("Show_Research_Production_",True)):
            found=model(planet_byte_f=planet,breakdown_enabled=breakdown)
            cases.append({"caller":caller,"planet_byte_0f":planet,**found})
            expected_inherited=(2 if planet==10 else 5 if planet==11 else 0) if breakdown else 0
            assert found["nested_breakdown_plus_226"]==expected_inherited
            checks+=1
        base,show=cases[-2:]
        assert base["base"]==show["base"]
        checks+=1
    for planet,expected in [(0,(0,0)),(10,(0,1)),(11,(0,1))]:
        sub=[x for x in cases if x["planet_byte_0f"]==planet]
        assert tuple(x["final_signed_job_output"] for x in sub)==expected
        checks+=1
    assert (0x4d4-0x226)==0x2ae
    checks+=1
    return checks,cases

def audit(exe,code):
    b=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("canonical original executable/CODE mismatch")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    bodies=[];maps={};instructions=0;opchecks=0
    for name,at,size,digest in BODIES:
        r=fs[name]
        if (int(r["offset"]),int(r["inferred_size"]))!=(at,size) or sha(b[at:at+size])!=digest:
            raise ValueError("Original body mismatch: "+name)
        # Evaluate_Screen_Input_ contains a region the generic linear decoder
        # cannot classify contiguously. Authenticate the *whole* named body's
        # bytes above, and decode only its exact UI CALL-site block here.
        scope_offset,scope_size=(0xB009B,0xB00BA-0xB009B) if name=="Evaluate_Screen_Input_" else (at,size)
        ins,continuations=parse(code,scope_offset,scope_size)
        for address,raw,op,arg in ins:
            if b[address:address+len(raw)]!=raw:
                raise ValueError(f"Decoder mismatch {address:#x}")
        mp={address:(op,arg) for address,raw,op,arg in ins}
        for address,expect in OPS[name].items():
            if mp.get(address)!=expect:
                raise ValueError(f"Anchor {name} {address:#x}: {mp.get(address)} != {expect}")
        maps[name]=mp
        instructions+=len(ins);opchecks+=len(OPS[name])
        bodies.append({"name":name,"CODE_offset":hex(at),"bytes":size,
                  "SHA256":digest,"instructions":len(ins),"byte_continuations":continuations,
                  "scope_decoded":("UI source CALL block only" if name=="Evaluate_Screen_Input_" else "entire named function"),
                  "cross_route_opcode_checks":len(OPS[name])})
    edges=[
        ("Evaluate_Screen_Input_",0xB00B0,"Show_Research_Production_"),
        ("Pre_Import_Computing_",0xD1DFF,"Colony_Research_Production_"),
        ("Show_Research_Production_",0xD03DC,"Colony_Research_Production_"),
        ("Colony_Research_Production_",0xCFFE8,"Colony_Job_Production_"),
        ("Colony_Job_Production_",0xCE3FA,"Colony_Pop_Base_Prod_Produced_"),
        ("Colony_Empire_Base_Research_Produced_",0xCFEA3,"Colony_Research_Per_Scientist_"),
    ]
    destinations={name:at for name,at,_,_ in BODIES}
    for caller,site,callee in edges:
        if maps[caller][site]!=("call",hex(destinations[callee])):
            raise ValueError("Source CALL route identity changed")
    # The only directly named callers in the original linker call graph;
    # indirect calls are separately identified through the DATA table.
    with (ROOT/"decompilation/game_call_edges.csv").open(newline="") as f:
        callers=sorted({r["caller"] for r in csv.DictReader(f)
                        if r["callee"]=="Colony_Research_Production_"})
    if callers!=sorted(["Pre_Import_Computing_","Show_Research_Production_"]):
        raise ValueError("Original direct caller inventory changed")
    n,fixtures=controlled()
    return {
        "status":"source-verified-null-vs-display-research-production-caller-routes",
        "official_EXE_SHA256":EXE_SHA,"LE_CODE_SHA256":CODE_SHA,
        "verified_original_bodies":bodies,
        "decoded_original_instructions_across_verified_scopes":instructions,
        "UI_screen_input_body_decode_limit":"Only 0xb009b..0xb00b9 CALL-site instructions decoded, entire 1038 bytes source-hashed",
        "source_cross_function_opcode_checks":opchecks,
        "direct_caller_inventory":callers,
        "verified_named_direct_call_edges":[{"caller":a,"CODE_site":hex(site),"callee":b}
                                             for a,site,b in edges],
        "indirect_research_dispatch":"DATA _colony_empire_base_functions at 0xb55c, selector 2 -> CODE 0xcfe77",
        "non_null_route":"Evaluate_Screen_Input_ UI branch CALL Show_Research_Production_ -> nonnull Show stack LEA EDX -> Research EDI -> local EBX -> Job EBX -> temporary ECX -> Scientist EBX",
        "null_route":"Pre_Import_Computing_ XOR EDX,EDX -> Research EDI=0 -> Job EBX=0 -> temporary ECX=0 -> Scientist EBX=0",
        "source_numeric_output_write":"Colony_Research_Production_ writes WORD colony+0xeb after Job_Production_ result, regardless of output pointer on normal path",
        "verified_alias":"EBP-0x4d4+0x226 = EBP-0x2ae",
        "controlled_fixture_checks":n,"controlled_examples":fixtures,
        "remaining_obligations":[
             "No original DOS runtime differential execution",
             "Valid original save-state reachability for synthetic values unproved",
             "Original named callgraph does not eliminate unknown indirect callers",
             "No user-authorized balance behavior changes, so no remediation is proposed",
        ],
    }
if __name__=="__main__":
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--exe",required=True,type=Path)
    a.add_argument("--code",required=True,type=Path)
    a.add_argument("--output",type=Path)
    x=a.parse_args()
    r=audit(x.exe,x.code)
    if x.output:x.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
