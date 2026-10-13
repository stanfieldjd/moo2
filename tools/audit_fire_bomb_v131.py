#!/usr/bin/env python3
"""Authenticate the exact original 224-byte MOO2 v1.31 Fire_Bomb_ function.

Checks full original source CODE body digest, Watcom names and key i386
instructions. Derived C reconstructs the explicit arithmetic and outer
loop with callbacks for original Random_ and Apply_Damage_To_Planet_;
this audit does NOT prove those callbacks equivalent to the DOS runtime.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODY_SHA="3911947f8cdc202cb3a815dc354a95f5e5edc06c1433c9fb262b5096073af5d8"
ENTRY=0x2A6CA
SIZE=224
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
EXPECTED={
    0x2A6D5:("cwde",""),
    0x2A6D6:("imul","eax,eax,0x139"),
    0x2A6DC:("mov","ebx,dword ptr ds:0x1a864"),
    0x2A6E4:("movsx","ebx,si"),
    0x2A6E7:("imul","ebx,ebx,0xb"),
    0x2A6EA:("mov","bx,word ptr [ebx+eax*1+0x52]"),
    0x2A6F2:("movsx","ebx,bx"),
    0x2A6F5:("imul","ebx,ebx,0x1c"),
    0x2A6F8:("movzx","eax,byte ptr [eax+0x20]"),
    0x2A6FC:("movsx","eax,word ptr [eax*2+0x21224]"),
    0x2A707:("movsx","eax,word ptr [ebx+0x7817]"),
    0x2A70E:("imul","eax,dword ptr [ebp-0x1c]"),
    0x2A719:("cdq",""),
    0x2A71A:("idiv","dword ptr [ebp-0x18]"),
    0x2A720:("movsx","eax,word ptr [ebx+0x7819]"),
    0x2A727:("imul","eax,dword ptr [ebp-0x1c]"),
    0x2A730:("cdq",""),
    0x2A731:("idiv","ebx"),
    0x2A735:("sub","eax,dword ptr [ebp-0xc]"),
    0x2A73E:("jmp","0x2a781"),
    0x2A740:("mov","eax,0x64"),
    0x2A745:("movsx","ebx,word ptr [ebp-0x4]"),
    0x2A749:("call","0x1147a0"),
    0x2A74E:("cwde",""),
    0x2A74F:("imul","eax,ebx"),
    0x2A757:("cdq",""),
    0x2A758:("idiv","ebx"),
    0x2A75A:("movsx","ebx,word ptr [ebp-0xc]"),
    0x2A75E:("add","eax,ebx"),
    0x2A763:("movsx","eax,word ptr [ebp-0x10]"),
    0x2A767:("imul","eax,eax,0x1c"),
    0x2A76A:("xor","edx,edx"),
    0x2A76C:("movsx","ebx,word ptr [eax+0x7815]"),
    0x2A773:("lea","eax,[ebp-0x14]"),
    0x2A776:("inc","dword ptr [ebp-0x8]"),
    0x2A779:("call","0x2a3c3"),
    0x2A77E:("add","ecx,dword ptr [ebp-0x14]"),
    0x2A791:("movsx","eax,si"),
    0x2A794:("imul","eax,eax,0xb"),
    0x2A797:("movzx","ax,byte ptr [ebx+eax*1+0x5b]"),
    0x2A79D:("cmp","ax,word ptr [ebp-0x8]"),
    0x2A7A1:("jg","0x2a740"),
    0x2A7A3:("mov","eax,ecx"),
    0x2A7A9:("ret",""),
}

def readcsv(path):
    with path.open(newline="") as fp:return list(csv.DictReader(fp))

def ins(path,address):
    r=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
         f"--start-address=0x{address:x}",
         f"--stop-address=0x{address+15:x}",str(path)],
         capture_output=True,text=True,check=True)
    for line in r.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==address:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"No original instruction at {address:#x}")

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError("Not authenticated original v1.31 executable")
    blob=code.read_bytes()
    if len(blob)!=1410709:raise ValueError("Wrong original LE code image")
    if hashlib.sha256(blob[ENTRY:ENTRY+SIZE]).hexdigest()!=BODY_SHA:
        raise ValueError("Original complete Fire_Bomb_ function bytes changed")
    fs={r["name"]:r for r in readcsv(ROOT/"decompilation/functions.csv")}
    for n,a,s in [("Fire_Bomb_",ENTRY,SIZE),
                   ("Random_",0x1147A0,128),
                   ("Apply_Damage_To_Planet_",0x2A3C3,775)]:
        f=fs[n]
        if int(f["offset"])!=a or int(f["inferred_size"])!=s:
            raise ValueError(f"Original function extent changed: {n}")
    globals={r["name"]:int(r["offset"]) for r in readcsv(ROOT/"decompilation/symbols.csv")
             if r["segment"]=="2"}
    for n,off in [("_combat_data",0x1A864),
                  ("_ordnance_bonus",0x21224),
                  ("_weapons",0x7803)]:
        if globals.get(n)!=off:raise ValueError(f"Original DATA symbol differs {n}")
    for at,expected in EXPECTED.items():
        got=ins(code,at)
        if got!=expected:
            raise ValueError(f"Original opcode differs at {at:#x}: {got} != {expected}")
    return {
       "source_sha256":SOURCE_SHA,
       "original_function":"Fire_Bomb_",
       "original_code_offset":hex(ENTRY),
       "full_function_length_bytes":SIZE,
       "full_function_code_sha256":BODY_SHA,
       "source_instruction_anchors":len(EXPECTED),
       "combat_ship_stride":313,
       "weapon_slot_stride":11,
       "weapon_definition_stride":28,
       "ordnance_bonus_original_data_offset":"0x21224",
       "ordnance_bonus_index_source":"BYTE ship+0x20",
       "damage_min_weapon_definition_word_offset":"0x14",
       "damage_max_weapon_definition_word_offset":"0x16",
       "damage_type_weapon_definition_word_offset":"0x12",
       "original_damage_roll":"IDIV signed min*bonus /100 and max*bonus/100, then Random_(100) low signed AX * signed low16(max-min) /100, add signed low16(min)",
       "loop_count_byte":"combat weapon slot+0x09, reread after each callback",
       "random_helper":"Random_ original CODE+0x1147A0, passed EAX=100; full RNG effect not reimplemented",
       "damage_callback":"Apply_Damage_To_Planet_ CODE+0x2A3C3, EAX=&damage, EDX=0, EBX=definition field+0x12; original full effect not reimplemented",
       "return":"EAX=ECX aggregate of callback-modified damage words",
       "scope":"complete 224-byte source checksum and opcode/data/call audit; callback-bounded C translation not equivalent to entire DOS combat logic"
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
