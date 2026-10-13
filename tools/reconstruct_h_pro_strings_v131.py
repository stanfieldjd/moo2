#!/usr/bin/env python3
"""Reconstruct all 199 global string bindings in v1.31 Load_H_And_Pro_File_Strings_.

Source: original executable hash, Watcom symbol table and LE-relocated
instruction window. Never extracts original LBX text or executable bytes.
A contiguous 199*(MOV EAX,id; CALL E_Strings_; MOV global,EAX) sequence
plus a final global-to-global copy and RET must account for EVERY decoded
instruction in the 2,996-byte original function.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"decompilation"
SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
RAW_RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OFFSET=0xBE0E5
SIZE=2996
VA_BASE=0x10000
DATA_BASE=0x170000
E_STRINGS_VA=0xCDF5C
COUNT=199

def disassemble(path,start,end):
    output=subprocess.run([
        "objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--adjust-vma=0x{VA_BASE:x}",
        f"--start-address=0x{start+VA_BASE:x}",
        f"--stop-address=0x{end+VA_BASE:x}",str(path)
    ],capture_output=True,text=True,check=True).stdout
    items=[]
    for line in output.splitlines():
        m=RAW_RX.match(line)
        if m:
            items.append((int(m[1],16)-VA_BASE,len(m[2].split()),
                         m[3].lower(),m[4].strip().lower()))
    return items

def run(executable,code):
    if hashlib.sha256(executable.read_bytes()).hexdigest()!=SHA:
        raise ValueError("Not verified original 1.31 executable")
    if code.stat().st_size!=1410709:
        raise ValueError("Unexpected original LE code-object size")
    functions={r["name"]:r for r in csv.DictReader((D/"functions.csv").open(newline=""))}
    current=functions["Load_H_And_Pro_File_Strings_"]
    if int(current["offset"])!=OFFSET or int(current["inferred_size"])!=SIZE:
        raise ValueError("Original function extent differs")
    ins=disassemble(code,OFFSET,OFFSET+SIZE)
    if len(ins)!=COUNT*3+3:
        raise ValueError(f"Expected exactly 600 original decoded instructions, got {len(ins)}")
    lookup={}
    for r in csv.DictReader((D/"symbols.csv").open(newline="")):
        if r["segment"]=="2":
            lookup.setdefault(int(r["offset"]),[]).append(r["name"])
    records=[]
    cursor=OFFSET
    for n in range(COUNT):
        m,call,store=ins[n*3:n*3+3]
        if m[0]!=cursor or m[2:]!=("mov",m[3]) or not m[3].startswith("eax,0x"):
            raise ValueError(f"Noncanonical index load at binding {n}")
        ident=int(m[3][len("eax,0x"):],16)
        if not (0<=ident<0x32c):
            raise ValueError(f"String id outside source-declared 812 entry range at {n}")
        if call[0]!=m[0]+m[1] or call[2:]!=("call",f"0x{E_STRINGS_VA:x}"):
            raise ValueError(f"Missing named E_Strings call at binding {n}")
        if store[0]!=call[0]+call[1] or store[2]!="mov":
            raise ValueError(f"Unrecognized global store at binding {n}")
        match=re.fullmatch(r"ds:0x([0-9a-f]+),eax",store[3])
        if not match:raise ValueError(f"Unexpected destination at binding {n}")
        global_va=int(match[1],16)
        if not (DATA_BASE<=global_va<DATA_BASE+384208):
            raise ValueError("Global write is not inside relocated DATA object 2")
        off=global_va-DATA_BASE
        records.append({
            "ordinal":n,
            "original_call_sequence_offset":hex(m[0]),
            "string_id":ident,
            "string_id_hex":hex(ident),
            "data_destination_offset":hex(off),
            "exact_data_symbol_names":lookup.get(off,[]),
        })
        cursor=store[0]+store[1]
    last=ins[-3:]
    if (last[0][0]!=cursor or last[0][2:]!=("mov","eax,ds:0x19ef88")
        or last[1][0]!=last[0][0]+last[0][1]
        or last[1][2:]!=("mov","ds:0x191170,eax")
        or last[2][0]!=last[1][0]+last[1][1]
        or last[2][2:]!=("ret","")
        or last[2][0]+last[2][1]!=OFFSET+SIZE):
        raise ValueError("Original final global copy/RET does not match entire body")
    return {
        "original_sha256":SHA,
        "function":"Load_H_And_Pro_File_Strings_",
        "original_code_offset":hex(OFFSET),
        "original_length_bytes":SIZE,
        "total_original_decoded_instructions":len(ins),
        "verified_E_Strings_lookup_assignments":len(records),
        "distinct_string_ids":len({r["string_id"] for r in records}),
        "max_assigned_id":max(r["string_id"] for r in records),
        "final_copy":{
            "from_DATA_object2_offset":hex(0x19ef88-DATA_BASE),
            "to_DATA_object2_offset":hex(0x191170-DATA_BASE)
        },
        "scope":"complete instruction-shape account of this 2,996-byte function; original file/data initialization, pointer validity and string contents remain separate",
        "bindings":records,
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True,
                   help="relocated original LE CODE object 1")
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=run(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="bindings"},indent=2))
