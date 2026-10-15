#!/usr/bin/env python3
"""Authenticate original MOO2 v1.31 Compute_Star_Colony_Stuff_.

Read-only source audit: SHA256 original ORION2.EXE and the COMPLETE
311-byte Watcom LE CODE function, selected exact i386 instructions,
named DATA pointers and 8-byte shared external epilogue. Derived C
tests are independent; this does not execute the original DOS game.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
ENTRY=0xD5296
LENGTH=311
BODY_SHA="b599c172a8a790494eb319c9edd73c881f6fea26a6e708ebf75cd3feae9d1ee0"
SHARED=0xD1F97
SHARED_SHA="a0a1f6af6d85bfeba680dfae738040640b858b18484a2aff60f23f3f7f7b6dc1"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
  0xD5296:("push","ebx"),
  0xD5297:("push","ecx"),
  0xD5298:("push","edx"),
  0xD5299:("push","esi"),
  0xD529A:("push","edi"),
  0xD529B:("enter","0x8,0x0"),
  0xD529F:("mov","byte ptr [eax+0x38],0x0"),
  0xD52A3:("mov","byte ptr [eax+0x39],0x0"),
  0xD52A7:("mov","byte ptr [eax+0x3e],0x0"),
  0xD52AB:("mov","byte ptr [eax+0x3d],0x0"),
  0xD52AF:("mov","byte ptr [eax+0x3b],0x0"),
  0xD52B3:("mov","byte ptr [eax+0x3c],0x0"),
  0xD52B7:("mov","byte ptr [eax+0x3f],0x0"),
  0xD52BB:("mov","esi,0x5"),
  0xD52C0:("mov","byte ptr [eax+0x40],0x0"),
  0xD52C4:("dec","esi"),
  0xD52C5:("movsx","edx,si"),
  0xD52C8:("mov","dx,word ptr [eax+edx*2+0x4a]"),
  0xD52CD:("movsx","edx,dx"),
  0xD52D0:("cmp","edx,0xffffffff"),
  0xD52D3:("je","0xd53bf"),
  0xD52D9:("imul","edx,edx,0x11"),
  0xD52DC:("mov","ecx,dword ptr ds:0x1b0d4"),
  0xD52E2:("mov","dx,word ptr [ecx+edx*1]"),
  0xD52E6:("movsx","edx,dx"),
  0xD52E9:("cmp","edx,0xffffffff"),
  0xD52EC:("je","0xd53bf"),
  0xD52F2:("imul","edx,edx,0x169"),
  0xD52F8:("mov","ecx,dword ptr ds:0x1ab18"),
  0xD52FE:("add","edx,ecx"),
  0xD5300:("movsx","cx,byte ptr [edx]"),
  0xD5304:("mov","word ptr [ebp-0x4],cx"),
  0xD5308:("mov","bl,0x1"),
  0xD530A:("mov","cl,byte ptr [ebp-0x4]"),
  0xD530D:("shl","bl,cl"),
  0xD530F:("add","edx,0x136"),
  0xD5315:("or","byte ptr [eax+0x38],bl"),
  0xD5318:("cmp","byte ptr [edx+0x2d],0x0"),
  0xD531C:("jbe","0xd5321"),
  0xD531E:("or","byte ptr [eax+0x39],bl"),
  0xD5321:("cmp","byte ptr [edx+0x28],0x0"),
  0xD5325:("ja","0xd5333"),
  0xD5327:("cmp","byte ptr [edx+0x8],0x0"),
  0xD532B:("ja","0xd5333"),
  0xD532D:("cmp","byte ptr [edx+0x29],0x0"),
  0xD5331:("jbe","0xd5373"),
  0xD5333:("movsx","ecx,word ptr [ebp-0x4]"),
  0xD5337:("imul","ecx,ecx,0xea9"),
  0xD533D:("mov","edi,dword ptr ds:0x1ff98"),
  0xD5345:("cmp","byte ptr [ecx+0x1cb],0x3"),
  0xD534C:("jne","0xd5351"),
  0xD534E:("or","byte ptr [eax+0x3b],bl"),
  0xD5351:("movsx","ecx,word ptr [ebp-0x4]"),
  0xD5355:("imul","ecx,ecx,0xea9"),
  0xD535E:("mov","ecx,dword ptr ds:0x1ff98"),
  0xD5367:("cmp","byte ptr [ecx+0x1c7],0x3"),
  0xD536E:("jne","0xd5373"),
  0xD5370:("or","byte ptr [eax+0x3c],bl"),
  0xD5373:("cmp","byte ptr [edx+0x3],0x0"),
  0xD5379:("or","byte ptr [eax+0x3f],bl"),
  0xD537C:("cmp","byte ptr [edx+0xe],0x0"),
  0xD5382:("or","byte ptr [eax+0x40],bl"),
  0xD5385:("movsx","edx,word ptr [ebp-0x4]"),
  0xD5389:("imul","edx,edx,0xea9"),
  0xD538F:("mov","ecx,dword ptr ds:0x1ff98"),
  0xD5395:("cmp","byte ptr [ecx+edx*1+0x17a],0x3"),
  0xD539D:("jne","0xd53a2"),
  0xD539F:("or","byte ptr [eax+0x3e],bl"),
  0xD53A2:("movsx","edx,word ptr [ebp-0x4]"),
  0xD53A6:("imul","edx,edx,0xea9"),
  0xD53AC:("mov","ecx,dword ptr ds:0x1ff98"),
  0xD53B2:("cmp","byte ptr [ecx+edx*1+0x1c1],0x3"),
  0xD53BA:("jne","0xd53bf"),
  0xD53BC:("or","byte ptr [eax+0x3d],bl"),
  0xD53BF:("test","si,si"),
  0xD53C2:("jg","0xd52c4"),
  0xD53C8:("jmp","0xd1f97"),
  0xD1F97:("leave",""),
  0xD1F98:("pop","edi"),
  0xD1F99:("pop","esi"),
  0xD1F9A:("pop","edx"),
  0xD1F9B:("pop","ecx"),
  0xD1F9C:("pop","ebx"),
  0xD1F9D:("ret",""),
}
def csvrows(p):
    with (ROOT/"decompilation"/p).open(newline="") as f:return list(csv.DictReader(f))
def decode(code,at):
    run=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
         f"--start-address=0x{at:x}",f"--stop-address=0x{at+16:x}",str(code)],
         capture_output=True,text=True,check=True)
    for l in run.stdout.splitlines():
        m=RX.match(l)
        if m and int(m[1],16)==at:return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Missing original instruction {at:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original executable identity mismatch")
    b=code.read_bytes()
    if len(b)!=1410709 or hashlib.sha256(b[ENTRY:ENTRY+LENGTH]).hexdigest()!=BODY_SHA:
        raise ValueError("Entire original Compute_Star_Colony_Stuff_ bytes mismatch")
    if hashlib.sha256(b[SHARED:SHARED+8]).hexdigest()!=SHARED_SHA:
        raise ValueError("Original external epilogue bytes mismatch")
    functions={r["name"]:r for r in csvrows("functions.csv")}
    row=functions["Compute_Star_Colony_Stuff_"]
    if(int(row["offset"]),int(row["inferred_size"]))!=(ENTRY,LENGTH):
        raise ValueError("Watcom source named function extent differs")
    globals={r["name"]:int(r["offset"]) for r in csvrows("symbols.csv") if r["segment"]=="2"}
    for n,off in [("_planet",0x1B0D4),("_colony",0x1AB18),("_player",0x1FF98)]:
        if globals.get(n)!=off:raise ValueError(f"Source DATA global differs {n}")
    for at,want in OPS.items():
        got=decode(code,at)
        if got!=want:raise ValueError(f"Original CODE {at:#x} {got} != {want}")
    return {
      "original_executable_SHA256":EXE_SHA,
      "source_function":"Compute_Star_Colony_Stuff_",
      "original_CODE_offset":"0xd5296",
      "original_complete_function_body_bytes":311,
      "original_complete_function_SHA256":BODY_SHA,
      "verified_original_instruction_sites":len(OPS),
      "shared_external_epilogue":"0xd1f97",
      "shared_epilogue_SHA256":SHARED_SHA,
      "original_named_DATA":{"_planet":"0x1b0d4","_colony":"0x1ab18","_player":"0x1ff98"},
      "star_planet_slots":"five signed WORDs, star+0x4a+2*i, i=4..0",
      "planet_colony_lookup":"_planet record stride 17, signed colony index WORD+0x00 or -1",
      "colony_owner_lookup":"_colony record stride 361, signed BYTE+0x00 owner, shifted 1<<owner",
      "player_record_stride":3753,
      "source_rebuilt_star_bytes":{
        "0x38":"any colony owner",
        "0x39":"colony building +45",
        "0x3b":"any building +40,+8,+41 AND player BYTE+0x1cb ==3",
        "0x3c":"any building +40,+8,+41 AND player BYTE+0x1c7 ==3",
        "0x3d":"player BYTE+0x1c1 ==3",
        "0x3e":"player BYTE+0x17a ==3",
        "0x3f":"colony building +3",
        "0x40":"colony building +14"},
      "source_calls":"none inside the original complete 311-byte body",
      "scope":"entire source instruction-defined star field rebuild; host preflight and owner index checks are non-DOS safety differences, not original DOS dynamic differential execution"}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
