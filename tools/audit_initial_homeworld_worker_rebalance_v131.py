#!/usr/bin/env python3
"""Original MOO2 v1.31 initial-homeworld worker redistribution source audit.

Authenticate full original named machine-code bodies, exact decoded
instructions, first job2 reset, four subsequent conditional job transitions,
and recalculation/import call ordering. Models bounded individual source
transitions; not DOS execution or whole-colony steady-state simulation.
"""
import argparse,csv,hashlib,json
from itertools import product
from pathlib import Path
from audit_remaining_colony_production_callers_v131 import parse

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BODIES=[
 ("Twiddle_Initial_Homeworld_",0xD55BE,530,"63231cd00c846d3dc955e8144437ae7deb45d76525ee8d52866b275a2173e891"),
 ("Twiddle_Initial_Homeworlds_",0xD5832,693,"c5ca5500d59e4b1a4e386416845502c62a4359981fa350afdc779e9c92f7987b"),
 ("Init_Homeworld_Colony2_",0x3A3D,1386,"58e4c26cdfe04526e297334cca9b26e4c411c86cfe65da5b3f78834b6b8b3454"),
 ("Pre_Import_Computing_",0xD1D59,198,"7aa1ea0d54d5e89f82905724eb7fc1609c1e2b9a715c828f557fb4a9224d6628"),
 ("Pass_Out_Imports_",0xCF8F0,1238,"e35af6d4ee3106edd7af2f4f6377a18453e107323c620993b3f577871eff4234"),
 ("Colony_Job_Production_",0xCE280,996,"853acbdf8e5057e9ad4f3a34c7f5aa98392c668eee1568f8133995ca5d641860")]
OP={
 "Twiddle_Initial_Homeworld_":{
 0xD55C5:("lea","edx,[eax+0xc]"),
 0xD55C8:("movzx","esi,byte ptr [eax+0xa]"),
 0xD55D1:("shl","esi,0x2"),
 0xD55D4:("movzx","eax,byte ptr [ebx+0xa]"),
 0xD55DA:("shl","eax,0x2"),
 0xD55DD:("add","esi,edx"),
 0xD55DF:("add","eax,edx"),
 0xD55E1:("jmp","0xd55ef"),
 0xD55E3:("sub","eax,0x4"),
 0xD55E6:("and","word ptr [eax],0xfe7f"),
 0xD55EB:("or","byte ptr [eax+0x1],0x1"),
 0xD55EF:("cmp","edi,eax"),
 0xD55F1:("jb","0xd55e3"),
 0xD561A:("call","0xd1d59"),
 0xD5626:("call","0xcf8f0"),
 0xD562B:("cmp","ecx,esi"),
 0xD562D:("jae","0xd5659"),
 0xD562F:("movzx","ax,byte ptr [ebx+0xf0]"),
 0xD5637:("cmp","ax,word ptr [ebx+0xe9]"),
 0xD563E:("jle","0xd5659"),
 0xD5642:("and","word ptr [ecx],0xfe7f"),
 0xD5649:("or","byte ptr [ecx],0x80"),
 0xD564C:("call","0xd1d59"),
 0xD5654:("add","ecx,0x4"),
 0xD5657:("jmp","0xd5626"),
 0xD5659:("cmp","byte ptr [ebx+0xdd],0x0"),
 0xD5660:("je","0xd5692"),
 0xD5662:("cmp","ecx,esi"),
 0xD5664:("jae","0xd5692"),
 0xD5666:("movzx","ax,byte ptr [ebx+0xef]"),
 0xD566E:("cmp","ax,word ptr [ebx+0xe7]"),
 0xD5675:("jle","0xd5692"),
 0xD5679:("and","word ptr [ecx],0xfe7f"),
 0xD567E:("call","0xd1d59"),
 0xD5688:("add","ecx,0x4"),
 0xD568B:("call","0xcf8f0"),
 0xD5690:("jmp","0xd5662"),
 0xD5692:("cmp","ecx,esi"),
 0xD5694:("jae","0xd56c4"),
 0xD5696:("mov","ax,word ptr [ebx+0xe9]"),
 0xD569D:("cmp","ax,word ptr [ebx+0xeb]"),
 0xD56A4:("jge","0xd56c4"),
 0xD56A8:("and","word ptr [ecx],0xfe7f"),
 0xD56AF:("or","byte ptr [ecx],0x80"),
 0xD56B2:("call","0xd1d59"),
 0xD56BA:("add","ecx,0x4"),
 0xD56BD:("call","0xcf8f0"),
 0xD56C2:("jmp","0xd5692"),
 0xD56C4:("mov","ax,word ptr [ebx+0xeb]"),
 0xD56CB:("cmp","ax,word ptr [ebx+0xe9]"),
 0xD56D2:("jg","0xd56f1"),
 0xD56D4:("sub","ecx,0x4"),
 0xD56D9:("and","word ptr [ecx],0xfe7f"),
 0xD56E0:("or","byte ptr [ecx+0x1],0x1"),
 0xD56E4:("call","0xd1d59"),
 0xD56EC:("call","0xcf8f0")},
 "Twiddle_Initial_Homeworlds_":{
 0xD584C:("imul","ebx,ebx,0x169"),
 0xD5862:("sub","ebx,0x169"),
 0xD586A:("call","0xd55be")},
 "Init_Homeworld_Colony2_":{
 0x3BEB:("mov","dword ptr [ebp-0x1c],0x3"),
 0x3BF6:("and","edx,0x3"),
 0x3C15:("mov","dword ptr [ebp-0x1c],0x2"),
 0x3C23:("and","eax,0x3"),
 0x3C42:("and","ebx,0xf"),
 0x3C4C:("or","dword ptr [eax+0xc],ebx"),
 0x3C52:("and","byte ptr [eax+0xc],0x8f"),
 0x3C62:("or","byte ptr [eax+0xd],0x2")},
 "Colony_Job_Production_":{
 0xCE393:("test","byte ptr [edi+0x1],0x2"),
 0xCE397:("je","0xce61e"),
 0xCE39F:("shl","edx,0x17"),
 0xCE3A6:("shr","edx,0x1e"),
 0xCE3AB:("jne","0xce61e")},
 "Pre_Import_Computing_":{
 0xD1DFD:("xor","edx,edx"),
 0xD1DFF:("call","0xcff74")},
 "Pass_Out_Imports_":{
 0xCF8F0:("push","ebx"),
 0xCF8FA:("movsx","ebx,ax"),
 0xCF8FD:("imul","ebx,ebx,0xea9")}
}
DIRECT=[
 ("Twiddle_Initial_Homeworlds_",0xD586A,"Twiddle_Initial_Homeworld_"),
 ("Twiddle_Initial_Homeworld_",0xD561A,"Pre_Import_Computing_"),
 ("Twiddle_Initial_Homeworld_",0xD5626,"Pass_Out_Imports_"),
 ("Twiddle_Initial_Homeworld_",0xD564C,"Pre_Import_Computing_"),
 ("Twiddle_Initial_Homeworld_",0xD567E,"Pre_Import_Computing_"),
 ("Twiddle_Initial_Homeworld_",0xD568B,"Pass_Out_Imports_"),
 ("Twiddle_Initial_Homeworld_",0xD56B2,"Pre_Import_Computing_"),
 ("Twiddle_Initial_Homeworld_",0xD56BD,"Pass_Out_Imports_"),
 ("Twiddle_Initial_Homeworld_",0xD56E4,"Pre_Import_Computing_"),
 ("Twiddle_Initial_Homeworld_",0xD56EC,"Pass_Out_Imports_")]
def sha(x):return hashlib.sha256(x).hexdigest()
def s16(x):
    if not 0<=x<=65535:raise ValueError("source WORD range")
    return x if x<32768 else x-65536
def pack_job(dword,job):
    """Exactly source AND WORD+OR BYTE modifies only bits7/8."""
    if not 0<=dword<2**32 or job not in range(3):
        raise ValueError("bounded source packed entry or job")
    return (dword&~0x180)|((job&3)<<7)
def job(dword):return (dword>>7)&3
def initial_reset(dwords):
    """Reverse loop resets all currently counted entries to research job2."""
    result=list(dwords)
    for i in range(len(result)-1,-1,-1):
        result[i]=pack_job(result[i],2)
    return result
def guard(stage,*,at_end,f0=0,e9=0,dd=0,ef=0,e7=0,eb=0):
    """Individual original signed-16-bit CMP predicates, NOT an engine loop."""
    if stage=="surplus_to_industry":
        return not at_end and f0>s16(e9)
    if stage=="gated_to_food":
        return dd!=0 and not at_end and ef>s16(e7)
    if stage=="industry_balance":
        return not at_end and s16(e9)<s16(eb)
    if stage=="restore_previous_to_research":
        return s16(eb)<=s16(e9)
    raise ValueError("original stage unknown")
def fixtures():
    n=0
    for count in range(0,16):
        origin=[((i*1234567)&0xfffffc7f)|((i%3)<<7)|0x200 for i in range(count)]
        result=initial_reset(origin)
        assert len(result)==count
        n+=1
        for before,after in zip(origin,result):
            assert job(after)==2
            assert (before^after)&~0x180==0
            assert after&0x200==before&0x200
            n+=3
    for tag,high,active,prev_job,new_job in product((0,1,6,7),(0,0x12ab0000),(0,0x200),range(4),range(3)):
        before=high|tag|active|(prev_job<<7)
        after=pack_job(before,new_job)
        assert job(after)==new_job
        assert ((after^before)&~0x180)==0
        assert after&0x200==active
        n+=3
    samples=[0,1,2,127,128,254,255]
    comparisons=[0,1,0x7fff,0x8000,0xffff]
    for a,b in product(samples,comparisons):
        assert guard("surplus_to_industry",at_end=False,f0=a,e9=b)==(a>s16(b))
        assert guard("surplus_to_industry",at_end=True,f0=a,e9=b) is False
        assert guard("gated_to_food",at_end=False,dd=1,ef=a,e7=b)==(a>s16(b))
        assert guard("gated_to_food",at_end=False,dd=0,ef=a,e7=b) is False
        n+=4
    for a,b in product(comparisons,repeat=2):
        assert guard("industry_balance",at_end=False,e9=a,eb=b)==(s16(a)<s16(b))
        assert guard("industry_balance",at_end=True,e9=a,eb=b) is False
        assert guard("restore_previous_to_research",at_end=False,e9=a,eb=b)==(s16(b)<=s16(a))
        n+=3
    # Correct signed comparisons at boundary: WORD 0xffff is -1, not 65535.
    assert guard("surplus_to_industry",at_end=False,f0=0,e9=0xffff)
    assert guard("gated_to_food",at_end=False,dd=1,ef=0,e7=0xffff)
    assert guard("restore_previous_to_research",at_end=False,eb=0xffff,e9=0)
    n+=3
    return n
def audit(exe,code):
    b=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("canonical original v1.31 executable and code identity mismatch")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    full=[];mp={};count=0
    for name,at,size,digest in BODIES:
        f=fs[name]
        if (int(f["offset"]),int(f["inferred_size"]))!=(at,size) or sha(b[at:at+size])!=digest:
            raise ValueError("original function extent or full hash differs "+name)
        ins,continued=parse(code,at,size)
        if sum(len(x[1]) for x in ins)!=size:
            raise ValueError("incomplete original machine code decode "+name)
        for addr,raw,op,arg in ins:
            if b[addr:addr+len(raw)]!=raw:
                raise ValueError("decoded machine bytes mismatch")
        m={addr:(op,arg) for addr,raw,op,arg in ins}
        for addr,expect in OP[name].items():
            if m.get(addr)!=expect:
                raise ValueError(f"original source {name} {addr:#x}: {m.get(addr)} != {expect}")
        count+=len(ins);mp[name]=m
        full.append({"name":name,"CODE_offset":hex(at),"bytes":size,"SHA256":digest,
                     "decoded_source_instructions":len(ins),"objdump_continuation_rows_recombined":len(continued),
                     "selected_opcode_checks":len(OP[name])})
    with (ROOT/"decompilation/game_call_edges.csv").open(newline="") as fh:
        edgeindex={(r["caller"],r["callee"]) for r in csv.DictReader(fh)}
    for caller,addr,target in DIRECT:
        if (caller,target) not in edgeindex:
            raise ValueError("original source named edge missing")
        dest=int(fs[target]["offset"])
        if mp[caller].get(addr)!=("call",hex(dest)):
            raise ValueError("original direct CALL instruction target mismatch")
        if b[addr]!=0xE8 or addr+5+int.from_bytes(b[addr+1:addr+5],"little",signed=True)!=dest:
            raise ValueError("original machine displacement CALL mismatch")
    sym={(r["name"],r["segment"]):int(r["offset"]) for r in csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    if sym.get(("_colony","2"))!=0x1AB18:
        raise ValueError("original _colony DATA global mismatch")
    checks=fixtures()
    return {"status":"source-verified-original-homeworld-multi-stage-worker-job-rebalance",
      "original_EXE_SHA256":EXE_SHA,"original_LE_CODE_SHA256":CODE_SHA,
      "complete_original_function_body_audits":full,
      "fully_decoded_original_instruction_count":count,
      "source_opcode_anchor_count":sum(len(x) for x in OP.values()),
      "named_original_CALL_site_checks":len(DIRECT),
      "original_CALC_call_sites":["0xd561a","0xd564c","0xd567e","0xd56b2","0xd56e4"],
      "original_IMPORT_call_sites":["0xd5626","0xd568b","0xd56bd","0xd56ec"],
      "source_original_population_reset":"backwards over colony BYTE+0x0a entries beginning at colony+0x0c, clear job bits7/8 with AND WORD 0xfe7f and set job2 with OR BYTE+1 0x01",
      "conditional_stages":[
       {"name":"surplus_to_industry","source_guard":"cursor<end AND unsigned BYTE colony+0xf0 > signed WORD colony+0xe9","job":1,"site":"0xd5642..0xd5649"},
       {"name":"gated_to_food","source_guard":"BYTE colony+0xdd !=0 AND cursor<end AND unsigned BYTE colony+0xef > signed WORD colony+0xe7","job":0,"site":"0xd5679"},
       {"name":"industry_balance","source_guard":"cursor<end AND signed WORD colony+0xe9 < signed WORD colony+0xeb","job":1,"site":"0xd56a8..0xd56af"},
       {"name":"restore_previous_to_research","source_guard":"signed WORD colony+0xeb <= signed WORD colony+0xe9; original ECX first decremented by4","job":2,"site":"0xd56d4..0xd56e0"}
      ],
      "packed_job_BITMASK_HEX":"0x180","packed_active_BIT_HEX":"0x200",
      "controlled_source_model_assertions":checks,
      "limits":[
       "Original Pre_Import_Computing_ and Pass_Out_Imports_ recompute/mutate colony inputs between loop iterations; stage guards cannot be treated as constant over the whole routine",
       "Full original DOS runtime state/return values not executed, no final exact homeworld worker distribution asserted",
       "Final backstep ECX-4 is source-authenticated but no global index/safety proof under all hypothetical states",
       "Homeworld code10 preservation was addressed in prior checkpoint, not all later external side effects",
       "No proof valid game save exposes prior synthetic research reporting-dependent 0-vs-1 difference",
       "No native game implementation or revised whole executable decompilation percentage"
      ]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
