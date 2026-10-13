#!/usr/bin/env python3
"""Authenticate original MOO2 v1.31 single-entry Resolve_Bomb_Hit_ path.

Checks original ORION2.EXE SHA256, entire 641-byte source function body
digest, and specific original i386 instructions from selected lone entry
through defense reduction or population death/Remove_Building_(9).
This is bounded structural evidence, not DOS dynamic equivalence.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODY_SHA="ee665889d157c0882ac1512a67f1f940bf25a1d3d76811dcad0f30558d53dc89"
FUNCTION_ENTRY=0xCCEBD
FUNCTION_LENGTH=641
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
ANCHORS={
    0xCCF56:("cmp","byte ptr [ecx+0xa],0x1"),
    0xCCF5A:("jne","0xccff0"),
    0xCCF60:("cmp","dword ptr [ebp-0x4],0x0"),
    0xCCF64:("jne","0xccff7"),
    0xCCF6A:("mov","eax,dword ptr [ecx+0xc]"),
    0xCCF6D:("and","eax,0xf"),
    0xCCF70:("add","eax,eax"),
    0xCCF72:("add","eax,ecx"),
    0xCCF74:("cmp","word ptr [eax+0xb4],0x64"),
    0xCCF7C:("jg","0xccfdd"),
    0xCCF7E:("inc","word ptr [esi+0xc]"),
    0xCCF82:("mov","eax,dword ptr [ecx+0xc]"),
    0xCCF85:("and","eax,0xf"),
    0xCCF88:("mov","word ptr [ecx+eax*2+0xb4],0x0"),
    0xCCF92:("mov","byte ptr [ecx+0xa],0x0"),
    0xCCF96:("cmp","byte ptr [ecx+0x13f],0x0"),
    0xCCF9D:("je","0xccfba"),
    0xCCF9F:("mov","eax,ecx"),
    0xCCFA1:("sub","eax,dword ptr ds:0x1ab18"),
    0xCCFA7:("mov","ebx,0x169"),
    0xCCFAC:("cdq",""),
    0xCCFAD:("idiv","ebx"),
    0xCCFAF:("mov","edx,0x9"),
    0xCCFB4:("cwde",""),
    0xCCFB5:("call","0x45ea"),
    0xCCFBA:("mov","byte ptr [esi+0x42],0x1"),
    0xCCFBE:("movsx","eax,byte ptr [ecx]"),
    0xCCFC1:("imul","eax,eax,0xea9"),
    0xCCFC7:("mov","ebx,dword ptr ds:0x1ff98"),
    0xCCFCD:("add","ebx,eax"),
    0xCCFCF:("movsx","eax,byte ptr [esi]"),
    0xCCFD2:("add","word ptr [ebx+eax*2+0x6ff],0xa"),
    0xCCFDB:("jmp","0xccfe5"),
    0xCCFDD:("sub","word ptr [eax+0xb4],0x64"),
    0xCCFE5:("mov","eax,0x1"),
    0xCCFEA:("mov","byte ptr [esi+0x41],0x1"),
    0xCCFEE:("jmp","0xccff7"),
    0xCCFF7:("test","eax,eax"),
    0xCCFF9:("jne","0xcd139")
}

def read_rows(name):
    with (ROOT/"decompilation"/name).open(newline="") as f:
        return list(csv.DictReader(f))

def get_opcode(code,addr):
    r=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--start-address=0x{addr:x}",f"--stop-address=0x{addr+15:x}",str(code)],
        capture_output=True,text=True,check=True).stdout
    for line in r.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==addr:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Missing original Watcom instruction at {addr:#x}")

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Authenticated original game executable hash mismatch")
    data=code.read_bytes()
    if len(data)!=1410709:
        raise ValueError("Original unrelocated LE CODE size mismatch")
    if hashlib.sha256(data[FUNCTION_ENTRY:FUNCTION_ENTRY+FUNCTION_LENGTH]).hexdigest()!=BODY_SHA:
        raise ValueError("Original Resolve_Bomb_Hit_ function body changed")
    symbols={row["name"]:row for row in read_rows("functions.csv")}
    for name,off in [
        ("Resolve_Bomb_Hit_",FUNCTION_ENTRY),
        ("Remove_Building_",0x45EA)
    ]:
        if int(symbols[name]["offset"])!=off:
            raise ValueError(f"Original Watcom named helper changed: {name}")
    if int(symbols["Resolve_Bomb_Hit_"]["inferred_size"])!=FUNCTION_LENGTH:
        raise ValueError("Original function length no longer agrees")
    globals={r["name"]:int(r["offset"]) for r in read_rows("symbols.csv")
            if r["segment"]=="2"}
    for name,off in [("_colony",0x1AB18),("_player",0x1FF98)]:
        if globals.get(name)!=off:
            raise ValueError(f"Original Watcom DATA symbol changed: {name}")
    for at,expected in ANCHORS.items():
        observed=get_opcode(code,at)
        if observed!=expected:
            raise ValueError(f"CODE {at:#x}: original {observed} != {expected}")
    return {
        "original_exe_sha256":EXE_SHA,
        "named_function":"Resolve_Bomb_Hit_",
        "original_code_offset":hex(FUNCTION_ENTRY),
        "original_code_size_bytes":FUNCTION_LENGTH,
        "entire_original_body_sha256":BODY_SHA,
        "verified_original_opcode_sites":len(ANCHORS),
        "entry_guard":"original colony count BYTE+0x0A ==1 and original weighted non-population target total ==0",
        "single_population_entry_type":"DWORD at colony+0x0C, masked to low nibble (0..15)",
        "signed_defense_field":"colony WORD+0xB4+2*entry_type",
        "defense_above_100_path":"if signed WORD >100, subtract 100 and set event BYTE+0x41=1",
        "defense_at_most_100_path":"increment event WORD+0x0C, zero selected defense WORD, set colony count BYTE+0x0A to 0, optionally call Remove_Building_(colony index,9), set event BYTE+0x42, increment owner/opponent player WORD by 10, set event BYTE+0x41",
        "building_remove_guard":"colony BYTE+0x13F nonzero",
        "remove_building_named_original_CODE":"0x45ea",
        "remove_building_parameter":"EAX=(colony pointer-_colony pointer)/0x169, EDX=9",
        "player_stat_address":"_player + signed colony BYTE[0]*0xEA9 + 0x6FF + 2*signed event BYTE[0]",
        "original_return":"EAX=1 then shared exit through 0xCD139; full enclosing 641-byte resolver remains incomplete",
        "scope":"original executable and bounded branch fully source-instruction verified; derived C host guards and Remove_Building callback do not establish entire DOS game equivalence"
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
