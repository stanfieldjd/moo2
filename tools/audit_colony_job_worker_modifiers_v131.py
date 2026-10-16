#!/usr/bin/env python3
"""Authenticated static v1.31 Colony_Job_Production_ per-entry multiplier audit.

Verify original canonical EXE, extracted Watcom CODE, exact named body and
machine instructions, source-indexed modifier table and controlled nonoverlap
stage behavior. Not DOS dynamic differential, native game, or source C.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from audit_remaining_colony_production_callers_v131 import parse

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
NAME="Colony_Job_Production_"
START,SIZE=0xCE280,996
BODY_SHA="853acbdf8e5057e9ad4f3a34c7f5aa98392c668eee1568f8133995ca5d641860"
SETTINGS_CODE_TABLE=0xCD4D7
SETTINGS_VALUES=(246,0,10,20,40,5,8,10,15,20,2,4,6,8,10)
SETTINGS_SHA="348ad136315e48429a9a5c1d1be7c999dcbe1d34abd267e26a4615d08d38e522"
SETTINGS_DATA_RECORD=0x21BDC
SETTINGS_SELECTOR_DATA=0x21CB0
# Exact original source opcodes spanning selector gate, signed multiplier
# selection and the aggregate/copy/return exits. Validated in raw CODE,
# not guessed from a compiler front-end or a community patch.
OPS={
 0xCE2B1:("sar","eax,cl"),
 0xCE2B3:("and","eax,0x1"),
 0xCE2DC:("cdq",""),
 0xCE2DF:("sar","eax,1"),
 0xCE385:("test","cl,cl"),
 0xCE387:("sete","byte ptr [ebp-0xc]"),
 0xCE393:("test","byte ptr [edi+0x1],0x2"),
 0xCE397:("je","0xce61e"),
 0xCE39F:("shl","edx,0x17"),
 0xCE3A6:("shr","edx,0x1e"),
 0xCE3AB:("jne","0xce61e"),
 0xCE3BB:("call","0xcdf2c"),
 0xCE3C0:("mov","edx,0x4"),
 0xCE3CA:("sub","edx,eax"),
 0xCE3FA:("call","0xce22c"),
 0xCE479:("movsx","eax,dx"),
 0xCE47C:("imul","eax,eax,0x14"),
 0xCE485:("add","dword ptr [ebp-0x4e],eax"),
 0xCE488:("cmp","word ptr [ebp-0x10],0x1"),
 0xCE494:("cmp","eax,0x8"),
 0xCE49C:("je","0xce4a7"),
 0xCE4A3:("mov","byte ptr [ebp-0x8],0x0"),
 0xCE4A7:("movsx","eax,word ptr [ebp-0x18]"),
 0xCE4AB:("movsx","ebx,dx"),
 0xCE4AE:("imul","eax,ebx"),
 0xCE4B1:("imul","eax,eax,0xfffffffb"),
 0xCE4BF:("movsx","eax,word ptr [ebp-0x14]"),
 0xCE4C3:("imul","ecx,eax"),
 0xCE4CF:("test","byte ptr [edi+0x1],0x4"),
 0xCE4D5:("imul","eax,ebx,0xfffffffb"),
 0xCE4E1:("cmp","byte ptr [ebp-0x8],0x0"),
 0xCE4E7:("movsx","eax,dx"),
 0xCE4EA:("movsx","ebx,byte ptr [esi+0x7]"),
 0xCE4EE:("imul","eax,ebx"),
 0xCE4F7:("mov","eax,dword ptr [ebp-0x296]"),
 0xCE500:("cmp","word ptr [ebp-0x10],0x1"),
 0xCE513:("cmp","dword ptr [ebp-0x1c],0x6"),
 0xCE519:("jbe","0xce523"),
 0xCE523:("movsx","eax,dx"),
 0xCE526:("imul","eax,eax,0xa"),
 0xCE52B:("movsx","eax,dx"),
 0xCE52E:("imul","eax,eax,0x14"),
 0xCE540:("cmp","byte ptr [ebp-0x4],0x0"),
 0xCE54A:("movsx","eax,dx"),
 0xCE54D:("imul","eax,eax,0xfffffff6"),
 0xCE55B:("cmp","dword ptr [ebp-0x1c],0x1"),
 0xCE579:("movsx","eax,dx"),
 0xCE57C:("imul","eax,eax,0xfffffff6"),
 0xCE581:("movsx","eax,dx"),
 0xCE584:("imul","eax,eax,0xfffffffb"),
 0xCE589:("movsx","eax,dx"),
 0xCE58C:("imul","eax,eax,0xa"),
 0xCE591:("movsx","eax,dx"),
 0xCE594:("imul","eax,eax,0xf"),
 0xCE5B5:("cmp","byte ptr [edx+eax*1+0x28],0x64"),
 0xCE5BC:("movzx","eax,byte ptr ds:0x21cb0"),
 0xCE5C3:("movsx","eax,byte ptr [eax+0xcd4d7]"),
 0xCE5D0:("add","dword ptr [ebp-0x2e],eax"),
 0xCE5D3:("mov","eax,dword ptr [ebp-0x2a6]"),
 0xCE5D9:("add","eax,dword ptr [ebp-0x2a2]"),
 0xCE5DF:("add","eax,dword ptr [ebp-0x28a]"),
 0xCE5E5:("add","eax,dword ptr [ebp-0x29e]"),
 0xCE5EB:("add","eax,dword ptr [ebp-0x296]"),
 0xCE5F1:("add","eax,dword ptr [ebp-0x29a]"),
 0xCE5F7:("add","eax,dword ptr [ebp-0x292]"),
 0xCE5FD:("add","eax,dword ptr [ebp-0x28e]"),
 0xCE609:("add","eax,dword ptr [ebp-0x2ae]"),
 0xCE611:("mov","dword ptr [ebp-0x282],edx"),
 0xCE617:("test","edx,edx"),
 0xCE619:("jle","0xce61e"),
 0xCE61B:("add","dword ptr [ebp-0x2a],edx"),
 0xCE627:("cmp","dword ptr [ebp-0x24],0x0"),
 0xCE62D:("mov","ecx,0x256"),
 0xCE63B:("rep","movs byte ptr es:[edi],byte ptr ds:[esi]"),
 0xCE63D:("cmp","word ptr [ebp-0x10],0x0"),
 0xCE647:("add","eax,0x14"),
 0xCE64A:("mov","ebx,0x28"),
 0xCE654:("add","eax,0xa"),
 0xCE657:("mov","ebx,0x14"),
 0xCE65D:("idiv","ebx"),
}
def sha(b): return hashlib.sha256(b).hexdigest()
def s8(v):
    v=v&255
    return v-256 if v>=128 else v
def job_gate(entry,job):
    """Source packed colony DWORD job eligibility, valid 0..2 job selector."""
    if not 0<=entry<=0xffffffff or job not in (0,1,2):
        raise ValueError("bounded original types required")
    return bool(entry&0x200) and ((entry>>7)&3)==job
def govt_multiplier(job,group):
    """Job-dependent base-weighted production adjustment, source stage."""
    if job not in (0,1,2) or not 0<=group<=7:
        raise ValueError("bounded source selector and derived government group")
    if job in (0,1):
        return {6:10,7:20}.get(group,0)
    return {0:-10,1:-5,4:10,5:15}.get(group,0)
def selected_job_worker_stage(*,job,tag,production_base,gravity_factor,
         leader_bonus=0,morale=0,government_group=3,star_owner_flag=False,
         packed_status_bit2=False,settings_index=1,player_byte_28=100,
         inherited_component=0):
    """Bounded static formula for the work contribution stage only.

    production_base is source-selected signed AX result of population helper;
    inherited_component is existing nonzero source-breakdown WORD/DWORD mix
    copied from nested per-pop helper, not inferred here.
    """
    if job not in (0,1,2) or not 0<=tag<=9:
        raise ValueError("source selectors invalid")
    if not 2<=gravity_factor<=4:
        raise ValueError("only original source-proven gravity 2,3,4")
    if not 0<=government_group<=7 or not 0<=settings_index<15:
        raise ValueError("controlled government/settings table index outside source domain")
    if not -1000<=production_base<=1000 or not -100<=morale<=100:
        raise ValueError("bounded fixture domain")
    if not -100<=leader_bonus<=100 or not -1000<=inherited_component<=1000:
        raise ValueError("bounded fixture domain")
    if not 0<=player_byte_28<=255:raise ValueError("source player field BYTE")
    morale_enabled=(government_group!=3 and not (job!=1 and tag==8))
    settings_component=0 if player_byte_28==100 else s8(SETTINGS_VALUES[settings_index])
    components={
      "base20":20*production_base,
      "gravity":(-5)*(4-gravity_factor)*production_base,
      "officer":leader_bonus*production_base,
      "packed_bit2":(-5)*production_base if packed_status_bit2 else 0,
      "morale":morale*production_base if morale_enabled else 0,
      "government":govt_multiplier(job,government_group)*production_base,
      "star_flag":(-10)*production_base if star_owner_flag and job in (0,1) else 0,
      "settings":settings_component,
      "inherited":inherited_component,
    }
    raw=sum(components.values())
    if not -(1<<31)<=raw<(1<<31):raise ValueError("signed 32-bit overflow unmodeled")
    return {"raw_signed_worker_contribution":raw,"total_addition_if_positive":max(raw,0),
            "components":components,"morale_applied":morale_enabled}

def fixtures():
    n=0
    def ck(actual,expected):
        nonlocal n
        assert actual==expected,(actual,expected)
        n+=1
    for job in (0,1,2):
        ck(job_gate(0x200|(job<<7),job),True)
        ck(job_gate((job<<7),job),False)
        ck(job_gate(0x200|(((job+1)%3)<<7),job),False)
    ck(job_gate(0x200|(2<<7)|0xF,2),True)
    for kind,group,val in [(0,6,10),(1,7,20),(2,0,-10),(2,1,-5),
                           (2,2,0),(2,3,0),(2,4,10),(2,5,15),(2,6,0)]:
        ck(govt_multiplier(kind,group),val)
    defaults={"job":1,"tag":1,"production_base":3,"gravity_factor":4}
    def stage(**changes):
        return selected_job_worker_stage(**{**defaults,**changes})
    ck(stage()["raw_signed_worker_contribution"],60)
    ck(stage(gravity_factor=3)["components"]["gravity"],-15)
    ck(stage(gravity_factor=2)["components"]["gravity"],-30)
    ck(stage(leader_bonus=4)["components"]["officer"],12)
    ck(stage(packed_status_bit2=True)["components"]["packed_bit2"],-15)
    ck(stage(government_group=3,morale=5)["components"]["morale"],0)
    ck(stage(government_group=2,morale=5)["components"]["morale"],15)
    ck(stage(job=0,tag=8,government_group=2,morale=5)["components"]["morale"],0)
    ck(stage(job=2,tag=8,government_group=2,morale=5)["components"]["morale"],0)
    ck(stage(job=1,tag=8,government_group=2,morale=5)["components"]["morale"],15)
    ck(stage(job=0,government_group=7)["components"]["government"],60)
    ck(stage(job=2,government_group=4)["components"]["government"],30)
    ck(stage(job=1,star_owner_flag=True)["components"]["star_flag"],-30)
    ck(stage(job=2,star_owner_flag=True)["components"]["star_flag"],0)
    ck(stage(settings_index=0,player_byte_28=90)["components"]["settings"],-10)
    ck(stage(settings_index=4,player_byte_28=90)["components"]["settings"],40)
    ck(stage(settings_index=14,player_byte_28=90)["components"]["settings"],10)
    ck(stage(settings_index=0,player_byte_28=100)["components"]["settings"],0)
    ck(stage(inherited_component=17)["components"]["inherited"],17)
    ck(stage(production_base=1,gravity_factor=2,packed_status_bit2=True,
             government_group=0,job=2)["raw_signed_worker_contribution"],-5)
    ck(stage(production_base=1,gravity_factor=2,packed_status_bit2=True,
             government_group=0,job=2)["total_addition_if_positive"],0)
    ck(stage(job=0,production_base=5,government_group=6,
             gravity_factor=3,leader_bonus=2,morale=5,
             packed_status_bit2=True,star_owner_flag=True,
             settings_index=2,player_byte_28=0)["raw_signed_worker_contribution"],95)
    return n

def audit(exe,code):
    b=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("canonical original EXE/LE CODE digest mismatch")
    fs={x["name"]:x for x in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    x=fs[NAME]
    if (int(x["offset"]),int(x["inferred_size"]))!=(START,SIZE) or sha(b[START:START+SIZE])!=BODY_SHA:
        raise ValueError("original shared job body mismatch")
    syms={(x["name"],x["segment"]):int(x["offset"]) for x in
       csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    for sym,segment,off in [("_settings","2",SETTINGS_DATA_RECORD),("_player","2",0x1FF98)]:
        if syms.get((sym,segment))!=off:raise ValueError("original global mismatch")
    table=b[SETTINGS_CODE_TABLE:SETTINGS_CODE_TABLE+len(SETTINGS_VALUES)]
    if tuple(table)!=SETTINGS_VALUES or sha(table)!=SETTINGS_SHA:
        raise ValueError("original source CODE-indexed production modifier table mismatch")
    ins,cont=parse(code,START,SIZE)
    idx={at:(op,arg) for at,raw,op,arg in ins}
    for at,raw,op,arg in ins:
        if b[at:at+len(raw)]!=raw:
            raise ValueError(f"full original instruction bytes mismatch {at:#x}")
    for at,expected in OPS.items():
        if idx.get(at)!=expected:raise ValueError(f"original opcode {at:#x}: {idx.get(at)} != {expected}")
    calls=0;direct=0
    for at,raw,op,arg in ins:
        if op=="call" or op.startswith("j"):
            direct+=1
            if op=="call":calls+=1
            else:
                if int(arg,16) not in idx:raise ValueError("original jump to non-instruction")
    if calls!=8 or direct!=62:raise ValueError("source full body transfer count changed")
    n=fixtures()
    return {"status":"source-verified-bounded-job-worker-production-modifiers",
      "official_EXE_SHA256":EXE_SHA,"LE_CODE_SHA256":CODE_SHA,
      "full_original_job_body":{"name":NAME,"CODE_offset":hex(START),"bytes":SIZE,"SHA256":BODY_SHA},
      "all_decoded_original_instructions":len(ins),
      "all_original_direct_transfers":direct,
      "source_disassembly_continuation_rows":cont,
      "exact_original_instruction_anchors":len(OPS),
      "original_settings_modifier_CODE":{"offset":hex(SETTINGS_CODE_TABLE),
         "signed_bytes":[s8(x) for x in SETTINGS_VALUES],"sha256":SETTINGS_SHA},
      "settings_selector_DATA":hex(SETTINGS_SELECTOR_DATA),
      "original_settings_record_DATA":hex(SETTINGS_DATA_RECORD),
      "controlled_synthetic_fixture_count":n,
      "eligible_packed_worker":"DWORD packed entry bit 9 must be set; job selector extracted from bits 7 and 8 must equal current job 0/1/2",
      "gravity_multiplier":"negative 5 times (4 - Gravity_Player_Production_Factor_()) times source base",
      "other_worker_components":"20*base, officer_bonus*base, packed DWORD bit 10: status test [entry+1]&4 = packed DWORD bit10 => -5*base, optional morale*base, government multiplier*base, star-related -10*base, signed CODE table setting, and inherited contribution from nested producer",
      "final_positive_gate":"only worker signed total >0 is added to job-production accumulator; original job returns signed IDIV after the worker loop",
      "caveats":["No DOS runtime differential comparison","Only bounded per-worker multiplication and source branch effects modeled",
                 "Nested helper inherited component passed as fixture input, not rederived",
                 "All player/planet legal state domains and signed overflow not established"]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
