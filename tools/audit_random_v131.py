#!/usr/bin/env python3
"""Verify original v1.31 Random_ 128-byte Watcom routine and seed behavior.

All original function bytes are SHA-checked; selected x86 instruction
anchors validate the rejection-sampling LCG and the unreachable zero-bound
branch. Does not claim original DOS dynamic execution or initial-seed value.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODY_SHA="fed72b3293ed869db1e3ff6c93477767f0322794a2185d18c95798a49c92ff56"
ENTRY=0x1147A0
SIZE=128
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
  0x1147B8:("mov","dword ptr [ebp-0x14],eax"),
  0x1147BB:("xor","edx,edx"),
  0x1147BD:("mov","eax,0xffffffff"),
  0x1147C2:("div","dword ptr [ebp-0x14]"),
  0x1147C8:("mov","eax,dword ptr [ebp-0xc]"),
  0x1147CB:("imul","eax,dword ptr [ebp-0x14]"),
  0x1147D2:("cmp","dword ptr [ebp-0x14],0x0"),
  0x1147D6:("jne","0x1147e1"),
  0x1147D8:("mov","dword ptr [ebp-0x4],0x1"),
  0x1147E1:("imul","eax,dword ptr ds:0x41e34,0x41c64e6d"),
  0x1147EB:("add","eax,0x3039"),
  0x1147F0:("mov","ds:0x41e34,eax"),
  0x1147F5:("mov","eax,dword ptr [ebp-0x8]"),
  0x1147F8:("cmp","eax,dword ptr ds:0x41e34"),
  0x1147FE:("jbe","0x1147e1"),
  0x114800:("xor","edx,edx"),
  0x114802:("mov","eax,ds:0x41e34"),
  0x114807:("div","dword ptr [ebp-0xc]"),
  0x114810:("inc","eax"),
  0x11481F:("ret",""),
}

def readcsv(file):
    with (ROOT/"decompilation"/file).open(newline="") as f:return list(csv.DictReader(f))

def get_op(code,at):
    p=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--start-address=0x{at:x}",f"--stop-address=0x{at+15:x}",str(code)],
        capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==at:
            return m[3].lower(),m[4].lower().strip()
    raise ValueError(f"Missing source instruction {at:#x}")

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SHA:
        raise ValueError("Verified source executable SHA mismatch")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Unexpected original LE CODE object length")
    if hashlib.sha256(b[ENTRY:ENTRY+SIZE]).hexdigest()!=BODY_SHA:
        raise ValueError("Original Random_ body digest mismatch")
    names={r["name"]:r for r in readcsv("functions.csv")}
    if int(names["Random_"]["offset"])!=ENTRY or int(names["Random_"]["inferred_size"])!=SIZE:
        raise ValueError("Original Random_ Watcom symbol differs")
    global_names={r["name"]:int(r["offset"]) for r in readcsv("symbols.csv") if r["segment"]=="2"}
    if global_names.get("_random_seed")!=0x41E34:
        raise ValueError("Original _random_seed DATA symbol differs")
    for at,expected in OPS.items():
        actual=get_op(code,at)
        if actual!=expected:
            raise ValueError(f"Original opcode mismatch {at:#x}: {actual} vs {expected}")
    return {
        "original_sha256":SHA,
        "function":"Random_",
        "original_code_offset":hex(ENTRY),
        "original_code_size_bytes":SIZE,
        "original_body_sha256":BODY_SHA,
        "verified_instruction_sites":len(OPS),
        "original_seed_symbol":"_random_seed",
        "original_seed_DATA_offset":"0x41e34",
        "LCG_multiplier":"0x41c64e6d",
        "LCG_increment":"0x3039",
        "original_unsigned_bound":"EAX uint32 max",
        "acceptance_limit":"(UINT32_MAX/max)*max",
        "retry_condition":"retry if seed >= acceptance_limit",
        "return":"1 + (seed/(UINT32_MAX/max)), 1..max inclusive for max>0",
        "zero_maximum_original":"DIV by EAX-arg zero at 0x1147c2 BEFORE test at 0x1147d2: machine exception; dead zero-case writes 1",
        "scope":"complete byte hash and instruction reconstruction of RNG result/state; caller seed initialization and DOS exception behavior remain outside derived C"
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
