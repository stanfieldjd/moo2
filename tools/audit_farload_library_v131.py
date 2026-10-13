#!/usr/bin/env python3
"""Audit the complete original Watcom Farload_Library_Data_ instruction shape.

Recognizes an embedded four-DWORD jump table as DATA, not x86 instructions.
Verifies original source SHA-256, code bytes and disassembly boundaries,
27 direct calls, 2048-byte LBX header, signature, four allocation dispatch
targets, two 16-bit reads and original return. Does NOT read or distribute LBX.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
ENTRY=0x116F3B
END=0x117233
TABLE=0x117145
TABLE_END=TABLE+16
DISPATCH=0x117190
BRANCH=0x117184
TARGETS=(0x117197,0x1171BA,0x1171E0,0x117206)
PAT=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
TARGET_PAT=re.compile(r"^0x([0-9a-f]+)\b",re.I)
EXPECTED_CALLS=27
EXPECTED_INSTRUCTIONS=194
EXPECTED_JUMPS=21
EXPECTED_HEADER=0x43A6C
EXPECTED_MAGIC=0xFEAD

def load_csv(name):
    with (ROOT/"decompilation"/name).open(newline="") as fp:
        return list(csv.DictReader(fp))

def decode(code,start,end):
    out=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
            f"--start-address=0x{start:x}",f"--stop-address=0x{end:x}",str(code)],
            capture_output=True,text=True,check=True).stdout
    result=[]
    for line in out.splitlines():
        m=PAT.match(line)
        if m:
            result.append(dict(offset=int(m[1],16),size=len(m[2].split()),
                               op=m[3].lower(),arg=m[4].lower().strip()))
    if not result or result[0]["offset"]!=start:
        raise ValueError(f"Disassembly does not start at {start:#x}")
    # objdump splits long original instructions (e.g. 10-byte MOV stores)
    # across multiple physical lines, with continuation bytes *without*
    # a mnemonic. Determine actual instruction sizes from the next decoded
    # opcode address; the final size is anchored to the exact interval end.
    for index,item in enumerate(result):
        subsequent=result[index+1]["offset"] if index+1<len(result) else end
        size=subsequent-item["offset"]
        if size<=0 or size>15 or size<item["size"]:
            raise ValueError(f"Invalid x86 instruction span at {item['offset']:#x}")
        item["size"]=size
    if result[-1]["offset"]+result[-1]["size"]!=end:
        raise ValueError("Disassembly misses interval end")
    return result

def assert_ins(ins,offset,op,arg=None):
    rec=ins.get(offset)
    if rec is None or rec["op"]!=op or (arg is not None and rec["arg"]!=arg):
        raise ValueError(f"Original instruction does not match at {offset:#x}: {rec}")
    return rec

def run(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError("Not authenticated v1.31 original executable")
    original=code.read_bytes()
    if len(original)!=1410709:
        raise ValueError("Unexpected raw original LE object 1 size")
    funcs=load_csv("functions.csv")
    named={int(f["offset"]):[] for f in funcs}
    for f in funcs:
        named[int(f["offset"])].append(f["name"])
    routine=[f for f in funcs if f["name"]=="Farload_Library_Data_"]
    if len(routine)!=1 or int(routine[0]["offset"])!=ENTRY or (
        int(routine[0]["inferred_size"])!=END-ENTRY):
        raise ValueError("Watcom routine bound differs")
    instructions=decode(code,ENTRY,TABLE)+decode(code,TABLE_END,END)
    ins={x["offset"]:x for x in instructions}
    if len(instructions)!=EXPECTED_INSTRUCTIONS:
        raise ValueError(f"Expected 194 instructions excluding table, got {len(instructions)}")
    calls=[]
    for item in instructions:
        if item["op"]=="call":
            m=TARGET_PAT.match(item["arg"])
            if not m:
                raise ValueError(f"Unexpected indirect call at {item['offset']:#x}")
            target=int(m[1],16)
            if target not in named:
                raise ValueError(f"Unmatched Watcom CODE symbol at {target:#x}")
            calls.append({"call_site_offset":hex(item["offset"]),
                          "target_offset":hex(target),
                          "target_symbols":named[target]})
    if len(calls)!=EXPECTED_CALLS:
        raise ValueError(f"Expected 27 direct calls, got {len(calls)}")
    jumps=sum(x["op"].startswith("j") or x["op"].startswith("loop") for x in instructions)
    if jumps!=EXPECTED_JUMPS:
        raise ValueError(f"Expected 21 conditional/unconditional jump instructions, got {jumps}")
    table_values=[int.from_bytes(original[TABLE+4*i:TABLE+4*i+4],"little")
                  for i in range(4)]
    if tuple(table_values)!=TARGETS:
        raise ValueError("Original four-DWORD jump table differs")
    assert_ins(ins,BRANCH,"ja","0x11720c")
    assert_ins(ins,DISPATCH,"jmp","DWORD PTR cs:[eax+0x117145]".lower())
    assert_ins(ins,0x117180,"cmp","DWORD PTR [ebp-0x38],0x3".lower())
    assert_ins(ins,0x11704E,"mov","ax,ds:0x43a6e")
    assert_ins(ins,0x117054,"cmp","eax,0xfead")
    assert_ins(ins,0x11703D,"mov","edx,0x800")
    assert_ins(ins,0x117042,"mov","eax,0x43a6c")
    assert_ins(ins,0x117047,"call","0x1188db")
    for at in (0x1170DB,0x1170F3):
        assert_ins(ins,at,"call","0x1188db")
    for at in TARGETS:
        if at not in ins:raise ValueError("Jump-table target not at an instruction boundary")
    assert_ins(ins,0x11719A,"call","0x101131")
    assert_ins(ins,0x1171C0,"call","0x101188")
    assert_ins(ins,0x1171E6,"call","0x1011d6")
    assert_ins(ins,0x117206,"mov","eax,DWORD PTR [ebp-0x48]".lower())
    assert_ins(ins,0x11721D,"call","0x1188db")
    assert_ins(ins,0x117230,"ret","0xc")
    # Check original, not a decompiler's guessed sentinel meaning. After
    # XOR EAX,EAX; MOV AX,word [local], EAX lies 0..65535, so 0xffffffff
    # is never equal under observed straight-line instruction semantics.
    sentinel=original[0x1170F8:0x117102]
    if sentinel!=bytes.fromhex("31 c0 66 8b 45 14 83 f8 ff 75"):
        raise ValueError("Source sentinel comparison bytes changed")
    return {
        "source_sha256":SOURCE_SHA,
        "watcom_symbol":"Farload_Library_Data_",
        "code_offset":hex(ENTRY),
        "size_bytes":END-ENTRY,
        "verified_instruction_count_excluding_embedded_table":len(instructions),
        "embedded_table_offset":hex(TABLE),
        "embedded_table_size_bytes":16,
        "jump_instructions":jumps,
        "direct_named_calls":len(calls),
        "header_read_bytes":2048,
        "header_original_DATA_object_offset":hex(EXPECTED_HEADER),
        "validated_header_magic":hex(EXPECTED_MAGIC),
        "header_number_of_entries":"uint16 at header +0; original code reads unaligned dword at header - 2 then signed SAR 16",
        "entry_offset_table":"DWORDs from header + 8, second at header +12; selected entry start/end offsets",
        "entry_two_word_reads":"original calls at 0x1170db, 0x1170f3 with EDX=2, EBX=1",
        "dispatch_entry_offset":hex(DISPATCH),
        "dispatch_index_register":"EAX <- saved original ECX * 4",
        "allocation_modes":[
            {"mode":0,"target_offset":hex(TARGETS[0]),"call":"Allocate_Space_No_Header_"},
            {"mode":1,"target_offset":hex(TARGETS[1]),"call":"Allocate_First_Block_No_Header_"},
            {"mode":2,"target_offset":hex(TARGETS[2]),"call":"Allocate_Next_Block_No_Header_"},
            {"mode":3,"target_offset":hex(TARGETS[3]),"call":"no allocation; pointer from original EBX"},
        ],
        "mode_out_of_range":"JA at 0x117184 bypasses table and keeps saved ECX pointer; exact calling contract pending",
        "sentinel_branch_note":"XOR EAX,EAX; MOV AX,[EBP+0x14]; CMP EAX,0xffffffff makes equality impossible under these instructions, even if AX == 0xffff. Do not claim a working wildcard size behavior.",
        "final_load":"fread_ original CODE 0x1188db then return loaded pointer via EAX; wrapper RET 0xc",
        "scope":"entire original instruction range structurally accounted, NOT full dataflow-equivalent LBX C decompilation or game-data validation",
        "call_edges":calls
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path,help="unrelocated original LE object 1")
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=run(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="call_edges"},indent=2))
