#!/usr/bin/env python3
"""Source-verified static cross-call trace: optional breakdown vs job total.

Does NOT assert a reproduced DOS gameplay defect. Authenticates all four
original body hashes and selected cross-function instructions. Uses controlled
fixtures solely to show a possible difference under explicit assumptions.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from audit_remaining_colony_production_callers_v131 import parse
from audit_colony_job_worker_modifiers_v131 import selected_job_worker_stage
from audit_colony_empire_base_formulas_v131 import scientist
from audit_colony_job_production_v131 import selected_final_arithmetic

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BODIES=[
 ("Colony_Job_Production_",0xCE280,996,"853acbdf8e5057e9ad4f3a34c7f5aa98392c668eee1568f8133995ca5d641860"),
 ("Colony_Pop_Base_Prod_Produced_",0xCE22C,84,"964117fde615677bbecb22bd682edf239015961f1ef758b03b67aaec5c0e0661"),
 ("Colony_Empire_Base_Research_Produced_",0xCFE77,253,"1e72e37daea066aa98c587b71c86f1faae81775b60886693b9a3d33b8888e0f9"),
 ("Colony_Research_Per_Scientist_",0xCFDC6,177,"7d9e54a024e600115cf99d1d299806ceaf74f93c1aa95638a135b97e2efadd14")]
# Exact original multi-function data-flow proof. Original source uses the
# Watcom fastcall register convention (pointer ECX at CE3FA), not a C ABI.
OPS={
 0xCE3C5:("mov","ebx,0x256"),
 0xCE3D5:("xor","edx,edx"),
 0xCE3D7:("lea","eax,[ebp-0x4d4]"),
 0xCE3DD:("call","0x119c70"),
 0xCE3E2:("cmp","dword ptr [ebp-0x24],0x0"),
 0xCE3E6:("je","0xce3f0"),
 0xCE3E8:("lea","ecx,[ebp-0x4d4]"),
 0xCE3F0:("xor","ecx,ecx"),
 0xCE3FA:("call","0xce22c"),
 0xCE467:("mov","eax,dword ptr [ebp-0x2ae]"),
 0xCE46D:("add","dword ptr [ebp-0x56],eax"),
 0xCE609:("add","eax,dword ptr [ebp-0x2ae]"),
 0xCE617:("test","edx,edx"),
 0xCE619:("jle","0xce61e"),
 0xCE61B:("add","dword ptr [ebp-0x2a],edx"),
 0xCE24E:("call","dword ptr [edi*4+0xb55c]"),
 0xCFE8E:("test","ecx,ecx"),
 0xCFE90:("jne","0xcfe9b"),
 0xCFE9F:("mov","ebx,ecx"),
 0xCFEA3:("call","0xcfdc6"),
 0xCFEF9:("xor","edx,edx"),
 0xCFDCC:("test","ebx,ebx"),
 0xCFDD0:("mov","dword ptr [ebx],0x3"),
 0xCFE42:("mov","al,byte ptr [ecx+eax*1+0xf]"),
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
}

def sha(x):return hashlib.sha256(x).hexdigest()

def model(*,planet_byte_f,breakdown_enabled,setting_idx=6,selected_player_byte_28=90):
    """Synthetic one-population research example, fresh independent caches.

    Controller assumes tag != owner, eligible packed job-2 entry, no source
    per-player +0x8a3, race/leader/morale flags, gravity factor 2, government
    group 0, and a zero-initialized breakdown. These are assumptions, NOT an
    observed valid savegame.
    """
    if planet_byte_f not in (0,10,11):raise ValueError("only synthetic planet cases")
    produced=scientist(planet_byte_f,{},breakdown=breakdown_enabled)
    base=produced["return"]
    inherited=(produced["writes"].get(0x226,("",0))[1] if breakdown_enabled else 0)
    stage=selected_job_worker_stage(job=2,tag=0,production_base=base,
      gravity_factor=2,government_group=0,
      settings_index=setting_idx,player_byte_28=selected_player_byte_28,
      inherited_component=inherited)
    value=selected_final_arithmetic(stage["total_addition_if_positive"],2)
    return {"base":base,"nested_breakdown_plus_226":inherited,
            "raw_worker":stage["raw_signed_worker_contribution"],
            "aggregate":stage["total_addition_if_positive"],
            "final_signed_job_output":value}

def fixtures():
    n=0
    def ck(val,exp):
        nonlocal n
        assert val==exp,(val,exp)
        n+=1
    ck(0x4d4-0x226,0x2ae)
    ck(model(planet_byte_f=0,breakdown_enabled=False),
       {"base":3,"nested_breakdown_plus_226":0,
        "raw_worker":8,"aggregate":8,"final_signed_job_output":0})
    ck(model(planet_byte_f=0,breakdown_enabled=True),
       {"base":3,"nested_breakdown_plus_226":0,
        "raw_worker":8,"aggregate":8,"final_signed_job_output":0})
    ck(model(planet_byte_f=10,breakdown_enabled=False),
       {"base":5,"nested_breakdown_plus_226":0,
        "raw_worker":8,"aggregate":8,"final_signed_job_output":0})
    ck(model(planet_byte_f=10,breakdown_enabled=True),
       {"base":5,"nested_breakdown_plus_226":2,
        "raw_worker":10,"aggregate":10,"final_signed_job_output":1})
    ck(model(planet_byte_f=11,breakdown_enabled=False),
       {"base":8,"nested_breakdown_plus_226":0,
        "raw_worker":8,"aggregate":8,"final_signed_job_output":0})
    ck(model(planet_byte_f=11,breakdown_enabled=True),
       {"base":8,"nested_breakdown_plus_226":5,
        "raw_worker":13,"aggregate":13,"final_signed_job_output":1})
    ck(model(planet_byte_f=10,breakdown_enabled=True,
             selected_player_byte_28=100)["raw_worker"],2)
    ck(model(planet_byte_f=10,breakdown_enabled=False,
             selected_player_byte_28=100)["raw_worker"],0)
    ck(model(planet_byte_f=11,breakdown_enabled=True,
             setting_idx=0)["raw_worker"],-5)
    ck(model(planet_byte_f=11,breakdown_enabled=True,
             setting_idx=0)["aggregate"],0)
    return n

def audit(exe,code):
    original,blob=exe.read_bytes(),code.read_bytes()
    if sha(original)!=EXE_SHA or len(blob)!=1410709 or sha(blob)!=CODE_SHA:
        raise ValueError("Original source hashes do not match")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    verified=[];maps={}
    for name,at,n,digest in BODIES:
        row=fs[name]
        if (int(row["offset"]),int(row["inferred_size"]))!=(at,n):
            raise ValueError("Original function-symbol extent differs: "+name)
        if sha(blob[at:at+n])!=digest:
            raise ValueError("Original named body digest differs: "+name)
        ins,cont=parse(code,at,n)
        for address,raw,op,arg in ins:
            if blob[address:address+len(raw)]!=raw:raise ValueError("Decoded original bytes differ")
        maps[name]={address:(op,arg) for address,raw,op,arg in ins}
        verified.append({"name":name,"CODE_offset":hex(at),"bytes":n,
                         "sha256":digest,"decoded_instructions":len(ins),
                         "continuation_lines_rejoined":cont})
    for addr,expect in OPS.items():
        matched=[maps[name].get(addr) for name in maps if addr in maps[name]]
        if len(matched)!=1 or matched[0]!=expect:
            raise ValueError(f"Instruction identity lost {addr:#x}: {matched} != {expect}")
    syms={(x["name"],x["segment"]):int(x["offset"]) for x in
          csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    if syms.get(("_colony_empire_base_functions","2"))!=0xB55C:
        raise ValueError("original indirect call DATA table identity mismatch")
    n=fixtures()
    return {"status":"source-authenticated-optional-breakdown-to-numeric-path",
      "original_EXE_SHA256":EXE_SHA,"LE_CODE_SHA256":CODE_SHA,
      "fully_verified_named_original_bodies":verified,
      "original_opcode_anchors":len(OPS),
      "temp_breakdown_start_local":"EBP-0x4d4",
      "nested_research_breakdown_offset":"0x226",
      "same_local_numeric_read":"EBP-0x2ae",
      "source_original_pointer_gate":"optional external breakdown pointer controls passing ECX = temp local buffer or ECX = 0",
      "source_original_numeric_dependency":"job always reads EBP-0x2ae when building eligible population contribution, including when temp buffer was not passed",
      "research_helper_specific_write":"when EBX nonnull and planet BYTE+0xf is 10 or 11, original helper ADDs 2 or 5 to DWORD [EBX+0x226]",
      "synthetic_fixture_count":n,
      "synthetic_examples":[model(planet_byte_f=v,breakdown_enabled=b)
                             for v in (0,10,11) for b in (False,True)],
      "limitations":[
        "No original DOS runtime/savegame differential test; no asserted user-observed gameplay bug",
        "Synthetic fixtures choose hypothetical state satisfying separated branch predicates; not a validated game-state domain",
        "No whole-engine native code equivalence or global buffer lifetime proof",
        "Caller-independent helper cache behavior assumed to be fresh and normal for fixtures"]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
