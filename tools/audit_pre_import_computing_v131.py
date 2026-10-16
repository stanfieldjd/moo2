#!/usr/bin/env python3
"""Authenticate original v1.31 Pre_Import_Computing_ and worker/research.

Reads local authenticated ORION2.EXE and its exact Watcom LE objects,
verifies COMPLETE 198/178/177-byte named function bodies and 5-byte
mineral table, original 15 direct CALL sites and critical instruction
locations for initial zero, three output fields, after-replicator
signed min, and remaining downstream source dispatch.

The ten larger original economy functions remain named callbacks.
No original DOS runtime differential execution.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODIES=[
 ("Pre_Import_Computing_",0xD1D59,198,"7aa1ea0d54d5e89f82905724eb7fc1609c1e2b9a715c828f557fb4a9224d6628"),
 ("Colony_Industry_Per_Worker_",0xCEC95,178,"1e58a5b42e7d04cbc1d412b55ba007dbee502d5f0c257a96890c93d5689d8aa9"),
 ("Colony_Research_Per_Scientist_",0xCFDC6,177,"7d9e54a024e600115cf99d1d299806ceaf74f93c1aa95638a135b97e2efadd14"),
 ("Colony_Food2_Per_Farmer_",0xCE03E,136,"6aef5f245db959b949a22eb0cfccd03b65db2c103a18c4dc47f5bbabcf9a04e4"),
 ("Colony_Environmental_Stuff_",0xD1CED,108,"94c8b7df7075f34a74650d3dc72ff466c6d9e69d57afaaa2502679d16131a086"),
]
MINERAL_AT=0xCD4B5
MINERAL_BYTES=bytes([1,2,3,5,8])
CALLS={
0xD1D6A:("memset_","0x119c70"),
0xD1D76:("Colony_Food2_Per_Farmer_","0xce03e"),
0xD1D85:("Colony_Environmental_Stuff_","0xd1ced"),
0xD1D8F:("Colony_Industry_Per_Worker_","0xcec95"),
0xD1DA1:("Colony_Research_Per_Scientist_","0xcfdc6"),
0xD1DB0:("Colony_Morale_","0xcdb25"),
0xD1DB7:("Colony_Industry_Maintenance_","0xcf546"),
0xD1DC0:("Colony_Industry_Production_","0xcee1b"),
0xD1DC9:("Colony_Food_Production_","0xce664"),
0xD1DD0:("Colony_Food_Maintenance_","0xceb4b"),
0xD1DD7:("Colony_Replicators_","0xcf66f"),
0xD1DFF:("Colony_Research_Production_","0xcff74"),
0xD1E06:("Colony_Industry_To_Tax_","0xd08f6"),
0xD1E0F:("Colony_BC_Production_","0xd03f1"),
0xD1E16:("Colony_BC_Maintenance_","0xd094f"),
}
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPCODES={
0xD1D59:("push","ebx"),0xD1D5A:("push","ecx"),
0xD1D5B:("push","edx"),0xD1D5C:("mov","ecx,eax"),
0xD1D5E:("mov","ebx,0x4"),0xD1D63:("add","eax,0xef"),
0xD1D68:("xor","edx,edx"),
0xD1D6F:("mov","eax,ecx"),0xD1D71:("movsx","edx,byte ptr [ecx]"),
0xD1D74:("xor","ebx,ebx"),
0xD1D7B:("mov","byte ptr [ecx+0xdd],al"),
0xD1D81:("mov","eax,ecx"),0xD1D83:("xor","ebx,ebx"),
0xD1D8A:("mov","eax,ecx"),0xD1D8C:("movsx","edx,byte ptr [ecx]"),
0xD1D94:("movsx","edx,byte ptr [ecx]"),
0xD1D97:("xor","ebx,ebx"),
0xD1D99:("mov","byte ptr [ecx+0xde],al"),
0xD1D9F:("mov","eax,ecx"),
0xD1DA6:("xor","edx,edx"),
0xD1DA8:("mov","byte ptr [ecx+0xdf],al"),
0xD1DAE:("mov","eax,ecx"),
0xD1DBC:("xor","edx,edx"),
0xD1DBE:("mov","eax,ecx"),
0xD1DC5:("mov","eax,ecx"),
0xD1DC7:("xor","edx,edx"),
0xD1DCE:("mov","eax,ecx"),
0xD1DD5:("mov","eax,ecx"),
0xD1DDC:("movzx","ax,byte ptr [ecx+0xf0]"),
0xD1DE4:("cmp","ax,word ptr [ecx+0xe9]"),
0xD1DEB:("jl","0xd1df4"),
0xD1DED:("mov","ax,word ptr [ecx+0xe9]"),
0xD1DF4:("mov","word ptr [ecx+0xf5],ax"),
0xD1DFB:("mov","eax,ecx"),
0xD1DFD:("xor","edx,edx"),
0xD1E04:("mov","eax,ecx"),
0xD1E0B:("xor","edx,edx"),
0xD1E0D:("mov","eax,ecx"),
0xD1E14:("mov","eax,ecx"),
0xD1E1B:("pop","edx"),
0xD1E1C:("pop","ecx"),
0xD1E1D:("pop","ebx"),0xD1E1E:("ret",""),
# Original worker mineral table read and bonuses
0xCEC9B:("movsx","eax,word ptr [eax+0x2]"),
0xCECA7:("movzx","eax,byte ptr [edx+eax*1+0xa]"),
0xCECAC:("movzx","dx,byte ptr [eax+0xcd4b5]"),
0xCECBD:("cmp","byte ptr [ecx+0x13a],0x0"),
0xCECD4:("cmp","byte ptr [ecx+0x13d],0x0"),
0xCECEB:("cmp","byte ptr [ecx+0x15a],0x0"),
0xCED03:("cmp","byte ptr [ecx+0x142],0x0"),
0xCED2A:("cmp","byte ptr [ecx+eax*1+0x183],0x3"),
0xCED42:("mov","eax,edx"),0xCED46:("ret",""),
# Original scientist bonuses & special planet table
0xCFDC7:("mov","edx,0x3"),
0xCFDD0:("mov","dword ptr [ebx],0x3"),
0xCFDD6:("cmp","byte ptr [eax+0x13a],0x0"),
0xCFDED:("cmp","byte ptr [eax+0x154],0x0"),
0xCFE05:("cmp","byte ptr [eax+0x149],0x0"),
0xCFE1E:("cmp","byte ptr [eax+0x159],0x0"),
0xCFE35:("movsx","eax,word ptr [eax+0x2]"),
0xCFE42:("mov","al,byte ptr [ecx+eax*1+0xf]"),
0xCFE46:("cmp","al,0xa"),
0xCFE4C:("cmp","al,0xb"),
0xCFE54:("inc","edx"),
0xCFE65:("add","edx,0x5"),
0xCFE73:("mov","eax,edx"),0xCFE76:("ret",""),
}
def loadcsv(filename):
    with (ROOT/"decompilation"/filename).open(newline="") as f:return list(csv.DictReader(f))
def ins(code,at):
    r=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
      f"--start-address=0x{at:x}",f"--stop-address=0x{at+16:x}",str(code)],
      capture_output=True,text=True,check=True)
    for line in r.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==at:return m[3].lower(),m[4].strip().lower()
    raise ValueError("Missing original CODE instruction at "+hex(at))
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original MOO2 v1.31 executable hash mismatch")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Original LE CODE length differs")
    allfunctions={r["name"]:r for r in loadcsv("functions.csv")}
    bodies=[]
    for name,start,length,sha in BODIES:
        f=allfunctions[name]
        if(int(f["offset"]),int(f["inferred_size"]))!=(start,length):
            raise ValueError("Original named function extent changed "+name)
        if hashlib.sha256(b[start:start+length]).hexdigest()!=sha:
            raise ValueError("Original entire function bytes changed "+name)
        bodies.append({"symbol":name,"CODE_offset":hex(start),
            "complete_body_bytes":length,"full_original_SHA256":sha})
    symbols={r["name"]:(r["segment"],int(r["offset"]))
             for r in loadcsv("symbols.csv")}
    if symbols.get("_minerals_per_mine")!=("1",MINERAL_AT):
        raise ValueError("Original Watcom mineral table symbol mismatch")
    if b[MINERAL_AT:MINERAL_AT+5]!=MINERAL_BYTES:
        raise ValueError("Original mineral table bytes differ")
    direct=[]
    for off,(name,target) in CALLS.items():
        got=ins(code,off)
        if got!=("call",target):
            raise ValueError(f"Original Watcom CODE {off:#x} call got {got}, expected {target}")
        fn=allfunctions.get(name)
        if fn and int(fn["offset"])!=int(target,16):
            raise ValueError("Original named call target disagrees with original functions.csv "+name)
        direct.append({"CODE_call_site":hex(off),"target":target,"source_symbol":name})
    for at,expected in OPCODES.items():
        got=ins(code,at)
        if got!=expected:
            raise ValueError(f"Original source opcode {at:#x}: {got} != {expected}")
    return {
      "original_executable_SHA256":EXE_SHA,
      "full_authenticated_named_function_bodies":bodies,
      "source_direct_call_sites":direct,
      "source_exact_opcode_checkpoints":len(OPCODES)+len(CALLS),
      "verified_original_mineral_table":{
       "CODE_offset":"0xcd4b5","values":list(MINERAL_BYTES),
       "sha256":hashlib.sha256(MINERAL_BYTES).hexdigest()
      },
      "pre_import_first_writes":"memset_ zero four bytes colony+0xef...+0xf2, then Food2 result low AL -> colony+0xdd, Worker result low AL -> +0xde, Research result low AL -> +0xdf",
      "environment_original":"original Colony_Environmental_Stuff_ is invoked between food and worker and recomputes original e0 and e2 based on colony/player/planet",
      "signed_cap_after_replicators":"after original Colony_Replicators_, output signed min(zeroextend BYTE+0xf0, signed WORD+0xe9) as low WORD+0xf5",
      "resolved_nested_math":["Colony_Food2_Per_Farmer_","Colony_Environmental_Stuff_","Colony_Industry_Per_Worker_","Colony_Research_Per_Scientist_"],
      "ten_unresolved_effects":["Colony_Morale_","Colony_Industry_Maintenance_","Colony_Industry_Production_","Colony_Food_Production_","Colony_Food_Maintenance_","Colony_Replicators_","Colony_Research_Production_","Colony_Industry_To_Tax_","Colony_BC_Production_","Colony_BC_Maintenance_"],
      "limitations":"original outer 198-byte function control and verified math rebuilt; ten named original economy callees are callbacks, no original DOS differential game-state execution"
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args();r=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
