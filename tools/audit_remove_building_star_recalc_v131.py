#!/usr/bin/env python3
"""Audit original MOO2 v1.31 direct building IDs 3/14/45 recalculation.

All read from original authenticated ORION2.EXE and local unrelocated LE
CODE. The outer Watcom Remove_Building_ body is full-sha verified;
these source-specific branches, globals and callees are checked at
individual i386 instruction locations. Queue-dependent building IDs
8,40,41 are intentionally outside the reconstructed direct paths.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
ENTRY=0x45EA
BODY_SIZE=493
BODY_SHA="8e0eb8d52268bf214d1ce3ec73d0e9970f0b4db1b0d1cae035810ace87179875"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
INS={
  0x45F6:("movsx","edx,ax"),
  0x45F9:("imul","eax,edx,0x169"),
  0x45FF:("mov","esi,dword ptr ds:0x1ab18"),
  0x460A:("mov","byte ptr [esi+eax*1+0x136],0x0"),
  0x4612:("cmp","bx,0xf"),
  0x4616:("jb","0x465a"),
  0x461E:("cmp","bx,0x1c"),
  0x4622:("jb","0x4642"),
  0x4636:("cmp","bx,0x2d"),
  0x463A:("je","0x46d4"),
  0x4668:("cmp","bx,0xe"),
  0x466C:("jmp","0x463a"),
  0x466E:("cmp","bx,0x3"),
  0x4672:("jmp","0x463a"),
  0x46D4:("movsx","edx,cx"),
  0x46D7:("imul","edx,edx,0x169"),
  0x46DD:("mov","eax,ds:0x1ab18"),
  0x46E2:("movsx","esi,word ptr [edx+eax*1+0x2]"),
  0x46E7:("imul","esi,esi,0x11"),
  0x46EA:("mov","eax,ds:0x1b0d4"),
  0x46EF:("movzx","eax,byte ptr [esi+eax*1+0x2]"),
  0x46F4:("imul","eax,eax,0x71"),
  0x46F7:("mov","esi,dword ptr ds:0x1b06c"),
  0x46FD:("add","eax,esi"),
  0x46FF:("call","0xd5296"),
  0x4704:("cmp","bx,0x2d"),
  0x4708:("jne","0x45e4"),
  0x470E:("mov","eax,ds:0x1ab18"),
  0x4713:("movsx","eax,byte ptr [edx+eax*1]"),
  0x4717:("call","0xf041c"),
  0x471C:("jmp","0x45e4"),
  0x45E4:("leave",""),
  0x45E5:("pop","edi"),
  0x45E6:("pop","esi"),
  0x45E7:("pop","ecx"),
  0x45E8:("pop","ebx"),
  0x45E9:("ret",""),
}
def csvrows(which):
    with (ROOT/"decompilation"/which).open(newline="") as fp:
        return list(csv.DictReader(fp))
def decode(code,at):
    p=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--start-address=0x{at:x}",f"--stop-address=0x{at+15:x}",str(code)],
        capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==at:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"No source instruction {at:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original MOO2 v1.31 EXE hash mismatch")
    b=code.read_bytes()
    if len(b)!=1410709 or hashlib.sha256(b[ENTRY:ENTRY+BODY_SIZE]).hexdigest()!=BODY_SHA:
        raise ValueError("Original 493-byte Remove_Building_ source changed")
    funcs={r["name"]:r for r in csvrows("functions.csv")}
    for name,at in [
        ("Remove_Building_",ENTRY),
        ("Compute_Star_Colony_Stuff_",0xD5296),
        ("Update_Ship_ETAs_",0xF041C)]:
        if int(funcs[name]["offset"])!=at:raise ValueError(f"Original callee differs: {name}")
    if int(funcs["Remove_Building_"]["inferred_size"])!=BODY_SIZE:
        raise ValueError("Original named function size changed")
    globals={r["name"]:int(r["offset"]) for r in csvrows("symbols.csv") if r["segment"]=="2"}
    for name,offset in [("_colony",0x1AB18),("_planet",0x1B0D4),("_star",0x1B06C)]:
        if globals.get(name)!=offset:raise ValueError(f"Original named DATA differs: {name}")
    for at,expected in INS.items():
        observed=decode(code,at)
        if observed!=expected:
            raise ValueError(f"Original {at:#x} opcode {observed} vs {expected}")
    return {
      "original_exe_sha256":EXE_SHA,
      "named_original_function":"Remove_Building_",
      "original_function_offset":hex(ENTRY),
      "original_full_body_size":BODY_SIZE,
      "original_full_body_sha256":BODY_SHA,
      "source_instruction_sites_verified":len(INS),
      "direct_recalculation_building_ids":[3,14,45],
      "additional_queue_dependent_ids_rejected":[8,40,41],
      "first_original_write":"colony[0x136+building_id]=0 at CODE 0x460a",
      "colony_planet_index":"SIGNED WORD colony+0x02; do not mislabel as star ID",
      "planet_lookup":"_planet pointer DATA 0x1b0d4; planet record stride 0x11; BYTE+0x02 supplies unsigned star index",
      "star_lookup":"_star pointer DATA 0x1b06c; star record stride 0x71; EAX pointer passed to Compute_Star_Colony_Stuff_(0xd5296)",
      "building45_only":"after star recomputation signed colony owner BYTE+0 supplied as EAX to Update_Ship_ETAs_(0xf041c)",
      "shared_return":"0x45e4 LEAVE/POP EDI/POP ESI/POP ECX/POP EBX/RET inside earlier Add_Building_ symbol",
      "scope":"verified bounded Remove_Building_ call dispatch with callbacks; original queue-dependent cases and true callee effects remain incomplete"
    }
if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe",required=True,type=Path)
    ap.add_argument("--code",required=True,type=Path)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    x=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(x,indent=2)+"\n")
    print(json.dumps(x,indent=2))
