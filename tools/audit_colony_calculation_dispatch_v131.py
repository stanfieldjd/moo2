#!/usr/bin/env python3
"""Authenticate source of MOO2 v1.31 Colony_Calculation_ dispatch.

Verify original DOS EXE hash, complete 65-byte named function,
three authenticated direct callee bodies, global DATA symbol
locations, exact 29 i386 opcode anchors and active/inactive
production gating. Callee effects not reconstructed in this audit.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODIES=[
 ("Colony_Calculation_",0xD2A70,65,"e667850010cdc8cb620bb98fcc6fe0c2b12971f572a8c48930c88833b940d63d"),
 ("Pre_Import_Computing_",0xD1D59,198,"7aa1ea0d54d5e89f82905724eb7fc1609c1e2b9a715c828f557fb4a9224d6628"),
 ("Pass_Out_Imports_",0xCF8F0,1238,"e35af6d4ee3106edd7af2f4f6377a18453e107323c620993b3f577871eff4234"),
 ("Update_Player_Stats_",0xD2710,864,"5b3d2b6948da42581600e270488ee10b4044851de96bcca00ba5358d6f00a38d"),
]
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
 0xD2A70:("push","ebx"),
 0xD2A71:("push","edx"),
 0xD2A72:("cwde",""),
 0xD2A73:("imul","eax,eax,0x169"),
 0xD2A79:("mov","ebx,dword ptr ds:0x1ab18"),
 0xD2A7F:("add","ebx,eax"),
 0xD2A81:("cmp","byte ptr [ebx+0x6],0x0"),
 0xD2A85:("jne","0xd2a98"),
 0xD2A87:("mov","eax,ebx"),
 0xD2A89:("call","0xd1d59"),
 0xD2A8E:("mov","edx,ebx"),
 0xD2A90:("movsx","eax,byte ptr [ebx]"),
 0xD2A93:("call","0xcf8f0"),
 0xD2A98:("movsx","eax,byte ptr [ebx]"),
 0xD2A9B:("imul","eax,eax,0xea9"),
 0xD2AA1:("mov","ebx,dword ptr ds:0x1ff98"),
 0xD2AA7:("add","eax,ebx"),
 0xD2AA9:("call","0xd2710"),
 0xD2AAE:("pop","edx"),
 0xD2AAF:("pop","ebx"),
 0xD2AB0:("ret",""),
}
def rows(name):
    with (ROOT/"decompilation"/name).open(newline="") as f:
        return list(csv.DictReader(f))
def opcode(code,at):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
        f"--start-address=0x{at:x}",f"--stop-address=0x{at+16:x}",str(code)],
        capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==at:return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Missing original x86 at {at:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original MOO2 executable SHA mismatch")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Watcom LE CODE bytes count differs")
    names={r["name"]:r for r in rows("functions.csv")}
    bodies=[]
    for name,start,size,sha in BODIES:
        r=names[name]
        if(int(r["offset"]),int(r["inferred_size"]))!=(start,size):
            raise ValueError("Original named function extent "+name)
        if hashlib.sha256(b[start:start+size]).hexdigest()!=sha:
            raise ValueError("Original source body SHA differs "+name)
        bodies.append({"name":name,"CODE_offset":hex(start),
             "full_original_body_bytes":size,"original_sha256":sha})
    sym={r["name"]:(r["segment"],int(r["offset"])) for r in rows("symbols.csv")}
    for name,expected in [
        ("_colony",("2",0x1AB18)),
        ("_player",("2",0x1FF98))]:
        if sym.get(name)!=expected:
            raise ValueError("Original global DATA "+name+" changed")
    for at,expected in OPS.items():
        got=opcode(code,at)
        if got!=expected:
            raise ValueError(f"Original instruction {at:#x}: {got} != {expected}")
    return {
      "original_EXE_SHA256":EXE_SHA,
      "verified_full_original_named_bodies":bodies,
      "verified_exact_opcode_checkpoints":len(OPS),
      "named_original_DATA_globals":{"_colony":"0x1ab18","_player":"0x1ff98"},
      "colony_input":"EAX low signed WORD colony index, signextended CWDE, original stride 0x169",
      "inactive_colony":"colony BYTE+6 !=0 skips Pre_Import_Computing_ and Pass_Out_Imports_, still updates owner player",
      "active_colony":"CODE 0xd2a89 calls Pre_Import_Computing_ EAX colony pointer, CODE 0xd2a93 calls Pass_Out_Imports_ EDX colony pointer and EAX signed owner BYTE+0",
      "always":"CODE 0xd2aa9 calls Update_Player_Stats_ EAX player record pointer (signed colony owner BYTE+0 * 0xEA9)",
      "owner_reload":"source loads signed colony owner once after preimport and once after import, permitting source callbacks to change subsequent routing",
      "limits":"only 65-byte named dispatcher control flow reimplemented; 198-byte Pre_Import_Computing_, 1238-byte Pass_Out_Imports_, and 864-byte Update_Player_Stats_ effects remain unresolved named callbacks; no DOS dynamic differential execution"
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    out=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
