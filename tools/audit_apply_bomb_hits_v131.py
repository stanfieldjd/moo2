#!/usr/bin/env python3
"""Audit original MOO2 v1.31 Apply_Bomb_Hits_ Watcom shared-return loop.

Original named 95-byte function tail-jumps into an earlier routine's
7-byte shared LEAVE/POPs/RET at CODE 0xCCDA5. This is a real original
cross-function branch, not a standalone source-ret at 0xCD351.
Whole named body and shared return bytes have separate source hashes.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
ENTRY=0xCD2F2
SIZE=95
BODY_SHA="baec81af1f295344473a9fe92e85220822ba595802e3e81b130efd2bcce538a4"
SHARED=0xCCDA5
SHARED_SIZE=7
SHARED_SHA="1c903070ad87dea1760b46e99addec3215f3983c955b643356bd4e063a57466a"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
0xCD2F2:("push","ebx"),
0xCD2F3:("push","ecx"),
0xCD2F4:("push","edx"),
0xCD2F5:("push","esi"),
0xCD2F6:("push","edi"),
0xCD2F7:("enter","0x4,0x0"),
0xCD2FB:("mov","ecx,eax"),
0xCD2FD:("movzx","eax,byte ptr [eax+0x1]"),
0xCD301:("imul","eax,eax,0x169"),
0xCD307:("mov","esi,dword ptr ds:0x1ab18"),
0xCD30F:("movsx","edi,word ptr [ecx+0x6]"),
0xCD316:("movsx","esi,word ptr [ecx+0x3]"),
0xCD31A:("lea","eax,[esi+edi*1]"),
0xCD31D:("test","eax,eax"),
0xCD31F:("jle","0xccda5"),
0xCD325:("test","edi,edi"),
0xCD327:("jne","0xcd344"),
0xCD329:("mov","eax,dword ptr [ebp-0x4]"),
0xCD32C:("mov","ebx,esi"),
0xCD32E:("mov","edx,ecx"),
0xCD330:("call","0xccebd"),
0xCD335:("test","eax,eax"),
0xCD337:("je","0xcd340"),
0xCD339:("sub","esi,eax"),
0xCD33B:("add","dword ptr [ecx+0x45],eax"),
0xCD33E:("jmp","0xcd31a"),
0xCD340:("xor","esi,esi"),
0xCD342:("jmp","0xcd31a"),
0xCD344:("mov","eax,dword ptr [ebp-0x4]"),
0xCD347:("mov","edx,ecx"),
0xCD349:("call","0xcd13e"),
0xCD34E:("dec","edi"),
0xCD34F:("jmp","0xcd31a"),
SHARED:("leave",""),
0xCCDA6:("pop","edi"),
0xCCDA7:("pop","esi"),
0xCCDA8:("pop","edx"),
0xCCDA9:("pop","ecx"),
0xCCDAA:("pop","ebx"),
0xCCDAB:("ret",""),
}
def rows(filename):
    with (ROOT/"decompilation"/filename).open(newline="") as fp:
        return list(csv.DictReader(fp))
def op(code,offset):
    output=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--start-address=0x{offset:x}",f"--stop-address=0x{offset+15:x}",str(code)],
        capture_output=True,text=True,check=True).stdout
    for line in output.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==offset:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Original instruction absent at {offset:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Wrong original v1.31 executable SHA")
    binary=code.read_bytes()
    if len(binary)!=1410709:raise ValueError("Wrong original unrelocated CODE object")
    if hashlib.sha256(binary[ENTRY:ENTRY+SIZE]).hexdigest()!=BODY_SHA:
        raise ValueError("Original named body hash differs")
    if hashlib.sha256(binary[SHARED:SHARED+SHARED_SIZE]).hexdigest()!=SHARED_SHA:
        raise ValueError("Original shared epilogue hash differs")
    funcs={r["name"]:r for r in rows("functions.csv")}
    expected={
        "Apply_Bomb_Hits_":(ENTRY,SIZE),
        "Resolve_Bomb_Hit_":(0xCCEBD,641),
        "Resolve_Biological_Hit_":(0xCD13E,436),
        "Handle_Leader_At_Lost_Colony_":(0xCCCCC,224)
    }
    for name,(entry,size) in expected.items():
        f=funcs[name]
        if (int(f["offset"]),int(f["inferred_size"]))!=(entry,size):
            raise ValueError(f"Original named function boundary changed: {name}")
    syms={r["name"]:int(r["offset"]) for r in rows("symbols.csv") if r["segment"]=="2"}
    if syms.get("_colony")!=0x1AB18:
        raise ValueError("Original colony data pointer global changed")
    for at,exp in OPS.items():
        got=op(code,at)
        if got!=exp:
            raise ValueError(f"Original opcode at {at:#x}: {got} vs {exp}")
    return {
        "original_sha256":EXE_SHA,
        "original_named_function":"Apply_Bomb_Hits_",
        "original_entry":hex(ENTRY),
        "original_named_body_bytes":SIZE,
        "original_body_sha256":BODY_SHA,
        "source_external_epilogue":hex(SHARED),
        "shared_epilogue_bytes":SHARED_SIZE,
        "shared_epilogue_sha256":SHARED_SHA,
        "original_instruction_checks":len(OPS),
        "original_named_source_of_external_epilogue":"Handle_Leader_At_Lost_Colony_",
        "shared_prologue_epilogue_check":"PUSH EBX ECX EDX ESI EDI; ENTER 4; external LEAVE POP EDI ESI EDX ECX EBX RET",
        "original_colony_pointer":"_colony DATA+0x1ab18",
        "colony_stride_bytes":361,
        "event_colony_index_byte":"+0x1",
        "event_normal_hit_word":"+0x3 (signed)",
        "event_biological_hit_word":"+0x6 (signed)",
        "event_consumed_accumulator_dword":"+0x45",
        "original_resolve_bomb_call":"0xcd330 -> Resolve_Bomb_Hit_(0xccebd)",
        "original_resolve_bio_call":"0xcd349 -> Resolve_Biological_Hit_(0xcd13e)",
        "loop_condition":"signed 32-bit normal_count + biological_count > 0",
        "priority":"biological_count != 0 => Resolve_Biological_Hit_ and --biological_count, else Resolve_Bomb_Hit_",
        "normal_hit_result":"if resolver EAX nonzero: normal_count -= EAX and event DWORD +0x45 += EAX, else normal_count = 0",
        "shared_return":"EAX receives signed 32-bit pending hit count sum and reaches external 0xccda5 LEAVE/POPs/RET",
        "scope":"complete named source-byte and shared epilogue proof; typed C loop uses callbacks for unresolved resolver side effects and safety iteration cap"
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
