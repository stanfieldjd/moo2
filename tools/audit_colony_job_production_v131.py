#!/usr/bin/env python3
"""Source-authenticated complete 996-byte Colony_Job_Production_ control flow.

Reuses the already authenticated x86 byte-continuation decoder and checks
original helper identity, all CALL/JMP/Jcc endpoints, decisive source opcodes,
and bounded final divisors. This is a static decompilation packet, NOT proof
of DOS runtime or complete rule equivalence.
"""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from audit_remaining_colony_production_callers_v131 import (
    ROOT, EXE_SHA, CODE_SHA, HELPERS, parse, sha,
)

TARGET=("Colony_Job_Production_",0xCE280,996,
        "853acbdf8e5057e9ad4f3a34c7f5aa98392c668eee1568f8133995ca5d641860")
HELPERS_PLUS={**HELPERS,
 "Gravity_Player_Production_Factor_":(0xCDF2C,167,"a0660fd4edfd3b57bb91c406ca614e6c445ff509fb191eb5b757bdc254142200"),
 "Colony_Pop_Base_Prod_Produced_":(0xCE22C,84,"964117fde615677bbecb22bd682edf239015961f1ef758b03b67aaec5c0e0661")}
EXPECTED_CALLS={
 "Colony_Officer_":1,
 "memset_":2,
 "Owned_Officer_Level_":3,
 "Gravity_Player_Production_Factor_":1,
 "Colony_Pop_Base_Prod_Produced_":1,
}
# CODE offsets are anchored independently to original x86 output.
OPS={
  0xCE280:("push","ecx"),
  0xCE283:("enter","0x4d4,0x0"),
  0xCE287:("mov","esi,eax"),
  0xCE289:("mov","dword ptr [ebp-0x10],edx"),
  0xCE28C:("mov","dword ptr [ebp-0x24],ebx"),
  0xCE2BB:("call","0xcd9f2"),
  0xCE2E1:("mov","ebx,0x256"),
  0xCE2FB:("call","0x119c70"),
  0xCE303:("je","0xce376"),
  0xCE313:("cmp","word ptr [ebp-0x10],0x1"),
  0xCE332:("mov","eax,edi"),
  0xCE334:("call","0x84951"),
  0xCE347:("call","0x84951"),
  0xCE36B:("call","0x84951"),
  0xCE376:("movzx","edi,byte ptr [esi+0xa]"),
  0xCE37D:("shl","edi,0x2"),
  0xCE390:("sub","edi,0x4"),
  0xCE3BB:("call","0xcdf2c"),
  0xCE3DD:("call","0x119c70"),
  0xCE3FA:("call","0xce22c"),
  0xCE5B5:("cmp","byte ptr [edx+eax*1+0x28],0x64"),
  0xCE5BC:("movzx","eax,byte ptr ds:0x21cb0"),
  0xCE617:("test","edx,edx"),
  0xCE619:("jle","0xce61e"),
  0xCE61B:("add","dword ptr [ebp-0x2a],edx"),
  0xCE61E:("cmp","edi,dword ptr [ebp-0x20]"),
  0xCE621:("ja","0xce390"),
  0xCE627:("cmp","dword ptr [ebp-0x24],0x0"),
  0xCE62D:("mov","ecx,0x256"),
  0xCE63B:("rep","movs byte ptr es:[edi],byte ptr ds:[esi]"),
  0xCE63D:("cmp","word ptr [ebp-0x10],0x0"),
  0xCE644:("mov","eax,dword ptr [ebp-0x2a]"),
  0xCE647:("add","eax,0x14"),
  0xCE64A:("mov","ebx,0x28"),
  0xCE651:("mov","eax,dword ptr [ebp-0x2a]"),
  0xCE654:("add","eax,0xa"),
  0xCE657:("mov","ebx,0x14"),
  0xCE65D:("idiv","ebx"),
  0xCE65F:("leave",""),
  0xCE663:("ret",""),
}

def truncdiv(n,den):
    if den<=0:raise ValueError("positive denominator required")
    return (1 if n>=0 else -1)*(abs(n)//den)
def selected_final_arithmetic(total,kind):
    """Original final signed IDIV with bounded fixture accumulator only."""
    if not 0<=kind<=2 or not -10000<=total<=10000:
        raise ValueError("controlled domain: 3 job selectors, small totals")
    # 0: (total+20)/40; 1,2: (total+10)/20. Source uses IDIV trunc.
    bonus,den=(20,40) if kind==0 else (10,20)
    return truncdiv(total+bonus,den)
def tests():
    for kind,ratio in [(0,40),(1,20),(2,20)]:
        assert selected_final_arithmetic(0,kind)==0
        assert selected_final_arithmetic(ratio-1,kind)==1
        assert selected_final_arithmetic(ratio,kind)==1
        assert selected_final_arithmetic(ratio*2,kind)==2
    assert selected_final_arithmetic(-100,0)==-2
    assert selected_final_arithmetic(-100,1)==-4
    assert selected_final_arithmetic(-100,2)==-4
    return 15

def audit(exe,code):
    b=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("original game/CODE SHA mismatch")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    names=[TARGET,*[(name,*v) for name,v in HELPERS_PLUS.items() if name in EXPECTED_CALLS]]
    for name,off,n,sha_expected in names:
        row=fs[name]
        if (int(row["offset"]),int(row["inferred_size"]))!=(off,n) or sha(b[off:off+n])!=sha_expected:
            raise ValueError("source named function body mismatch: "+name)
    at,n=TARGET[1:3]
    ins,cont=parse(code,at,n)
    origins={x[0]:(x[2],x[3]) for x in ins}
    for address,raw,op,arg in ins:
        if b[address:address+len(raw)]!=raw:raise ValueError("decoded raw byte identity mismatch")
    for off,expected in OPS.items():
        if origins.get(off)!=expected:
            raise ValueError(f"original CODE {off:#x} {origins.get(off)} != {expected}")
    targets={v[0]:name for name,v in HELPERS_PLUS.items()}
    calls=Counter();transfers=[]
    for address,raw,op,arg in ins:
        if op=="call" or op.startswith("j"):
            if not re.fullmatch(r"0x[0-9a-f]+",arg):
                raise ValueError("unresolved original direct transfer: "+hex(address))
            target=int(arg,16)
            if op=="call":
                if target not in targets:raise ValueError("uncatalogued original callee: "+hex(target))
                calls[targets[target]]+=1
            elif target not in origins:
                raise ValueError("branch outside named function or into opcode: "+hex(target))
            transfers.append({"at":hex(address),"op":op,"to":hex(target)})
    if dict(calls)!=EXPECTED_CALLS:
        raise ValueError("source nested call count different: "+str(calls))
    syms={(x["name"],x["segment"]):int(x["offset"]) for x in
          csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    for symbol,offset in [("_player",0x1FF98),("_planet",0x1B0D4),("_leaders",0x1B0DC),
                          ("_settings",0x21BDC)]:
        if syms.get((symbol,"2"))!=offset:raise ValueError("global source identity differs "+symbol)
    count=tests()
    return {
        "status":"source-verified-static-shared-job-callee-control-flow",
        "canonical_exe_sha256":EXE_SHA,"LE_CODE_sha256":CODE_SHA,
        "full_named_procedure":{"name":TARGET[0],"start":hex(TARGET[1]),"bytes":TARGET[2],"sha256":TARGET[3]},
        "instruction_count":len(ins),"decoded_source_bytes":sum(len(x[1]) for x in ins),
        "byte_continuation_rows":cont,
        "direct_control_transfer_inventory":transfers,
        "nested_callee_call_counts":dict(calls),
        "authenticated_nested_helper_full_bodies":[
            {"name":n,"start":hex(v[0]),"bytes":v[1],"sha256":v[2]}
            for n,v in HELPERS_PLUS.items() if n in EXPECTED_CALLS
        ],
        "exact_instruction_anchors":len(OPS),
        "bounded_final_divisor_fixtures":count,
        "source_job_selectors":{
            "0":"signed IDIV ((accumulator + 20)/40)",
            "1":"signed IDIV ((accumulator + 10)/20)",
            "2":"signed IDIV ((accumulator + 10)/20)"
        },
        "other_source_observations":[
            "Optional 0x256-byte breakdown buffer is initialized/copy-filled inside the named body",
            "Walk packed 4-byte colony population entries in reverse, checking job-type bits",
            "SOURCE worker stage uses Gravity_Player_Production_Factor_ and Colony_Pop_Base_Prod_Produced_",
            "Accumulate source contributions only when positive for the final total, with job-specific modifier cases",
            "Function returns original signed IDIV quotient in EAX, does not directly write output WORD to colony"
        ],
        "limitations":[
            "No original DOS runtime differential execution",
            "Nested helpers' full body SHA checked, but this audit does not reconstruct their entire semantics",
            "Signed 32-bit arithmetic, custom production modifiers and all in-game states require further study",
            "Controlled arithmetic fixtures verify only the isolated final division stage"
        ]
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    val=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(val,indent=2)+"\n")
    print(json.dumps(val,indent=2))
