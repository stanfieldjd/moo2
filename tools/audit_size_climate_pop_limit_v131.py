#!/usr/bin/env python3
"""Audit original MOO2 v1.31 size/climate population math and BOTH tables.

Reads authenticated local ORION2.EXE, original LE CODE object and
original initialized LE DATA object. Verifies full 49-byte named
Size_And_Climate_Max_Population_ and full 188-byte named
Size_And_Climate_Race_Pop_Limit_, exact 5+16 lookup-table bytes,
table-related Watcom symbols, and original x86 instruction anchors.
No original DOS differential execution; no game assets distributed.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODIES=[
 ("Size_And_Climate_Max_Population_",0xD0A18,49,
  "405533edb6bdde5d69b314322b9a8a024bacd606529689968521f5c02b54bb14"),
 ("Size_And_Climate_Race_Pop_Limit_",0xD0A93,188,
  "7c8629ad880163c090835f05037b1bde31bf058a183d30069b2af1b014eb032d"),
]
SIZE_TABLE=(0x5806,bytes([5,10,15,20,25]))
CLIMATE_TABLE=(0xCD4EB,bytes([25,25,25,25,25,25,40,60,80,100,30,60,30,60,60,120]))
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
# Exact original 49-byte base algorithm
 0xD0A18:("push","ecx"),
 0xD0A19:("movzx","ecx,byte ptr [eax+0x5806]"),
 0xD0A20:("movzx","eax,byte ptr [edx+0xcd4eb]"),
 0xD0A27:("movzx","edx,bl"),
 0xD0A2A:("imul","edx,edx,0x19"),
 0xD0A2D:("add","eax,edx"),
 0xD0A2F:("cmp","eax,0x64"),
 0xD0A32:("jle","0xd0a39"),
 0xD0A34:("mov","eax,0x64"),
 0xD0A39:("imul","eax,ecx"),
 0xD0A3C:("add","eax,0x32"),
 0xD0A3F:("mov","ebx,0x64"),
 0xD0A44:("cdq",""),
 0xD0A45:("idiv","ebx"),
 0xD0A47:("pop","ecx"),
 0xD0A48:("ret",""),
# Original 188-byte race-specific source logic
 0xD0A93:("push","ecx"),
 0xD0A94:("push","esi"),
 0xD0A95:("push","edi"),
 0xD0A96:("enter","0x4,0x0"),
 0xD0A9A:("mov","esi,eax"),
 0xD0A9C:("mov","ecx,ebx"),
 0xD0A9E:("cmp","bx,0x8"),
 0xD0AA2:("jge","0xd0abc"),
 0xD0AA4:("movsx","ebx,bx"),
 0xD0AA7:("imul","ebx,ebx,0xea9"),
 0xD0AAD:("mov","eax,ds:0x1ff98"),
 0xD0AB2:("cmp","byte ptr [ebx+eax*1+0x8b6],0x0"),
 0xD0ABA:("jne","0xd0ac2"),
 0xD0ABC:("cmp","cx,0x8"),
 0xD0AC0:("jne","0xd0ac6"),
 0xD0AC2:("mov","al,0x1"),
 0xD0AC4:("jmp","0xd0ac8"),
 0xD0AC6:("xor","al,al"),
 0xD0AC8:("mov","byte ptr [ebp-0x4],al"),
 0xD0ACB:("movsx","ebx,cx"),
 0xD0ACE:("mov","eax,edx"),
 0xD0AD0:("cmp","ebx,0x8"),
 0xD0AD3:("jge","0xd0b10"),
 0xD0AD5:("imul","ebx,ebx,0xea9"),
 0xD0ADB:("mov","edi,dword ptr ds:0x1ff98"),
 0xD0AE1:("add","ebx,edi"),
 0xD0AE3:("cmp","byte ptr [ebx+0x8ab],0x0"),
 0xD0AEA:("je","0xd0b10"),
 0xD0AEC:("cmp","edx,0x5"),
 0xD0AEF:("jb","0xd0aff"),
 0xD0AF1:("jbe","0xd0b0b"),
 0xD0AF3:("cmp","edx,0x6"),
 0xD0AF6:("jbe","0xd0b04"),
 0xD0AF8:("cmp","edx,0x8"),
 0xD0AFB:("je","0xd0b0b"),
 0xD0AFD:("jmp","0xd0b10"),
 0xD0AFF:("cmp","edx,0x4"),
 0xD0B02:("jne","0xd0b10"),
 0xD0B04:("mov","eax,0x8"),
 0xD0B09:("jmp","0xd0b10"),
 0xD0B0B:("mov","eax,0x9"),
 0xD0B10:("movzx","ebx,byte ptr [ebp-0x4]"),
 0xD0B14:("mov","edx,eax"),
 0xD0B16:("mov","eax,esi"),
 0xD0B18:("call","0xd0a18"),
 0xD0B1D:("mov","ebx,eax"),
 0xD0B1F:("cmp","cx,0x8"),
 0xD0B23:("jge","0xd0b48"),
 0xD0B25:("movsx","edx,cx"),
 0xD0B28:("imul","ecx,edx,0xea9"),
 0xD0B2E:("mov","edx,dword ptr ds:0x1ff98"),
 0xD0B34:("cmp","byte ptr [ecx+edx*1+0x8ac],0x0"),
 0xD0B3C:("je","0xd0b48"),
 0xD0B3E:("mov","edx,esi"),
 0xD0B40:("inc","edx"),
 0xD0B41:("add","edx,edx"),
 0xD0B43:("movsx","ebx,dx"),
 0xD0B46:("add","ebx,eax"),
 0xD0B48:("mov","eax,ebx"),
 0xD0B4A:("leave",""),
 0xD0B4B:("pop","edi"),
 0xD0B4C:("pop","esi"),
 0xD0B4D:("pop","ecx"),
 0xD0B4E:("ret",""),
}
def table_hash(v):return hashlib.sha256(v).hexdigest()
def rows(name):
    with (ROOT/"decompilation"/name).open(newline="") as f:
        return list(csv.DictReader(f))
def opcode(code,at):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
       f"--start-address=0x{at:x}",f"--stop-address=0x{at+16:x}",str(code)],
       capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==at:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Original opcode not found at {at:#x}")
def audit(exe,code,initialized):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Authenticated original MOO2 executable hash differs")
    cb=code.read_bytes()
    db=initialized.read_bytes()
    if len(cb)!=1410709 or len(db)!=81920:
        raise ValueError("Wrong LE object sizes")
    original_names={r["name"]:r for r in rows("functions.csv")}
    out_bodies=[]
    for name,at,size,sha in BODIES:
        sym=original_names[name]
        if (int(sym["offset"]),int(sym["inferred_size"]))!=(at,size):
            raise ValueError("Original named Watcom CODE function extent changed "+name)
        if table_hash(cb[at:at+size])!=sha:
            raise ValueError("Original complete function body changed "+name)
        out_bodies.append({"original_name":name,"CODE_offset":hex(at),
                           "complete_body_bytes":size,"original_sha256":sha})
    sym={r["name"]:(r["segment"],int(r["offset"])) for r in rows("symbols.csv")}
    for name,expected in [
      ("_planet_max_population",("2",0x5806)),
      ("_climate_maintenance_modifiers",("1",0xCD4BA)),
      ("_player",("2",0x1FF98))
    ]:
        if sym.get(name)!=expected:
            raise ValueError(f"Original Watcom source symbol {name} differs {sym.get(name)}")
    ss,stable=SIZE_TABLE; cs,ctable=CLIMATE_TABLE
    if db[ss:ss+len(stable)]!=stable:
        raise ValueError("Original data-object planet-max-population lookup differs")
    if cb[cs:cs+len(ctable)]!=ctable:
        raise ValueError("Original code-object climate-percent lookup differs")
    for at,want in OPS.items():
        got=opcode(code,at)
        if got!=want:
            raise ValueError(f"Original CODE {at:#x}: {got} != {want}")
    return {
      "original_EXE_sha256":EXE_SHA,
      "authenticated_complete_function_bodies":out_bodies,
      "verified_exact_i386_opcodes":len(OPS),
      "lookups":{
        "_planet_max_population":{
           "source":"original initialized LE DATA segment 2","original_offset":"0x5806",
           "values":list(stable),"original_sha256":table_hash(stable)
        },
        "climate_percentage":{
           "source":"original LE CODE object 1 inside _climate_maintenance_modifiers region",
           "original_offset":"0xcd4eb","values":list(ctable),
           "original_sha256":table_hash(ctable)
        }
      },
      "max_population":"min(100,climate_percentage[environment]+25*bonus)*planet_max_population[size], add50, signed divide by100",
      "race0_7":"bonus if player BYTE+0x8b6 !=0; when player BYTE+0x8ab !=0: climate 4/6->8,5/8->9; player BYTE+0x8ac !=0 adds signed low WORD of 2*(size+1)",
      "race8":"automatic +25% climate bonus, no player record",
      "race9":"no climate bonus, no player record",
      "remaining_original_dependencies":"no other callees of these two source functions; upstream Colony_Race_Pop_Limit_ adds owner tech and building bonus",
      "host_limitations":"only source-valid size0..4, environment0..15, race0..9; no differential original DOS execution or proof of malformed-state equivalence"
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--data-initialized",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    out=audit(args.exe,args.code,args.data_initialized)
    if args.output:args.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
