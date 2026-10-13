#!/usr/bin/env python3
"""Audit two decompiled combat-ammo functions against ORIGINAL v1.31 x86.

Verifies authenticated executable, original LE CODE-object sizes,
Watcom entries, helper call edges, original 6-case jump table, iteration
bounds, data-symbol pointers, and signed/unsigned branch choices.

This is source-side structural validation, NOT DOS dynamic differential
execution or complete combat-gameplay equivalence. Original binary and
assets are never committed.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
CASE_TARGETS=[0x1959A,0x1957C,0x1959A,0x19585,0x1959E,0x19575]

def records(name):
    with (ROOT/"decompilation"/name).open(newline="") as fp:
        return list(csv.DictReader(fp))

def instruction(code,addr):
    output=subprocess.run(
       ["objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--start-address=0x{addr:x}",f"--stop-address=0x{addr+16:x}",str(code)],
       capture_output=True,text=True,check=True
    ).stdout
    for line in output.splitlines():
        match=RX.match(line)
        if match and int(match[1],16)==addr:
            return match[3].lower(),match[4].strip().lower()
    raise ValueError(f"Original x86 instruction missing at {addr:#x}")

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SHA:
        raise ValueError("Original DOS executable digest differs")
    blob=code.read_bytes()
    if len(blob)!=1410709:
        raise ValueError("Original raw LE CODE object size differs")
    funcs={r["name"]:r for r in records("functions.csv")}
    for name,offset,size in [
        ("Check_For_Launched_Fighters_",0x19480,95),
        ("Is_Ship_Out_Of_Ammo_",0x194DF,241),
        ("Does_Combat_Ship_Have_Special_",0x3B0D3,75),
        ("Test_Bit_Field_",0x1176F0,34)
    ]:
        r=funcs[name]
        if int(r["offset"])!=offset or int(r["inferred_size"])!=size:
            raise ValueError(f"Watcom symbol extent mismatch: {name}")
    data={r["name"]:int(r["offset"]) for r in records("symbols.csv")
          if r["segment"]=="2"}
    for name,expected in [
        ("_combat_data",0x1A864),("_missile",0x1AB14),
        ("_weapons",0x7803)
    ]:
        if data.get(name)!=expected:
            raise ValueError(f"Original DATA symbol differs: {name}")
    required={
        0x1948F:("imul","ecx,eax,0x1a"),
        0x1949D:("jne","0x194b3"),
        0x194A5:("cmp","byte ptr [eax+0x780f],0x4"),
        0x194B4:("cmp","bx,0x12c"),
        0x194B9:("jge","0x194c0"),
        0x194F7:("call","0x3b0d3"),
        0x19508:("call","0x3b0d3"),
        0x19527:("imul","esi,eax,0x139"),
        0x19537:("imul","eax,eax,0xb"),
        0x1953C:("mov","cx,word ptr [eax+0x52]"),
        0x1954C:("cmp","byte ptr [eax+0x54],0x0"),
        0x19559:("imul","ecx,ecx,0x1c"),
        0x1955C:("movzx","cx,byte ptr [ecx+0x780f]"),
        0x19564:("cmp","cx,0x5"),
        0x19568:("ja","0x195b7"),
        0x1956D:("jmp","dword ptr cs:[ecx*4+0x194c7]"),
        0x19575:("cmp","word ptr [ebp-0x4],0x21"),
        0x1957C:("cmp","word ptr [eax+0x58],0x0"),
        0x19585:("cmp","word ptr [eax+0x58],0x0"),
        0x1959E:("cmp","word ptr [eax+0x58],0x0"),
        0x195A8:("call","0x19480"),
        0x195B8:("cmp","dx,0x8"),
        0x195C8:("mov","eax,ebx"),
    }
    # Additional full special predicate and Watcom bitfield primitive.
    # The original query uses two independent 0x139-byte combat-record
    # bitsets: installed at +0x4C and suppressed at +0xB2.
    required.update({
        0x3B0D9:("imul","esi,esi,0x139"),
        0x3B0DF:("mov","eax,ds:0x1a864"),
        0x3B0EB:("add","eax,0x4c"),
        0x3B0F0:("call","0x1176f0"),
        0x3B0F5:("cmp","ax,0x1"),
        0x3B104:("add","eax,0xb2"),
        0x3B109:("call","0x1176f0"),
        0x3B10E:("test","ax,ax"),
        0x3B113:("mov","ecx,0x1"),
        0x1176F3:("shr","ebx,0x3"),
        0x1176FA:("and","ecx,0x7"),
        0x117701:("shr","eax,cl"),
        0x117703:("and","eax,0x1"),
        0x117706:("mov","ds:0x1176ec,eax"),
    })
    for addr,expected in required.items():
        actual=instruction(code,addr)
        if actual!=expected:
            raise ValueError(f"Original instruction at {addr:#x} changed: {actual} != {expected}")
    original=[int.from_bytes(blob[0x194C7+i*4:0x194CB+i*4],"little")
              for i in range(6)]
    if original!=CASE_TARGETS:
        raise ValueError("Original six-case weapon dispatch differs")
    for at,codeval in [(0x194EB,"edx,0x25"),(0x19501,"edx,0x26")]:
        if instruction(code,at)!=("mov",codeval):
            raise ValueError("Original special-type input differs")
    if instruction(code,0x195B0)!=("sete","al"):
        raise ValueError("Launched-fighter inverted flag semantics changed")
    if instruction(code,0x195B3)!=("movzx","bx,al"):
        raise ValueError("Launched-fighter output byte normalization changed")
    if instruction(code,0x1958C)!=("movzx","ax,byte ptr [esi+0x20]"):
        raise ValueError("Original ship-byte compare source changed")
    if instruction(code,0x19591)!=("cmp","ax,word ptr ds:0x218ac"):
        raise ValueError("Original unnamed global word changed")
    return {
        "source_sha256":SHA,
        "original_combat_ammo_offset":"0x194df",
        "combat_ammo_size_bytes":241,
        "original_launched_fighters_offset":"0x19480",
        "launched_fighters_size_bytes":95,
        "verified_opcode_sites":len(required)+6,
        "source_named_globals":{
            "_combat_data":"0x1a864","_missile":"0x1ab14",
            "_weapons":"0x7803"
        },
        "combat_ship_stride":313,
        "eight_weapon_slot_step_bytes":11,
        "weapon_definition_stride_bytes":28,
        "missile_record_stride_bytes":26,
        "original_missile_slots_scanned":300,
        "original_weapon_category_count":6,
        "original_special_check_offset":"0x3b0d3",
        "original_special_check_size_bytes":75,
        "original_bitfield_test_offset":"0x1176f0",
        "original_bitfield_test_size_bytes":34,
        "special_present_offset_in_combat_ship":"0x4c",
        "special_suppressed_offset_in_combat_ship":"0xb2",
        "bit_index_transform":"bit-index >>3 byte index; bit-index &7 shift; result masked to 1",
        "special_check_condition":"installed bit must equal 1 AND suppressed bit must equal 0",
        "side_effect_warning":"Original Test_Bit_Field_ writes result to scratch CODE+0x1176EC, a side effect intentionally omitted in pure derived C",
        "six_case_table_original_CODE_offset":"0x194c7",
        "six_case_destinations":[hex(v) for v in original],
        "named_helper_calls":[
            {"origin":"0x194f7","target":"Does_Combat_Ship_Have_Special_","special_id":"0x25"},
            {"origin":"0x19508","target":"Does_Combat_Ship_Have_Special_","special_id":"0x26"},
            {"origin":"0x195a8","target":"Check_For_Launched_Fighters_"}
        ],
        "scope":"byte-anchored static Watcom control-flow and symbols; derived C tests are separate and not original DOS differential validation"
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
