#!/usr/bin/env python3
"""Trace Fire_Ship_ original weapon category producer and six dispatch cases.

Read-only audit of original authenticated MOO2 v1.31 Watcom CODE object.
The 6-way switch is driven by the signed weapon ID -> _weapons category
BYTE at +0x0C. The local [EBP-0x14] WORD also selects the mode-2
post-missile counter overwrite. Does not decompile full firing routine.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
OP=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
TABLE_OFFSET=0x28B46
DISPATCH=0x28F62
EXPECTED_TARGETS=[0x28FD1,0x28F6A,0x28F6A,0x290E2,0x28F6A,0x29113]
ANCHORS={
  0x28CA4:("movsx","eax,word ptr [esi]"),
  0x28CA7:("imul","eax,eax,0x1c"),
  0x28CAA:("movzx","ax,byte ptr [eax+0x780f]"),
  0x28CB2:("mov","dword ptr [ebp-0x14],eax"),
  0x28F53:("cmp","word ptr [ebp-0x14],0x5"),
  0x28F58:("ja","0x29143"),
  0x28F5E:("movzx","eax,word ptr [ebp-0x14]"),
  DISPATCH:("jmp","dword ptr cs:[eax*4+0x28b46]"),
  0x28F85:("call","0x2c892"),
  0x28F95:("cmp","word ptr [ebp-0x14],0x2"),
  0x28F9A:("jne","0x28fbb"),
  0x28FB5:("mov","word ptr [eax+0x58],dx"),
  0x28FC3:("dec","word ptr [edx+eax*1+0x58]"),
  0x28FF4:("call","0x294f7"),
  0x290EE:("call","0x2a6ca"),
  0x2910C:("dec","word ptr [edx+eax*1+0x58]"),
  0x29131:("call","0x2a82f"),
}
CATEGORIES=[
 ("beam","Fire_Beam_Weapon_"),
 ("missile","Fire_Missile_"),
 ("missile_special_counter","Fire_Missile_"),
 ("bomb","Fire_Bomb_"),
 ("missile","Fire_Missile_"),
 ("special","Fire_Special_Weapon_"),
]

def instruction(code,off):
    p=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--start-address=0x{off:x}",f"--stop-address=0x{off+15:x}",str(code)],
        capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=OP.match(line)
        if m and int(m[1],16)==off:return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Undecodable site {off:#x}")

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Wrong original v1.31 executable")
    binary=code.read_bytes()
    if len(binary)!=1410709:raise ValueError("Wrong original LE code length")
    with (ROOT/"decompilation/functions.csv").open(newline="") as f:
        names={r["name"]:r for r in csv.DictReader(f)}
    current=names["Fire_Ship_"]
    if int(current["offset"])!=0x28B5E or int(current["inferred_size"])!=2216:
        raise ValueError("Original Watcom Fire_Ship_ function boundary differs")
    with (ROOT/"decompilation/symbols.csv").open(newline="") as f:
        globals={r["name"]:int(r["offset"]) for r in csv.DictReader(f) if r["segment"]=="2"}
    if globals.get("_weapons")!=0x7803 or globals.get("_combat_data")!=0x1A864:
        raise ValueError("Original Watcom DATA globals differ")
    for off,expected in ANCHORS.items():
        result=instruction(code,off)
        if result!=expected:
            raise ValueError(f"Original source differs at {off:#x}: {result} != {expected}")
    raw_targets=[int.from_bytes(binary[TABLE_OFFSET+4*i:TABLE_OFFSET+4*i+4],"little") for i in range(6)]
    if raw_targets!=EXPECTED_TARGETS:
        raise ValueError("Original six-case CODE table changed")
    destinations={
        "Fire_Missile_":0x2C892,
        "Fire_Bomb_":0x2A6CA,
        "Fire_Beam_Weapon_":0x294F7,
        "Fire_Special_Weapon_":0x2A82F,
    }
    for n,off in destinations.items():
        if int(names[n]["offset"])!=off:
            raise ValueError(f"Original named callee changed: {n}")
    return {
        "original_sha256":EXE_SHA,
        "original_watcom_function":"Fire_Ship_",
        "function_entry":"0x28b5e",
        "function_length_bytes":2216,
        "producer_instructions":{
            "read_weapon_id":"0x28ca4 signed WORD from selected slot",
            "scale_weapon_definitions":"0x28ca7 *28 bytes",
            "read_category":"0x28caa byte at _weapons+12+28*weapon_id",
            "store_local":"0x28cb2 DWORD local EBP-0x14 (subsequently compared as WORD)",
        },
        "original_category_byte_offset_in_definition":12,
        "original_weapon_definition_stride":28,
        "original_six_case_table_offset":hex(TABLE_OFFSET),
        "dispatch_site_offset":hex(DISPATCH),
        "verified_instructions":len(ANCHORS),
        "case_map":[{"category":i,"target":hex(raw_targets[i]),"path":CATEGORIES[i][0],
                     "named_firing_helper":CATEGORIES[i][1]}
                    for i in range(6)],
        "default_for_category_gt_5":"branch 0x28f58 to shared 0x29143 without calling a firing helper",
        "category_two_counter_write":"original 0x28f95 tests same category WORD =2; after Fire_Missile_ original 0x28fb5 overwrites slot counter with _weapons+13 byte",
        "scope":"original-byte and named-control-flow verified category dispatch, not whole Fire_Ship_, call side effects, or original DOS differential execution"
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    data=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps(data,indent=2))
