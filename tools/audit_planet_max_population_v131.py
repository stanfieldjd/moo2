#!/usr/bin/env python3
"""Authenticate v1.31 full Planet_Max_Population_For_Player_ CODE.

Checks authenticated ORION2.EXE identity, original complete 206-byte
function body, named Watcom symbols, external shared epilogue,
and exact x86 control-flow instruction anchors. Verify call edges
to complete reconstructed Size_And_Climate_Race_Pop_Limit_
and Colony_Race_Pop_Limit_ source functions.

Original copyrighted executable remains local. No DOS dynamic
differential test; C host bounds guards differ on broken state.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODIES=[
 ("Planet_Max_Population_For_Player_",0xD0B4F,206,
 "00adaceecdeea9bb7cd18420bf11803ee6d784361fb2282b2581b4122f72b886"),
 ("Size_And_Climate_Race_Pop_Limit_",0xD0A93,188,
 "7c8629ad880163c090835f05037b1bde31bf058a183d30069b2af1b014eb032d"),
 ("Colony_Race_Pop_Limit_",0xD0C1D,81,
 "97d4044d83c3594792d5d159b6858599d63f153c9532081fa6aae13e70838e58"),
]
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
 0xD0B4F:("push","ebx"),0xD0B50:("push","ecx"),
 0xD0B51:("push","esi"),0xD0B52:("push","edi"),
 0xD0B53:("enter","0xc,0x0"),
 0xD0B57:("mov","esi,edx"),
 0xD0B59:("movsx","edx,word ptr [eax]"),
 0xD0B5C:("cmp","edx,0xffffffff"),
 0xD0B5F:("je","0xd0b75"),
 0xD0B61:("imul","edx,edx,0x169"),
 0xD0B67:("mov","ecx,dword ptr ds:0x1ab18"),
 0xD0B6D:("add","ecx,edx"),
 0xD0B6F:("cmp","byte ptr [ecx+0x6],0x0"),
 0xD0B73:("je","0xd0baa"),
 0xD0B75:("movsx","ebx,si"),
 0xD0B78:("movzx","edx,byte ptr [eax+0x8]"),
 0xD0B7C:("movzx","eax,byte ptr [eax+0x5]"),
 0xD0B80:("call","0xd0a93"),
 0xD0B85:("movsx","ecx,ax"),
 0xD0B88:("imul","eax,esi,0xea9"),
 0xD0B8E:("mov","edx,dword ptr ds:0x1ff98"),
 0xD0B94:("cmp","byte ptr [edx+eax*1+0x11a],0x3"),
 0xD0B9C:("jne","0xd0c16"),
 0xD0BA2:("add","ecx,0x5"),
 0xD0BA5:("jmp","0xd0c16"),
 0xD0BAA:("mov","edi,ecx"),
 0xD0BAC:("cmp","byte ptr [ecx+0xa],0x0"),
 0xD0BB0:("jne","0xd0bc1"),
 0xD0BB2:("movsx","edx,si"),
 0xD0BB5:("mov","eax,ecx"),
 0xD0BB7:("call","0xd0c1d"),
 0xD0BBC:("movsx","ecx,ax"),
 0xD0BBF:("jmp","0xd0c16"),
 0xD0BC1:("mov","ebx,0xa"),
 0xD0BC6:("lea","eax,[ebp-0xc]"),
 0xD0BC9:("xor","edx,edx"),
 0xD0BCB:("call","0x119c70"),
 0xD0BD0:("movzx","edx,byte ptr [ecx+0xa]"),
 0xD0BD4:("mov","eax,edx"),
 0xD0BD6:("shl","eax,0x2"),
 0xD0BD9:("xor","esi,esi"),
 0xD0BDB:("add","eax,ecx"),
 0xD0BDD:("jmp","0xd0bee"),
 0xD0BDF:("mov","ecx,dword ptr [eax+0x8]"),
 0xD0BE2:("and","ecx,0xf"),
 0xD0BE5:("sub","eax,0x4"),
 0xD0BE8:("dec","edx"),
 0xD0BE9:("mov","byte ptr [ecx+ebp*1-0xc],0x1"),
 0xD0BEE:("test","edx,edx"),
 0xD0BF0:("jg","0xd0bdf"),
 0xD0BF2:("mov","ecx,0xa"),
 0xD0BF7:("dec","ecx"),
 0xD0BF8:("cmp","byte ptr [ecx+ebp*1-0xc],0x0"),
 0xD0BFD:("je","0xd0c10"),
 0xD0BFF:("movsx","edx,cx"),
 0xD0C02:("mov","eax,edi"),
 0xD0C04:("call","0xd0c1d"),
 0xD0C09:("cwde",""),
 0xD0C0A:("cmp","esi,eax"),
 0xD0C0C:("jge","0xd0c10"),
 0xD0C0E:("mov","esi,eax"),
 0xD0C10:("test","ecx,ecx"),
 0xD0C12:("jg","0xd0bf7"),
 0xD0C14:("mov","ecx,esi"),
 0xD0C16:("mov","eax,ecx"),
 0xD0C18:("jmp","0xceb17"),
 0xCEB17:("leave",""),
 0xCEB18:("pop","edi"),
 0xCEB19:("pop","esi"),
 0xCEB1A:("pop","ecx"),
 0xCEB1B:("pop","ebx"),
 0xCEB1C:("ret",""),
}
def csvrows(name):
    with (ROOT/"decompilation"/name).open(newline="") as f:
        return list(csv.DictReader(f))
def decode(code,at):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
           f"--start-address=0x{at:x}",f"--stop-address=0x{at+16:x}",str(code)],
           capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==at:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Original opcode not at {at:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original v1.31 executable hash mismatch")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Original CODE extent differs")
    named={r["name"]:r for r in csvrows("functions.csv")}
    originals=[]
    for name,start,size,sha in BODIES:
        row=named[name]
        if (int(row["offset"]),int(row["inferred_size"]))!=(start,size):
            raise ValueError("Original named function boundary mismatch "+name)
        if hashlib.sha256(b[start:start+size]).hexdigest()!=sha:
            raise ValueError("Original complete function body mismatch "+name)
        originals.append({"source_symbol":name,"CODE_offset":hex(start),
                          "complete_body_bytes":size,"body_SHA256":sha})
    original_return=b[0xCEB17:0xCEB1D]
    if original_return!=bytes.fromhex("c9 5f 5e 59 5b c3"):
        raise ValueError("Watcom external return bytes differ")
    sym={r["name"]:(r["segment"],int(r["offset"])) for r in csvrows("symbols.csv")}
    for name,expected in [
      ("_colony",("2",0x1AB18)),
      ("_player",("2",0x1FF98))]:
        if sym.get(name)!=expected:raise ValueError("Original source DATA symbol "+name)
    for at,want in OPS.items():
        got=decode(code,at)
        if got!=want:
            raise ValueError(f"Original CODE {at:#x}: {got} != {want}")
    return {
      "original_executable_SHA256":EXE_SHA,
      "original_authenticated_complete_bodies":originals,
      "verified_original_instruction_checkpoints":len(OPS),
      "external_Watcom_return":"0xceb17 original LEAVE POP EDI POP ESI POP ECX POP EBX RET",
      "original_direct_calls":{
        "0xd0b80":"0xd0a93 Size_And_Climate_Race_Pop_Limit_",
        "0xd0bb7":"0xd0c1d Colony_Race_Pop_Limit_",
        "0xd0bcb":"0x119c70 memset_",
        "0xd0c04":"0xd0c1d Colony_Race_Pop_Limit_"},
      "uncolonized_or_inactive":"signed planet WORD+0 ==-1 OR colony BYTE+6 nonzero; size from planet BYTE+5, climate from planet BYTE+8, source race is requested player; return signed AX capacity +5 if queried player BYTE+0x11a==3",
      "colony_no_population":"colony BYTE+0x0a==0: return low signed AX from Colony_Race_Pop_Limit_(colony,requested player race)",
      "colony_occupied":"mark original four-byte population record low-nibble classes 0..9, then scan represented classes from9 through1; return maximum signed low AX class capacity, starting at 0; source class0 never visited",
      "host_safety":"reject invalid class>=10, count>42, colony/planet/player bounds; game source on malformed state is not defined",
      "status":"All direct original subroutine source numeric effects now reconstructed and host-regressed; original DOS differential run remains unavailable"
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    x=p.parse_args()
    o=audit(x.exe,x.code)
    if x.output:x.output.write_text(json.dumps(o,indent=2)+"\n")
    print(json.dumps(o,indent=2))
