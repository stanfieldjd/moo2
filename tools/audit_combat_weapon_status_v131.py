#!/usr/bin/env python3
"""Audit three recovered v1.31 tactical weapon-state helper bodies.

Byte-level checks tie each whole derived routine to authenticated original
Watcom CODE object; selected machine instructions and source symbols
cross-check the interpretation. This is not original DOS differential
execution, not a complete combat-turn reconstruction.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
FUNCS=[
    ("Weapons_Left_",0x26C60,60,
     "80de2dddd1f89b65e079b3c1122b352024cba20a8fc62040a77dde14e32f3f41"),
    ("Weapon_Is_On_",0x3584C,32,
     "926b93300eb8ed5f66beff71232e5893ca2cb5bdc2f3214568f6b6b05dc5003a"),
    ("Weapon_Is_Off_",0x3586C,32,
     "f47700db9f5cd6cab84b4b55003572520d74ea3215764f94234b66d9e43f0417"),
]
PAT=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
INSTRUCTIONS={
    0x26C64:("movsx","edx,dx"),
    0x26C67:("add","edx,edx"),
    0x26C6C:("movsx","esi,word ptr [ebx+0x104]"),
    0x26C75:("movsx","edi,word ptr [ebx+0x114]"),
    0x26C7D:("idiv","edi"),
    0x26C84:("idiv","edi"),
    0x26C86:("test","edx,edx"),
    0x26C88:("je","0x26c95"),
    0x26C8A:("cmp","word ptr [ebx+0x104],0x0"),
    0x26C92:("jle","0x26c95"),
    0x26C94:("inc","ecx"),
    0x26C95:("mov","eax,ecx"),
    0x3584D:("cwde",""),
    0x3584E:("imul","eax,eax,0x139"),
    0x35854:("mov","ebx,dword ptr ds:0x1a864"),
    0x3585C:("movsx","eax,dx"),
    0x3585F:("imul","eax,eax,0xb"),
    0x35862:("cmp","byte ptr [ebx+eax*1+0x5a],0x1"),
    0x35867:("sete","al"),
    0x3586D:("cwde",""),
    0x3586E:("imul","eax,eax,0x139"),
    0x35874:("mov","ebx,dword ptr ds:0x1a864"),
    0x3587C:("movsx","eax,dx"),
    0x3587F:("imul","eax,eax,0xb"),
    0x35882:("cmp","byte ptr [ebx+eax*1+0x5a],0x1"),
    0x35887:("setne","al"),
}

def readcsv(path):
    with path.open(newline="") as f:return list(csv.DictReader(f))

def opcode(path,addr):
    p=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
          f"--start-address=0x{addr:x}",f"--stop-address=0x{addr+15:x}",str(path)],
          capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=PAT.match(line)
        if m and int(m[1],16)==addr:
            return m[3].lower(),m[4].lower().strip()
    raise ValueError(f"Original instruction missing {addr:#x}")

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError("Source original executable identity mismatch")
    original=code.read_bytes()
    if len(original)!=1410709:
        raise ValueError("Original LE object length changed")
    fs={r["name"]:r for r in readcsv(ROOT/"decompilation/functions.csv")}
    functions=[]
    for name,entry,size,expected_hash in FUNCS:
        f=fs[name]
        if int(f["offset"])!=entry or int(f["inferred_size"])!=size:
            raise ValueError(f"Original named CODE extent changed: {name}")
        digest=hashlib.sha256(original[entry:entry+size]).hexdigest()
        if digest!=expected_hash:
            raise ValueError(f"Source function byte hash changed: {name}")
        functions.append({"name":name,"original_code_offset":hex(entry),
                          "size_bytes":size,"source_bytes_sha256":digest})
    syms={r["name"]:int(r["offset"]) for r in readcsv(ROOT/"decompilation/symbols.csv")
          if r["segment"]=="2"}
    if syms.get("_combat_data")!=0x1A864:
        raise ValueError("Original combat record pointer DATA symbol differs")
    for addr,expected in INSTRUCTIONS.items():
        actual=opcode(code,addr)
        if actual!=expected:
            raise ValueError(f"Opcode differs at {addr:#x}: {actual} / {expected}")
    return {
        "source_sha256":SOURCE_SHA,
        "original_named_function_count":len(functions),
        "original_function_body_bytes_verified":sum(x["size_bytes"] for x in functions),
        "selected_original_machine_instruction_anchors":len(INSTRUCTIONS),
        "combat_ship_record_stride":313,
        "weapon_status_flag_offset_in_ship":0x5A,
        "weapon_status_slot_stride":11,
        "weapon_status_compare_value":1,
        "status_return_register":"AL only (original SETE/SETNE AL)",
        "weapons_left_signed_short_first_offset":"0x104 + 2*slot",
        "weapons_left_signed_short_divisor_offset":"0x114 + 2*slot",
        "weapons_left_behavior":"signed IDIV twice; if remainder != 0 and numerator > 0 increment quotient, else return truncated quotient",
        "zero_divisor_original":"x86 IDIV divide-by-zero exception; isolated derived C instead returns explicit ZERO_DIVISOR status",
        "scope":"full source-byte hashes and opcode anchors, not original DOS dynamic-equivalence testing; derived C has safer bounds and normalized output",
        "functions":functions,
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
