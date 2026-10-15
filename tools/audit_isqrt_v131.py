#!/usr/bin/env python3
"""Audit authenticated original MOO2 v1.31 isqrt_ function bytes.

The original 155-byte function includes a Watcom runtime stack probe
then an unsigned integer binary-search square root; the derived C
omits the runtime stack probe. No executable DOS differential run.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_START=0x124C92
SIZE=155
BODY_SHA="712fab862da65b98b408b6bcaf4da8352fdb00306b0e40dfeeae616211d6c1b8"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
  0x124C92:("push","0x30"),
  0x124C97:("call","0x12f1e0"),
  0x124C9C:("push","ebx"),
  0x124C9D:("push","ecx"),
  0x124C9E:("push","edx"),
  0x124C9F:("push","esi"),
  0x124CA0:("push","edi"),
  0x124CA1:("push","ebp"),
  0x124CA2:("mov","ebp,esp"),
  0x124CA4:("sub","esp,0x14"),
  0x124CAA:("mov","dword ptr [ebp-0x10],eax"),
  0x124CAD:("cmp","dword ptr [ebp-0x10],0xfffe0001"),
  0x124CB4:("jb","0x124cbf"),
  0x124CB6:("mov","dword ptr [ebp-0x4],0xffff"),
  0x124CBD:("jmp","0x124d21"),
  0x124CBF:("cmp","dword ptr [ebp-0x10],0xffff"),
  0x124CC6:("ja","0x124cd8"),
  0x124CC8:("mov","dword ptr [ebp-0xc],0x0"),
  0x124CCF:("mov","dword ptr [ebp-0x8],0x100"),
  0x124CD6:("jmp","0x124ce6"),
  0x124CD8:("mov","dword ptr [ebp-0xc],0x100"),
  0x124CDF:("mov","dword ptr [ebp-0x8],0xffff"),
  0x124CE6:("mov","edx,dword ptr [ebp-0xc]"),
  0x124CE9:("add","edx,dword ptr [ebp-0x8]"),
  0x124CEC:("mov","eax,edx"),
  0x124CEE:("sar","edx,0x1f"),
  0x124CF1:("sub","eax,edx"),
  0x124CF3:("sar","eax,1"),
  0x124CF5:("mov","dword ptr [ebp-0x14],eax"),
  0x124CF8:("mov","edx,dword ptr [ebp-0x14]"),
  0x124CFB:("imul","edx,dword ptr [ebp-0x14]"),
  0x124CFF:("cmp","edx,dword ptr [ebp-0x10]"),
  0x124D02:("ja","0x124d0c"),
  0x124D04:("mov","eax,dword ptr [ebp-0x14]"),
  0x124D07:("mov","dword ptr [ebp-0xc],eax"),
  0x124D0A:("jmp","0x124d12"),
  0x124D0C:("mov","eax,dword ptr [ebp-0x14]"),
  0x124D0F:("mov","dword ptr [ebp-0x8],eax"),
  0x124D12:("mov","eax,dword ptr [ebp-0xc]"),
  0x124D15:("inc","eax"),
  0x124D16:("cmp","eax,dword ptr [ebp-0x8]"),
  0x124D19:("jl","0x124ce6"),
  0x124D1B:("mov","eax,dword ptr [ebp-0xc]"),
  0x124D1E:("mov","dword ptr [ebp-0x4],eax"),
  0x124D21:("mov","eax,dword ptr [ebp-0x4]"),
  0x124D24:("mov","esp,ebp"),
  0x124D26:("pop","ebp"),
  0x124D27:("pop","edi"),
  0x124D28:("pop","esi"),
  0x124D29:("pop","edx"),
  0x124D2A:("pop","ecx"),
  0x124D2B:("pop","ebx"),
  0x124D2C:("ret",""),
}
def decode(path,at):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
        f"--start-address=0x{at:x}",f"--stop-address=0x{at+16:x}",str(path)],
        capture_output=True,text=True,check=True)
    for l in p.stdout.splitlines():
        m=RX.match(l)
        if m and int(m[1],16)==at:return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"missing opcode {at:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Wrong original v1.31 EXE")
    b=code.read_bytes()
    if len(b)!=1410709 or hashlib.sha256(b[CODE_START:CODE_START+SIZE]).hexdigest()!=BODY_SHA:
        raise ValueError("Original complete isqrt_ source body differs")
    with (ROOT/"decompilation/functions.csv").open(newline="") as fp:
        f={r["name"]:r for r in csv.DictReader(fp)}
    row=f["isqrt_"]
    if(int(row["offset"]),int(row["inferred_size"]))!=(CODE_START,SIZE):
        raise ValueError("Original isqrt symbol extent differs")
    for at,expected in OPS.items():
        got=decode(code,at)
        if got!=expected:raise ValueError(f"CODE {at:#x} {got} != {expected}")
    return {
        "original_EXE_SHA256":EXE_SHA,
        "named_function":"isqrt_",
        "CODE_offset":"0x124c92",
        "complete_original_function_bytes":155,
        "original_body_SHA256":BODY_SHA,
        "original_instruction_anchors_verified":len(OPS),
        "source_math":"floor(sqrt(unsigned 32-bit EAX)), result <=65535",
        "saturation":"input>=0xFFFE0001 returns 65535",
        "source_search_bounds":"input<=65535: low0,high256; else low256,high65535",
        "source_binary_search":"middle=(low+high)/2; unsigned middle^2 <= input => low=middle else high=middle; return low when low+1>=high",
        "original_runtime_call":"0x124c97 calls Watcom stack probe at CODE 0x12f1e0; omitted in portable host C",
        "first_movement_caller":"Move_Player_1_Turn_To_Star_ CODE 0xdbb66 calls this function on 32-bit squared coordinate distance",
        "scope":"complete original integer arithmetic translated; no original DOS execution or full movement/collision logic reconstructed"
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
