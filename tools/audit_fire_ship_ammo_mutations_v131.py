#!/usr/bin/env python3
"""Original v1.31 Fire_Ship_ weapon-slot ammunition mutations.

Reads only original CODE bytes and Watcom symbols; validates the precise
original branches that write/DECREMENT weapon+0x58 after firing.
The full 2216-byte Fire_Ship_ routine is NOT reconstructed here.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
EXPECTED={
    0x28F62:("jmp","dword ptr cs:[eax*4+0x28b46]"),
    0x28F85:("call","0x2c892"),  # Fire_Missile_
    0x28F8A:("imul","edx,dword ptr [ebp-0x58],0xb"),
    0x28F8E:("imul","eax,dword ptr [ebp-0x48],0x139"),
    0x28F95:("cmp","word ptr [ebp-0x14],0x2"),
    0x28F9A:("jne","0x28fbb"),
    0x28FA6:("movsx","edx,word ptr [eax+0x52]"),
    0x28FAA:("imul","edx,edx,0x1c"),
    0x28FAD:("movzx","dx,byte ptr [edx+0x7810]"),
    0x28FB5:("mov","word ptr [eax+0x58],dx"),
    0x28FC3:("dec","word ptr [edx+eax*1+0x58]"),
    0x290EE:("call","0x2a6ca"), # Fire_Bomb_
    0x290F6:("imul","eax,dword ptr [ebp-0x4c],0x139"),
    0x29105:("imul","eax,ecx,0xb"),
    0x2910C:("dec","word ptr [edx+eax*1+0x58]"),
}

def op(code,site):
    x=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
       f"--start-address=0x{site:x}",f"--stop-address=0x{site+15:x}",str(code)],
       capture_output=True,text=True,check=True).stdout
    for line in x.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==site:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"No original instruction at {site:#x}")

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SHA:
        raise ValueError("Verified executable checksum mismatch")
    if code.stat().st_size!=1410709:
        raise ValueError("LE source CODE size differs")
    with (ROOT/"decompilation/functions.csv").open(newline="") as f:
        funcs={r["name"]:r for r in csv.DictReader(f)}
    if int(funcs["Fire_Ship_"]["offset"])!=0x28B5E or int(funcs["Fire_Ship_"]["inferred_size"])!=2216:
        raise ValueError("Original Fire_Ship_ source extent changed")
    for site,expected in EXPECTED.items():
        actual=op(code,site)
        if actual!=expected:
            raise ValueError(f"Original instruction mismatch {site:#x} {actual} != {expected}")
    for helper,expected in [("Fire_Missile_",0x2C892),("Fire_Bomb_",0x2A6CA)]:
        if int(funcs[helper]["offset"])!=expected:
            raise ValueError("Original firing helper target changed")
    with (ROOT/"decompilation/symbols.csv").open(newline="") as f:
        data={r["name"]:int(r["offset"]) for r in csv.DictReader(f) if r["segment"]=="2"}
    if data["_weapons"]!=0x7803 or data["_combat_data"]!=0x1A864:
        raise ValueError("Original DATA symbols changed")
    return {
       "original_sha256":SHA,
       "original_fire_ship_CODE_entry":"0x28b5e",
       "original_fire_ship_body_size_bytes":2216,
       "verified_original_instruction_sites":len(EXPECTED),
       "combat_record_stride":313,"weapon_slot_stride":11,
       "weapon_slot_counter_field_offset":"0x58 + slot*11",
       "missile_helper_call":"0x28f85 -> Fire_Missile_ (0x2c892)",
       "missile_mode_equal_two":"0x28f95 CMP mode,2; 0x28fad load byte at _weapons+13+28*weapon_id; 0x28fb5 store WORD at selected slot+0x58",
       "missile_other_modes":"0x28f9a JNE to 0x28fbb; 0x28fc3 DEC WORD at selected slot+0x58",
       "bomb_helper_call":"0x290ee -> Fire_Bomb_ (0x2a6ca)",
       "bomb_counter_change":"0x2910c DEC WORD at selected slot+0x58",
       "original_counter_underflow":"16-bit DEC wraps 0x0000 -> 0xffff; no bounds guard at this instruction",
       "scope":"verified bounded Fire_Ship_ mutation sites only; surrounding missile/bomb effects and full fire eligibility are NOT decompiled",
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
