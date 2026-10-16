#!/usr/bin/env python3
"""Audit original v1.31 Enforce_Population_Limits_At_Colony_ source.

Source-authenticate full 489-byte population limit function, 81-byte
race capacity wrapper, 188-byte underlying size/climate routine,
190-byte original shuffle, 136-byte original food helper and 24-byte
Watcom memset. Verify real Watcom symbol extents, important stack
mark/limit logic, 42-capacity, population priority and zero-food
status writes with exact original i386 instruction checks.

This is a source-instruction audit, NOT original DOS differential
execution or proof of all gameplay behavior equivalence. Callbacks
still required for Shuffle_ and Size_And_Climate_Race_Pop_Limit_.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODIES=[
("Enforce_Population_Limits_At_Colony_",0xDC97C,489,"6e728e998d84105e2a3004ad1809c94ea1acf201db4ab907a6a935be54b92845"),
("Colony_Race_Pop_Limit_",0xD0C1D,81,"97d4044d83c3594792d5d159b6858599d63f153c9532081fa6aae13e70838e58"),
("Size_And_Climate_Race_Pop_Limit_",0xD0A93,188,"7c8629ad880163c090835f05037b1bde31bf058a183d30069b2af1b014eb032d"),
("Shuffle_",0xEEA82,190,"d5dc211bc4f2300aa5c591335beac6e905aac5d6134309eb71e0a1a26e28a604"),
("Colony_Food2_Per_Farmer_",0xCE03E,136,"6aef5f245db959b949a22eb0cfccd03b65db2c103a18c4dc47f5bbabcf9a04e4"),
("memset_",0x119C70,24,"e1bb125f736118af8cb392e308cbf68630169cada23d288f5adad0c3eb4fdc8c"),
]
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
 0xDC97C:("push","ebx"),0xDC97D:("push","ecx"),0xDC97E:("push","edx"),
 0xDC97F:("push","esi"),0xDC980:("push","edi"),
 0xDC981:("enter","0x74,0x0"),
 0xDC985:("mov","ecx,eax"),0xDC987:("mov","ebx,0x2a"),
 0xDC98C:("lea","esi,[eax+0xc]"),0xDC98F:("xor","edx,edx"),
 0xDC991:("lea","eax,[ebp-0x74]"),0xDC994:("call","0x119c70"),
 0xDC999:("mov","ebx,0x14"),0xDC99E:("lea","eax,[ebp-0x48]"),
 0xDC9A3:("call","0x119c70"),0xDC9A8:("mov","ebx,0x14"),
 0xDC9AD:("mov","edx,0xffffffff"),0xDC9B2:("lea","eax,[ebp-0x34]"),
 0xDC9B5:("call","0x119c70"),0xDC9BA:("movzx","eax,byte ptr [ecx+0xa]"),
 0xDC9BE:("shl","eax,0x2"),0xDC9C1:("lea","ebx,[esi+eax*1]"),
 0xDC9C6:("sub","ebx,0x4"),0xDC9C9:("mov","eax,dword ptr [ebx]"),
 0xDC9CB:("and","eax,0xf"),0xDC9CE:("inc","word ptr [ebp+eax*2-0x48]"),
 0xDC9D3:("mov","edx,dword ptr [ebx]"),
 0xDC9D5:("and","edx,0xf"),
 0xDC9D8:("movsx","eax,word ptr [ebp+edx*2-0x34]"),
 0xDC9DD:("cmp","eax,0xffffffff"),
 0xDC9E0:("jne","0xdca07"),
 0xDC9E2:("movsx","edx,dx"),0xDC9E5:("mov","eax,ecx"),
 0xDC9E7:("call","0xd0c1d"),
 0xDC9EC:("mov","edx,eax"),
 0xDC9EE:("mov","eax,dword ptr [ebx]"),
 0xDC9F0:("and","eax,0xf"),
 0xDC9F3:("mov","word ptr [ebp+eax*2-0x34],dx"),
 0xDC9F8:("mov","ebx,dword ptr [ebx]"),
 # original store indexed mark by returned capacity
 0xDCA07:("cmp","esi,ebx"),0xDCA09:("jb","0xdc9c6"),
 0xDCA0B:("mov","edx,0x4"),0xDCA10:("mov","eax,esi"),
 0xDCA12:("movzx","ebx,byte ptr [ecx+0xa]"),
 0xDCA16:("call","0xeea82"),
 0xDCA1B:("mov","eax,0x1"),
 0xDCA20:("cmp","byte ptr [ebp+eax*1-0x74],0x0"),
 0xDCA25:("je","0xdcb17"),
 0xDCA2B:("mov","byte ptr [ebp-0x4],0x0"),
 0xDCA2F:("mov","dword ptr [ebp-0x10],0x0"),
 0xDCA36:("mov","dword ptr [ebp-0x18],0x0"),
 0xDCA3D:("mov","dword ptr [ebp-0xc],0x0"),
 0xDCA44:("mov","dword ptr [ebp-0x20],0x0"),
 0xDCA4B:("movzx","edx,byte ptr [ecx+0xa]"),
 0xDCA4F:("mov","dword ptr [ebp-0x14],0x0"),
 0xDCA56:("shl","edx,0x2"),
 0xDCA59:("mov","dword ptr [ebp-0x1c],0x0"),
 0xDCA60:("lea","ebx,[esi+edx*1]"),
 0xDCA65:("sub","ebx,0x4"),
 0xDCA68:("mov","edx,dword ptr [ebx]"),
 0xDCA6A:("and","edx,0xf"),
 0xDCA6D:("mov","dword ptr [ebp-0x8],edx"),
 0xDCA70:("movsx","edx,word ptr [ebp+edx*2-0x34]"),
 0xDCA75:("cmp","edx,eax"),0xDCA77:("jg","0xdcab3"),
 0xDCA79:("inc","dword ptr [ebp-0x1c]"),
 0xDCA7C:("cmp","dword ptr [ebp-0x8],0x9"),
 0xDCA80:("jne","0xdca87"),0xDCA82:("mov","dword ptr [ebp-0x10],ebx"),
 0xDCA87:("cmp","dword ptr [ebp-0x8],0x8"),
 0xDCA8B:("jne","0xdca92"),0xDCA8D:("mov","dword ptr [ebp-0x20],ebx"),
 0xDCA92:("movsx","edx,byte ptr [ecx]"),
 0xDCA95:("cmp","edx,dword ptr [ebp-0x8]"),
 0xDCA98:("jne","0xdca9f"),0xDCA9A:("mov","dword ptr [ebp-0x14],ebx"),
 0xDCA9F:("mov","edi,dword ptr [ebx]"),
 0xDCAA1:("shl","edi,0x19"),0xDCAA4:("shr","edi,0x1d"),
 0xDCAA7:("cmp","edx,edi"),0xDCAA9:("jne","0xdcab0"),
 0xDCAAB:("mov","dword ptr [ebp-0xc],ebx"),
 0xDCAB0:("mov","dword ptr [ebp-0x18],ebx"),
 0xDCAB3:("cmp","esi,ebx"),0xDCAB5:("jb","0xdca65"),
 0xDCAB7:("cmp","eax,dword ptr [ebp-0x1c]"),
 0xDCABA:("jl","0xdcac2"),0xDCABC:("mov","byte ptr [ebp-0x4],0x1"),
 0xDCAC0:("jmp","0xdcb0d"),0xDCAC2:("dec","byte ptr [ecx+0xa]"),
 0xDCAC5:("cmp","dword ptr [ebp-0x10],0x0"),
 0xDCAC9:("je","0xdcad4"),0xDCACB:("movzx","edx,byte ptr [ecx+0xa]"),
 0xDCACF:("mov","ebx,dword ptr [ebp-0x10]"),
 0xDCAD4:("cmp","dword ptr [ebp-0x18],0x0"),
 0xDCAD8:("je","0xdcae3"),0xDCADA:("movzx","edx,byte ptr [ecx+0xa]"),
 0xDCADE:("mov","ebx,dword ptr [ebp-0x18]"),
 0xDCAE3:("cmp","dword ptr [ebp-0xc],0x0"),
 0xDCAE7:("je","0xdcaf2"),0xDCAE9:("movzx","edx,byte ptr [ecx+0xa]"),
 0xDCAED:("mov","ebx,dword ptr [ebp-0xc]"),
 0xDCAF2:("cmp","dword ptr [ebp-0x20],0x0"),
 0xDCAF6:("je","0xdcb01"),0xDCAF8:("movzx","edx,byte ptr [ecx+0xa]"),
 0xDCAFC:("mov","ebx,dword ptr [ebp-0x20]"),
 0xDCB01:("movzx","edx,byte ptr [ecx+0xa]"),
 0xDCB05:("mov","ebx,dword ptr [ebp-0x14]"),
 0xDCB08:("mov","edx,dword ptr [esi+edx*4]"),
 0xDCB0B:("mov","dword ptr [ebx],edx"),
 0xDCB0D:("cmp","byte ptr [ebp-0x4],0x0"),
 0xDCB11:("je","0xdca2f"),
 0xDCB17:("inc","eax"),0xDCB18:("cmp","eax,0x2a"),
 0xDCB1B:("jl","0xdca20"),
 0xDCB21:("mov","eax,ecx"),0xDCB23:("movsx","edx,byte ptr [ecx]"),
 0xDCB26:("xor","ebx,ebx"),0xDCB28:("call","0xce03e"),
 0xDCB2D:("test","ax,ax"),0xDCB30:("jne","0xdcb5e"),
 0xDCB32:("movzx","eax,byte ptr [ecx+0xa]"),
 0xDCB36:("shl","eax,0x2"),0xDCB39:("lea","ecx,[esi+eax*1]"),
 0xDCB3E:("sub","ecx,0x4"),0xDCB41:("test","word ptr [ecx],0x180"),
 0xDCB46:("jne","0xdcb5a"),0xDCB48:("mov","eax,dword ptr [ecx]"),
 0xDCB4A:("and","eax,0xf"),0xDCB4D:("cmp","eax,0x8"),
 0xDCB50:("je","0xdcb5a"),
 0xDCB52:("and","word ptr [ecx],0xfe7f"),
 0xDCB57:("or","byte ptr [ecx],0x80"),
 0xDCB5A:("cmp","esi,ecx"),0xDCB5C:("jb","0xdcb3e"),
 0xDCB5E:("leave",""),0xDCB5F:("pop","edi"),
 0xDCB60:("pop","esi"),0xDCB61:("pop","edx"),
 0xDCB62:("pop","ecx"),0xDCB63:("pop","ebx"),
 0xDCB64:("ret",""),
 # source 81-byte race cap wrapper
 0xD0C1D:("push","ebx"),0xD0C1E:("push","ecx"),
 0xD0C1F:("push","esi"),0xD0C20:("mov","ecx,eax"),
 0xD0C22:("movsx","ebx,dx"),0xD0C25:("movzx","edx,byte ptr [eax+0xe2]"),
 0xD0C2C:("movsx","eax,word ptr [eax+0x2]"),
 0xD0C30:("imul","esi,eax,0x11"),
 0xD0C33:("mov","eax,ds:0x1b0d4"),
 0xD0C38:("movzx","eax,byte ptr [esi+eax*1+0x5]"),
 0xD0C3D:("call","0xd0a93"),0xD0C42:("movsx","edx,byte ptr [ecx]"),
 0xD0C45:("imul","edx,edx,0xea9"),
 0xD0C4B:("mov","ebx,dword ptr ds:0x1ff98"),
 0xD0C51:("cwde",""),
 0xD0C52:("cmp","byte ptr [edx+ebx*1+0x11a],0x3"),
 0xD0C5A:("jne","0xd0c5f"),0xD0C5C:("add","eax,0x5"),
 0xD0C5F:("cmp","byte ptr [ecx+0x145],0x0"),
 0xD0C66:("je","0xd0c6a"),0xD0C68:("inc","eax"),
 0xD0C69:("inc","eax"),0xD0C6A:("pop","esi"),
 0xD0C6B:("pop","ecx"),0xD0C6C:("pop","ebx"),
 0xD0C6D:("ret","")
}
def csvrows(name):
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
    raise ValueError(f"Missing original Watcom opcode at {at:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original DOS source executable identity changed")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Original LE CODE size changed")
    symbols={r["name"]:r for r in csvrows("functions.csv")}
    bodies=[]
    for name,start,size,sha in BODIES:
        r=symbols[name]
        if(int(r["offset"]),int(r["inferred_size"]))!=(start,size):
            raise ValueError(f"Named original function extent changed: {name}")
        if hashlib.sha256(b[start:start+size]).hexdigest()!=sha:
            raise ValueError(f"Original named function body hash changed: {name}")
        bodies.append({"symbol":name,"original_CODE_offset":hex(start),
                 "complete_body_bytes":size,"original_complete_body_SHA256":sha})
    names={r["name"]:int(r["offset"]) for r in csvrows("symbols.csv")
           if r["segment"]=="2"}
    for name,off in [("_planet",0x1B0D4),("_player",0x1FF98)]:
        if names.get(name)!=off:
            raise ValueError(f"Original named DATA global mismatch: {name}")
    for address,expected in OPS.items():
        got=opcode(code,address)
        if got!=expected:
            raise ValueError(f"Source CODE {address:#x} {got} != {expected}")
    return {
      "original_executable_SHA256":EXE_SHA,
      "source_authenticated_complete_named_function_bodies":bodies,
      "verified_exact_i386_instruction_checkpoints":len(OPS),
      "named_DATA_globals":{"_planet":"0x1b0d4","_player":"0x1ff98"},
      "source_population_record":"BYTE colony+0x0a count; 4-byte records at colony+0x0c",
      "source_limits":"initial 42-byte mark array, two 20-byte WORD arrays for 10 type buckets, race capacity from 0xd0c1d",
      "source_first_scan":"reverse traverse population, tag=record DWORD&0xf, call Colony_Race_Pop_Limit_ once per encountered tag and mark BYTE at returned capacity",
      "shuffle":"Shuffle_ at 0xeea82 called with colony population pointer EAX, count EBX, four-byte stride EDX",
      "original_thresholds":"from t=1 through 41 (cap0 mark is not processed); remove one item and repeat same threshold until count of entries with their type limit<=t is no greater than t",
      "victim_priority_order":["type9","race-not-matching-colony-owner-neither-type8-nor-owner-code","record bits4..6 equal signed colony owner","type8","type matching colony owner"],
      "compaction":"decrement colony BYTE+0x0a then overwrite selected four-byte victim entry with last source population DWORD",
      "zero_food":"call Colony_Food2_Per_Farmer_ with EAX colony pointer, EDX signed owner, EBX0; if AX low WORD ==0, for each remaining record with WORD&0x180 ==0 and type !=8, set WORD=(WORD&0xFE7F)|0x80",
      "race_cap_wrapper":"Colony_Race_Pop_Limit_ passes planet BYTE+5 and colony BYTE+0xe2 with race index to Size_And_Climate_Race_Pop_Limit_ 0xd0a93, CWDE signextends returned AX, adds 5 for owning player tech BYTE+0x11a==3, adds 2 for colony BYTE+0x145 nonzero",
      "host_safety":"derived C bounds population count<=42, type0..9, capacity0..41; detects callback failure; these guards and no rollback differ from malformed DOS source",
      "unrecovered_effects":"original Shuffle_ 190-byte behavior and 188-byte Size_And_Climate_Race_Pop_Limit_ (and its callees) remain explicit callbacks, though both source bodies are authenticated",
      "scope":"complete observed 489-byte source control-flow reconstructed for safe original-like state, except external callback effects; no original DOS dynamic differential validation"
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
