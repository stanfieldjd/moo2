#!/usr/bin/env python3
"""Authenticate v1.31 gravity factor and its race-option origins from original CODE."""
import argparse,csv,hashlib,json
from pathlib import Path
from itertools import product
from audit_remaining_colony_production_callers_v131 import parse
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BODIES=[
 ("Gravity_Player_Production_Factor_",0xCDF2C,167,"a0660fd4edfd3b57bb91c406ca614e6c445ff509fb191eb5b757bdc254142200"),
 ("Convert_Player_To_Flags_",0x4AD97,161,"e84d39178d6ef63e679d205d734a991add5d774997653e3edba64b2a371f9d95"),
 ("Convert_Flags_To_Player_",0x4AE38,188,"55e168ee1847ba7de6868476a4acff3811b89d1b996c8555c0dec08666eb0fd5"),
 ("Colony_Job_Production_",0xCE280,996,"853acbdf8e5057e9ad4f3a34c7f5aa98392c668eee1568f8133995ca5d641860")
]
OPS={
 "Gravity_Player_Production_Factor_":{
 0xCDF2E:("cmp","byte ptr [eax+0x14f],0x0"),0xCDF35:("jne","0xcdfc9"),
 0xCDF3B:("cmp","dx,0x8"),0xCDF3F:("jge","0xcdfc9"),
 0xCDF45:("movsx","eax,word ptr [eax+0x2]"),
 0xCDF49:("imul","eax,eax,0x11"),
 0xCDF4C:("mov","ecx,dword ptr ds:0x1b0d4"),
 0xCDF52:("mov","al,byte ptr [ecx+eax*1+0x6]"),
 0xCDF56:("cmp","al,0x1"),0xCDF58:("jb","0xcdf65"),
 0xCDF5A:("jbe","0xcdf8b"),0xCDF5C:("cmp","al,0x2"),
 0xCDF5E:("je","0xcdfa6"),0xCDF60:("mov","eax,ebx"),
 0xCDF65:("test","al,al"),0xCDF67:("jne","0xcdfce"),
 0xCDF6C:("imul","ebx,ebx,0xea9"),
 0xCDF77:("cmp","byte ptr [ebx+eax*1+0x8a9],0x0"),
 0xCDF7F:("jne","0xcdfc9"),0xCDF81:("mov","ebx,0x3"),
 0xCDF8E:("imul","eax,eax,0xea9"),
 0xCDF9A:("cmp","byte ptr [ebx+eax*1+0x8a9],0x0"),
 0xCDFA2:("jne","0xcdf81"),0xCDFA4:("jmp","0xcdfc9"),
 0xCDFA9:("imul","eax,eax,0xea9"),
 0xCDFB5:("cmp","byte ptr [ebx+eax*1+0x8aa],0x0"),
 0xCDFBD:("jne","0xcdfc9"),0xCDFBF:("mov","ebx,0x2"),
 0xCDFC9:("mov","ebx,0x4")},
 "Convert_Player_To_Flags_":{
 0x4ADA0:("lea","ebx,[eax+0x89f]"),
 0x4ADDD:("movsx","ax,byte ptr [ecx+ebx*1]"),
 0x4ADE5:("movsx","eax,si"),0x4ADE8:("add","eax,ecx"),
 0x4ADED:("mov","word ptr [eax*2+0x236c8],di"),
 0x4ADF5:("cmp","dx,0xf"),0x4AE27:("mov","esi,0x1")},
 "Convert_Flags_To_Player_":{
 0x4AE4F:("lea","esi,[eax+0x89f]"),
 0x4AE99:("cmp","ax,0xf"),0x4AECF:("inc","eax"),
 0x4AED5:("movsx","ecx,word ptr [ebp-0x4]"),
 0x4AEDB:("sub","edx,ecx"),
 0x4AEDD:("mov","bl,byte ptr [ebx*2+0x236c8]"),
 0x4AEE4:("mov","byte ptr [edx+esi*1],bl")},
 "Colony_Job_Production_":{
 0xCE3B3:("and","eax,0xf"),
 0xCE3BB:("call","0xcdf2c"),
 0xCE3C0:("mov","edx,0x4"),
 0xCE3CA:("sub","edx,eax"),
 0xCE4A7:("movsx","eax,word ptr [ebp-0x18]"),
 0xCE4B1:("imul","eax,eax,0xfffffffb")}
}
def sha(b):return hashlib.sha256(b).hexdigest()
def factor(gravity,tag,flag_a=False,flag_b=False,colony_14f=False):
    if not 0<=tag<=9:raise ValueError("population tag out of supported bounds")
    if gravity not in (0,1,2):
        raise ValueError("source returns caller EBX for other gravity codes: unproven")
    if colony_14f or tag>=8:return 4
    if gravity==0:return 4 if flag_a else 3
    if gravity==1:return 3 if flag_a else 4
    return 4 if flag_b else 2
def option_address(player_field):
    if player_field not in (0x8A9,0x8AA):raise ValueError("only source checked fields")
    index=player_field-0x89F
    assert index in (10,11) and index<15
    a=0x236C8+2*index
    return {"player_offset":hex(player_field),
            "option_WORD_address":hex(a),
            "option_toggle_index":(a-0x236DC)//2}
def fixtures():
    checks=0;matrix=[]
    for gravity,fa,fb in product((0,1,2),(False,True),(False,True)):
        expected=(4 if fa else 3) if gravity==0 else ((3 if fa else 4) if gravity==1 else (4 if fb else 2))
        for tag in range(10):
            got=factor(gravity,tag,fa,fb)
            assert got==(4 if tag>=8 else expected)
            checks+=1
        assert factor(gravity,0,fa,fb,colony_14f=True)==4
        checks+=1
        matrix.append({"planet_gravity_BYTE":gravity,"race_8a9":fa,"race_8aa":fb,"factor":expected})
    for field,want in ((0x8A9,0),(0x8AA,1)):
        assert option_address(field)["option_toggle_index"]==want
        checks+=1
    for g,base in product((2,3,4),(-3,0,3)):
        assert -5*(4-g)*base==((-10 if g==2 else -5 if g==3 else 0)*base)
        checks+=1
    for invalid in (3,255):
        try:factor(invalid,0)
        except ValueError:checks+=1
        else:raise AssertionError("unmodeled original gravity case accepted")
    return checks,matrix
def audit(exe,code):
    b=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("canonical original executable/CODE fingerprint mismatch")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    checked=[];nins=0
    for name,start,size,digest in BODIES:
        r=fs[name]
        if (int(r["offset"]),int(r["inferred_size"]))!=(start,size) or sha(b[start:start+size])!=digest:
            raise ValueError("named source body changed "+name)
        ins,continuations=parse(code,start,size)
        mp={at:(op,arg) for at,raw,op,arg in ins}
        for at,raw,op,arg in ins:
            if b[at:at+len(raw)]!=raw:raise ValueError("decoded original bytes differ")
        for at,expected in OPS[name].items():
            if mp.get(at)!=expected:raise ValueError(f"{name} {at:#x}: {mp.get(at)} vs {expected}")
        branches=[]
        for at,raw,op,arg in ins:
            if name=="Gravity_Player_Production_Factor_" and op.startswith("j"):
                target=int(arg,16)
                if target not in mp:raise ValueError(f"gravity branch target wrong {at:#x} -> {target:#x}")
                branches.append({"from":hex(at),"to":hex(target),"opcode":op})
        nins+=len(ins)
        checked.append({"name":name,"CODE_offset":hex(start),"bytes":size,"SHA256":digest,
                        "decoded_instructions":len(ins),"decoder_continuation_rows":continuations,
                        "opcode_checks":len(OPS[name]),
                        **({"complete_original_direct_branches":branches} if branches else {})})
    syms={(r["name"],r["segment"]):int(r["offset"]) for r in csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    for k,off in [("_planet",0x1B0D4),("_player",0x1FF98),("_option_toggle",0x236DC)]:
        if syms.get((k,"2"))!=off:raise ValueError("original DATA symbol mismatch "+k)
    with (ROOT/"decompilation/game_call_edges.csv").open(newline="") as fd:
        callers=sorted(row["caller"] for row in csv.DictReader(fd)
                       if row["callee"]=="Gravity_Player_Production_Factor_")
    if callers!=["Colony_Job_Production_","Colony_Pop_Prod_Produced_"]:
        raise ValueError("source named caller inventory differs")
    rel=int.from_bytes(b[0xCE3BC:0xCE3C0],"little",signed=True)
    if b[0xCE3BB]!=0xE8 or 0xCE3C0+rel!=0xCDF2C:raise ValueError("wrong original CALL")
    tests,matrix=fixtures()
    return {"status":"source-verified-gravity-factor-and-race-option-0-1",
        "official_EXE_SHA256":EXE_SHA,"original_CODE_SHA256":CODE_SHA,
        "verified_original_function_bodies":checked,
        "decoded_instructions_across_four_bodies":nins,
        "source_opcode_checks":sum(len(x) for x in OPS.values()),
        "source_direct_named_callers":callers,
        "bounded_result_matrix":matrix,"controlled_fixture_assertions":tests,
        "source_race_option_fields":[option_address(x) for x in (0x8A9,0x8AA)],
        "normal_factor":"colony BYTE+0x14f nonzero or tag>=8 =>4; planet BYTE+0x06=0 => player+0x8a9 ? 4:3; =1 => player+0x8a9 ? 3:4; =2 => player+0x8aa ?4:2",
        "job_gravity_term":"-5*(4-factor)*per-population production base",
        "unresolved_outside_domain":"planet gravity BYTE >=3 reaches original CODE 0xcdf60 MOV EAX,EBX; no local default assignment proven",
        "limits":["Original DOS runtime not executed",
                  "All real-state constraints and user-facing option names not established",
                  "The original planet BYTE+0x06 normal range 0..2 remains to be proved globally",
                  "No native game or user-authorized rule changes"]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    data=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps(data,indent=2))
