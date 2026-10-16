#!/usr/bin/env python3
"""Authenticate original v1.31 Random_/Shuffle_Int_/Shuffle_ chain.

Original Random_ uses 32-bit _random_seed LCG and UINT32_MAX/n
rejection sampling, returns one-based value 1..n. Source Shuffle_
uses Shuffle_Int_ for four-byte entries. This audit reads original
LE CODE and EXE and confirms three FULL function-body hashes and
key exact i386 instructions, including the shared Watcom epilogue.

No original DOS dynamic execution or proprietary media distribution.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODIES=[
 ("Random_",0x1147A0,128,"fed72b3293ed869db1e3ff6c93477767f0322794a2185d18c95798a49c92ff56"),
 ("Shuffle_Int_",0xEEA3C,70,"89379ad9f18797040d7bf7d33ef316c72c77d746f75c9ba95e5e47a3147e2315"),
 ("Shuffle_",0xEEA82,190,"d5dc211bc4f2300aa5c591335beac6e905aac5d6134309eb71e0a1a26e28a604"),
]
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
 0x1147A0:("push","0x30"),
 0x1147A5:("call","0x12f1e0"),
 0x1147B8:("mov","dword ptr [ebp-0x14],eax"),
 0x1147BB:("xor","edx,edx"),
 0x1147BD:("mov","eax,0xffffffff"),
 0x1147C2:("div","dword ptr [ebp-0x14]"),
 0x1147C5:("mov","dword ptr [ebp-0xc],eax"),
 0x1147C8:("mov","eax,dword ptr [ebp-0xc]"),
 0x1147CB:("imul","eax,dword ptr [ebp-0x14]"),
 0x1147CF:("mov","dword ptr [ebp-0x8],eax"),
 0x1147D2:("cmp","dword ptr [ebp-0x14],0x0"),
 0x1147D6:("jne","0x1147e1"),
 0x1147D8:("mov","dword ptr [ebp-0x4],0x1"),
 0x1147DF:("jmp","0x114814"),
 0x1147E1:("imul","eax,dword ptr ds:0x41e34,0x41c64e6d"),
 0x1147EB:("add","eax,0x3039"),
 0x1147F0:("mov","ds:0x41e34,eax"),
 0x1147F5:("mov","eax,dword ptr [ebp-0x8]"),
 0x1147F8:("cmp","eax,dword ptr ds:0x41e34"),
 0x1147FE:("jbe","0x1147e1"),
 0x114800:("xor","edx,edx"),
 0x114802:("mov","eax,ds:0x41e34"),
 0x114807:("div","dword ptr [ebp-0xc]"),
 0x11480A:("mov","dword ptr [ebp-0x10],eax"),
 0x11480D:("mov","eax,dword ptr [ebp-0x10]"),
 0x114810:("inc","eax"),
 0x114811:("mov","dword ptr [ebp-0x4],eax"),
 0x114814:("mov","eax,dword ptr [ebp-0x4]"),
 0x114819:("pop","ebp"),
 0x11481F:("ret",""),
 # specialized 4-byte shuffle and shared epilogue
 0xEEA3C:("push","ebx"),0xEEA3D:("push","ecx"),
 0xEEA3E:("push","esi"),0xEEA3F:("push","edi"),
 0xEEA40:("enter","0x8,0x0"),
 0xEEA44:("mov","esi,eax"),
 0xEEA46:("mov","ecx,edx"),
 0xEEA48:("xor","ebx,ebx"),
 0xEEA4A:("jmp","0xeea78"),
 0xEEA4C:("movsx","eax,cx"),
 0xEEA4F:("movsx","edx,bx"),
 0xEEA52:("sub","eax,edx"),
 0xEEA54:("call","0x1147a0"),
 0xEEA59:("add","eax,ebx"),
 0xEEA5B:("dec","eax"),
 0xEEA5C:("mov","dword ptr [ebp-0x4],eax"),
 0xEEA5F:("mov","eax,edx"),
 0xEEA61:("mov","edx,dword ptr [esi+eax*4]"),
 0xEEA64:("mov","dword ptr [ebp-0x8],edx"),
 0xEEA67:("movsx","edx,word ptr [ebp-0x4]"),
 0xEEA6B:("mov","edi,dword ptr [esi+edx*4]"),
 0xEEA6E:("mov","dword ptr [esi+eax*4],edi"),
 0xEEA71:("mov","eax,dword ptr [ebp-0x8]"),
 0xEEA74:("inc","ebx"),
 0xEEA75:("mov","dword ptr [esi+edx*4],eax"),
 0xEEA78:("cmp","bx,cx"),
 0xEEA7B:("jl","0xeea4c"),
 0xEEA7D:("jmp","0xee9ef"),
 0xEE9EF:("leave",""),
 0xEE9F0:("pop","edi"),
 0xEE9F1:("pop","esi"),
 0xEE9F2:("pop","ecx"),
 0xEE9F3:("pop","ebx"),
 0xEE9F4:("ret",""),
 # original generic Shuffle_ checks EDX stride4 and calls the helper
 0xEEA82:("push","ecx"),
 0xEEA91:("cmp","dx,0x2"),
 0xEEA99:("cmp","dx,0x4"),
 0xEEA9D:("je","0xeeac1"),
 0xEEAC1:("movsx","edx,bx"),
 0xEEAC4:("call","0xeea3c"),
 0xEEAC9:("jmp","0xeeb35"),
}
def rows(name):
    with (ROOT/"decompilation"/name).open(newline="") as fp:
        return list(csv.DictReader(fp))
def opcode(code,at):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
        f"--start-address=0x{at:x}",f"--stop-address=0x{at+16:x}",str(code)],
        capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==at:return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Original opcode missing at CODE {at:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original MOO2 v1.31 executable wrong hash")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Original LE CODE length differs")
    symbols={r["name"]:r for r in rows("functions.csv")}
    authenticated=[]
    for name,at,size,sha in BODIES:
        r=symbols[name]
        if (int(r["offset"]),int(r["inferred_size"]))!=(at,size):
            raise ValueError(f"Original Watcom function extent wrong {name}")
        if hashlib.sha256(b[at:at+size]).hexdigest()!=sha:
            raise ValueError(f"Original complete Watcom function body mismatch {name}")
        authenticated.append({"symbol":name,"original_CODE_offset":hex(at),
              "complete_body_bytes":size,"full_body_SHA256":sha})
    globals={r["name"]:int(r["offset"]) for r in rows("symbols.csv")
             if r["segment"]=="2"}
    if globals.get("_random_seed")!=0x41E34:
        raise ValueError("Original _random_seed DATA offset not as verified")
    for at,expected in OPS.items():
        found=opcode(code,at)
        if found!=expected:
            raise ValueError(f"CODE {at:#x}: got {found}, expected {expected}")
    return {
     "original_executable_SHA256":EXE_SHA,
     "original_full_named_function_bodies":authenticated,
     "verified_exact_original_instruction_checkpoints":len(OPS),
     "original_random_seed_DATA":"0x41e34",
     "Random_source":"unsigned q=UINT32_MAX/n, cutoff=q*n; 32bit state=state*0x41C64E6D+0x3039; repeat until state<cutoff; return state/q+1 (1..n)",
     "Random_divide_zero":"source unsigned DIV by n occurs before n==0 test, original would trap for n0; derived host rejects n0",
     "Shuffle_source_4byte":"for signed i=0..count-1: j=Random(count-i)+i-1; swap original four-byte entries[i] and [j]",
     "dispatch":"original generic Shuffle_ CODE 0xeeac4 dispatches stride EDX4 to exact Shuffle_Int_ entry CODE 0xeea3c",
     "shared_return":"Shuffle_Int_ source jumps to shared LEAVE POP EDI ESI ECX EBX RET at CODE 0xee9ef",
     "C_host_difference":"100000 RNG rejection retry cap, input and memory bounds checks; original can trap or loop on malformed source inputs",
     "scope":"full numerical seed and original 4-byte population shuffle source reconstructed, not DOS dynamic differential execution"
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
