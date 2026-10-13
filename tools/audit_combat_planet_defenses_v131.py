#!/usr/bin/env python3
"""Verify original v1.31 Does_Combat_Planet_Have_Defenses_ 92-byte code.

This Watcom helper packs four colony byte fields using OR with shifts.
The original writes some 16-bit halves of 32-bit registers (SI/CX/DX/AX),
so only the returned AX's low 16-bit packed value is source-guaranteed
without additional caller-register provenance. Derived C returns a
zero-normalized full uint32_t: deliberate host interface difference.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODY_SHA="2e091e1f69040da609a1c6935910251caff5b38a071d45b5a1e7936488ee13c9"
ENTRY=0x2A142
SIZE=92
PAT=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
0x2A146:("movsx","eax,word ptr ds:0x21878"),
0x2A14D:("cmp","eax,0xffffffff"),
0x2A150:("je","0x2a197"),
0x2A152:("imul","eax,eax,0x169"),
0x2A158:("mov","edx,ds:0x1ab18"),
0x2A160:("movzx","si,byte ptr [eax+0x150]"),
0x2A168:("movzx","cx,byte ptr [eax+0x151]"),
0x2A170:("movzx","dx,byte ptr [eax+0x160]"),
0x2A178:("movzx","ax,byte ptr [eax+0x165]"),
0x2A180:("add","ecx,ecx"),
0x2A182:("mov","ebx,eax"),
0x2A184:("mov","eax,esi"),
0x2A186:("shl","edx,0x2"),
0x2A189:("or","eax,ecx"),
0x2A18B:("shl","ebx,0x3"),
0x2A18E:("or","eax,edx"),
0x2A190:("or","eax,ebx"),
0x2A196:("ret",""),
0x2A197:("xor","eax,eax"),
0x2A19D:("ret",""),
}
def readcsv(file):
    with (ROOT/"decompilation"/file).open(newline="") as f:
        return list(csv.DictReader(f))
def instruction(path,offset):
    p=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
         f"--start-address=0x{offset:x}",f"--stop-address=0x{offset+15:x}",str(path)],
         capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=PAT.match(line)
        if m and int(m[1],16)==offset:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Missing original i386 instruction {offset:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original game executable identity differs")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Wrong LE original CODE length")
    if hashlib.sha256(b[ENTRY:ENTRY+SIZE]).hexdigest()!=BODY_SHA:
        raise ValueError("Original entire function bytes differ")
    funcs={r["name"]:r for r in readcsv("functions.csv")}
    f=funcs["Does_Combat_Planet_Have_Defenses_"]
    if (int(f["offset"]),int(f["inferred_size"]))!=(ENTRY,SIZE):
        raise ValueError("Original Watcom function symbol changed")
    syms={r["name"]:int(r["offset"]) for r in readcsv("symbols.csv") if r["segment"]=="2"}
    if syms.get("_colony")!=0x1AB18 or syms.get("_cmbt_colony_id")!=0x21878:
        raise ValueError("Original colony or combat-colony globals differ")
    for at,expected in OPS.items():
        got=instruction(code,at)
        if got!=expected:
            raise ValueError(f"Original i386 opcode {at:#x}: {got} != {expected}")
    return {
        "original_sha256":EXE_SHA,
        "original_function":"Does_Combat_Planet_Have_Defenses_",
        "original_code_offset":hex(ENTRY),
        "original_function_size_bytes":SIZE,
        "original_full_body_sha256":BODY_SHA,
        "instruction_anchors":len(OPS),
        "combat_colony_global":"_cmbt_colony_id DATA+0x21878 as signed 16-bit",
        "colony_record_pointer":"_colony DATA+0x1ab18",
        "colony_record_stride_bytes":361,
        "field_offsets":["0x150","0x151","0x160","0x165"],
        "low16_packed_result":"byte150 | (byte151 << 1) | (byte160 << 2) | (byte165 << 3)",
        "missing_colony_id":"signed -1 => EAX=0",
        "original_result_high16_note":"Source MOVZX SI/CX/DX/AX only writes low halves; high EAX after OR can retain input register high halves. Only low16 guarantee derived, and caller Apply_Damage_To_Planet_ tests AX.",
        "host_compatibility_choice":"C helper outputs normalized uint32_t packed value and explicitly validates colony pointers/indices",
        "scope":"complete original 92-byte source body and selected opcode proof, not entire game or DOS register-differential execution"
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    x=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(x,indent=2)+"\n")
    print(json.dumps(x,indent=2))
