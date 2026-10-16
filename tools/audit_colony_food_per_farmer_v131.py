#!/usr/bin/env python3
"""Original MOO2 v1.31 Colony_Food2_Per_Farmer_ 136-byte audit.

Verifies executable SHA, complete source body digest, Watcom named
function extent, original _planet/_player DATA globals and exact
source machine instructions for planet food and optional breakdown.
No original DOS dynamic differential execution.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
START=0xCE03E
LENGTH=136
BODY_SHA="6aef5f245db959b949a22eb0cfccd03b65db2c103a18c4dc47f5bbabcf9a04e4"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
 0xCE03E:("push","ecx"),
 0xCE03F:("push","esi"),
 0xCE040:("mov","ecx,eax"),
 0xCE042:("mov","esi,edx"),
 0xCE044:("movsx","eax,word ptr [eax+0x2]"),
 0xCE048:("imul","edx,eax,0x11"),
 0xCE04B:("mov","eax,ds:0x1b0d4"),
 0xCE050:("movzx","dx,byte ptr [edx+eax*1+0xb]"),
 0xCE056:("add","edx,edx"),
 0xCE058:("test","ebx,ebx"),
 0xCE05A:("je","0xce061"),
 0xCE05C:("movsx","eax,dx"),
 0xCE05F:("mov","dword ptr [ebx],eax"),
 0xCE061:("test","dx,dx"),
 0xCE064:("jne","0xce08b"),
 0xCE066:("movsx","esi,si"),
 0xCE069:("imul","esi,esi,0xea9"),
 0xCE06F:("mov","eax,ds:0x1ff98"),
 0xCE074:("cmp","byte ptr [esi+eax*1+0x134],0x3"),
 0xCE07C:("jne","0xce08b"),
 0xCE07E:("mov","edx,0x2"),
 0xCE083:("test","ebx,ebx"),
 0xCE085:("je","0xce08b"),
 0xCE087:("mov","word ptr [ebx+0x52],dx"),
 0xCE08B:("test","dx,dx"),
 0xCE08E:("jle","0xce0c1"),
 0xCE090:("cmp","byte ptr [ecx+0x164],0x0"),
 0xCE097:("je","0xce0a9"),
 0xCE099:("add","edx,0x4"),
 0xCE09C:("test","ebx,ebx"),
 0xCE09E:("je","0xce0a9"),
 0xCE0A0:("mov","word ptr [ebx+0x21c],0x4"),
 0xCE0A9:("cmp","byte ptr [ecx+0x13a],0x0"),
 0xCE0B0:("je","0xce0c1"),
 0xCE0B2:("inc","edx"),
 0xCE0B3:("inc","edx"),
 0xCE0B4:("test","ebx,ebx"),
 0xCE0B6:("je","0xce0c1"),
 0xCE0B8:("mov","word ptr [ebx+0x1c8],0x2"),
 0xCE0C1:("mov","eax,edx"),
 0xCE0C3:("pop","esi"),
 0xCE0C4:("pop","ecx"),
 0xCE0C5:("ret",""),
}
def decode(path,address):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
        f"--start-address=0x{address:x}",f"--stop-address=0x{address+16:x}",str(path)],
        capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==address:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Original x86 opcode missing: {address:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original EXE identity differs")
    raw=code.read_bytes()
    if len(raw)!=1410709 or hashlib.sha256(raw[START:START+LENGTH]).hexdigest()!=BODY_SHA:
        raise ValueError("Original complete Watcom source body differs")
    with (ROOT/"decompilation/functions.csv").open(newline="") as f:
        fs={r["name"]:r for r in csv.DictReader(f)}
    row=fs["Colony_Food2_Per_Farmer_"]
    if(int(row["offset"]),int(row["inferred_size"]))!=(START,LENGTH):
        raise ValueError("Original named function boundary differs")
    with (ROOT/"decompilation/symbols.csv").open(newline="") as f:
        gl={r["name"]:int(r["offset"]) for r in csv.DictReader(f) if r["segment"]=="2"}
    for name,addr in [("_planet",0x1B0D4),("_player",0x1FF98)]:
        if gl.get(name)!=addr:raise ValueError(f"Original DATA differs {name}")
    for at,expect in OPS.items():
        found=decode(code,at)
        if found!=expect:raise ValueError(f"Original source {at:#x}: {found} != {expect}")
    return {
       "original_EXE_SHA256":EXE_SHA,
       "named_original_function":"Colony_Food2_Per_Farmer_",
       "original_CODE_offset":"0xce03e",
       "original_body_bytes":LENGTH,
       "complete_original_body_SHA256":BODY_SHA,
       "exact_source_instruction_checkpoints":len(OPS),
       "DATA_globals":{"_planet":"0x1b0d4","_player":"0x1ff98"},
       "planet_food":"signed colony planet ID WORD+2 -> 17-byte planet record -> BYTE+0x0b; MOVZX DX retains upper original EDX; ADD EDX,EDX doubles full 32-bit register",
       "player_tech_fallback":"if low16 food==0 and signed player owner record BYTE+0x134==3, set EDX=2",
       "conditional_bonuses":"when signed low16 food>0, colony BYTE+0x164 nonzero adds 4; colony BYTE+0x13a nonzero adds 2",
       "optional_stats_writes":"DWORD+0 initial signextended base WORD; WORD+0x52=2 technology; WORD+0x21c=4 flag164; WORD+0x1c8=2 flag13a; only write fields for source-triggered conditions",
       "caller":"Colony_Environmental_Stuff_ at CODE 0xd1d39 passes colony EAX, signed owner EDX, and EBX=0, and tests AX==0 to write colony+0xe0",
       "scope":"complete named 136-byte source-body arithmetic and optional output effects, independent host mathematical regression; no original DOS dynamic differential execution"
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
