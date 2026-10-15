#!/usr/bin/env python3
"""Read-only original MOO2 v1.31 ship-movement/environment source audit.

Authenticates full 422-byte Move_Player_1_Turn_To_Star_ body, unnamed
114-byte per-nebula cell lookup CODE 0xDB9C8, named 66-byte
Point_Is_In_Some_Nebula_, named 73-byte warp interdictor, and
the original 155-byte isqrt_. Confirms exact source call destinations,
DATA symbols, and independent opcode checkpoints.
This does not execute DOS original or include proprietary game media.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODIES=[
 ("Move_Player_1_Turn_To_Star_",0xDBB0C,422,
  "01baaeca994622f9d2d56541ef9b5a5463ffdd619a20054c34c4230e8e2c64cb"),
 ("Point_Is_In_Some_Nebula_",0xDBA3A,66,
  "78203712436446f44a76e139d6b3a899fda9595d48ad58a0d415441ba558f307"),
 ("Point_Is_In_Warp_Field_Interdictor_Of_Star_",0xDBAC3,73,
  "c9c753a493dd59543b8929aadcc4ea4e02bdfad1ca32c227074b91a22dbfb305"),
 ("isqrt_",0x124C92,155,
  "712fab862da65b98b408b6bcaf4da8352fdb00306b0e40dfeeae616211d6c1b8")]
ANON=(0xDB9C8,114,"4cc37fb9b315c032a08140ed6bb70828d18cbab39d92f13629297a5ffc7e34a8")
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
# Point in one nebula: bitmap pitch and coordinate floor rounding
 0xDB9C8:("push","ecx"),
 0xDB9CB:("mov","edi,edx"),
 0xDB9CD:("movsx","esi,bx"),
 0xDB9D0:("mov","edx,dword ptr ds:0x1b068"),
 0xDB9D6:("lea","ebx,[esi+esi*4]"),
 0xDB9DB:("cwde",""),
 0xDB9DC:("movsx","edx,word ptr [ebx]"),
 0xDB9DF:("sub","eax,edx"),
 0xDB9E1:("mov","ecx,0x3"),
 0xDB9E7:("idiv","ecx"),
 0xDB9ED:("jl","0xdba34"),
 0xDB9EF:("movsx","edx,di"),
 0xDB9F2:("movsx","eax,word ptr [ebx+0x2]"),
 0xDB9FF:("cdq",""),
 0xDBA00:("idiv","ebx"),
 0xDBA06:("jl","0xdba34"),
 0xDBA0A:("shl","eax,0x4"),
 0xDBA0D:("mov","eax,dword ptr [eax+0x182a4]"),
 0xDBA13:("movsx","edx,word ptr [eax]"),
 0xDBA16:("movsx","esi,word ptr [eax+0x2]"),
 0xDBA1A:("cmp","ecx,edx"),
 0xDBA1C:("jge","0xdba34"),
 0xDBA20:("jge","0xdba34"),
 0xDBA22:("imul","edx,ebx"),
 0xDBA27:("cmp","byte ptr [edx+eax*1+0x10],0x5"),
 0xDBA2C:("jbe","0xdba34"),
 0xDBA2E:("mov","al,0x1"),
 0xDBA33:("ret",""),
 0xDBA34:("xor","al,al"),
 0xDBA39:("ret",""),
# named any-nebula scan
 0xDBA3A:("push","ebx"),
 0xDBA42:("mov","edi,eax"),
 0xDBA44:("mov","dword ptr [ebp-0x4],edx"),
 0xDBA47:("xor","cl,cl"),
 0xDBA49:("xor","esi,esi"),
 0xDBA4D:("movsx","edx,word ptr [ebp-0x4]"),
 0xDBA51:("movsx","ebx,si"),
 0xDBA54:("movsx","eax,di"),
 0xDBA57:("call","0xdb9c8"),
 0xDBA5C:("test","al,al"),
 0xDBA60:("mov","cl,0x1"),
 0xDBA62:("inc","esi"),
 0xDBA63:("test","cl,cl"),
 0xDBA67:("movzx","ax,byte ptr ds:0x21f0d"),
 0xDBA6F:("cmp","si,ax"),
 0xDBA72:("jl","0xdba4d"),
 0xDBA74:("mov","al,cl"),
 0xDBA7B:("ret",""),
# warp check
 0xDBAC3:("push","esi"),
 0xDBAC5:("mov","esi,eax"),
 0xDBAC7:("mov","edi,edx"),
 0xDBAC9:("mov","eax,ecx"),
 0xDBACB:("xor","bh,bh"),
 0xDBACD:("mov","dl,0x1"),
 0xDBACF:("mov","cl,bl"),
 0xDBAD1:("shl","dl,cl"),
 0xDBAD3:("not","dl"),
 0xDBAD5:("movzx","ecx,byte ptr [eax+0x39]"),
 0xDBADC:("test","edx,ecx"),
 0xDBADE:("je","0xdbb07"),
 0xDBAE0:("movsx","esi,si"),
 0xDBAE3:("movsx","edx,word ptr [eax+0xf]"),
 0xDBAEE:("movsx","eax,word ptr [eax+0x11]"),
 0xDBAF9:("imul","eax,esi"),
 0xDBAFE:("cmp","eax,0x1fa4"),
 0xDBB03:("jg","0xdbb07"),
 0xDBB05:("mov","bh,0x1"),
 0xDBB07:("mov","al,bh"),
 0xDBB0B:("ret",""),
# movement distance, rounded coordinate, and obstruction call sites
 0xDBB0C:("push","esi"),
 0xDBB0E:("enter","0x38,0x0"),
 0xDBB12:("mov","edi,dword ptr [ebp+0x14]"),
 0xDBB15:("mov","esi,dword ptr [ebp+0x18]"),
 0xDBB21:("imul","eax,ecx,0x71"),
 0xDBB24:("mov","edx,dword ptr ds:0x1b06c"),
 0xDBB2C:("movsx","edx,word ptr [eax+0xf]"),
 0xDBB30:("movsx","eax,word ptr [eax+0x11]"),
 0xDBB3E:("sub","edx,eax"),
 0xDBB43:("movsx","eax,bx"),
 0xDBB49:("sub","edx,eax"),
 0xDBB51:("imul","edx,edx"),
 0xDBB57:("imul","eax,eax"),
 0xDBB5A:("add","edx,eax"),
 0xDBB66:("call","0x124c92"),
 0xDBB6E:("mov","eax,dword ptr [ebp+0x10]"),
 0xDBB77:("test","ax,ax"),
 0xDBB7C:("mov","dword ptr [ebp-0x14],0x1"),
 0xDBB83:("imul","ecx,ecx,0x71"),
 0xDBB86:("mov","eax,dword ptr [ebp+0x20]"),
 0xDBB90:("mov","byte ptr [eax],0x0"),
 0xDBB9B:("cwde",""),
 0xDBB9C:("imul","edx,eax,0x384"),
 0xDBBA2:("imul","edx,eax"),
 0xDBBA5:("cmp","edx,dword ptr [ebp-0x28]"),
 0xDBBAA:("mov","eax,dword ptr [ebp-0x30]"),
 0xDBBAD:("mov","word ptr [edi],ax"),
 0xDBBB3:("mov","byte ptr [ebp-0x4],0x1"),
 0xDBBBC:("imul","eax,eax,0x1e"),
 0xDBBCA:("imul","eax,edx"),
 0xDBBD2:("idiv","dword ptr [ebp-0x38]"),
 0xDBBDB:("mov","word ptr [edi],dx"),
 0xDBBE9:("idiv","dword ptr [ebp-0x38]"),
 0xDBBF2:("mov","word ptr [edi],ax"),
 0xDBC0F:("idiv","dword ptr [ebp-0x38]"),
 0xDBC18:("mov","word ptr [esi],dx"),
 0xDBC2D:("idiv","dword ptr [ebp-0x38]"),
 0xDBC36:("mov","word ptr [esi],ax"),
 0xDBC39:("cmp","dword ptr [ebp+0x1c],0x0"),
 0xDBC45:("call","0xdba3a"),
 0xDBC4E:("mov","byte ptr [ebp-0x8],0x1"),
 0xDBC54:("movsx","ebx,word ptr [ebp-0xc]"),
 0xDBC58:("mov","ecx,dword ptr ds:0x1b06c"),
 0xDBC67:("call","0xdbac3"),
 0xDBC73:("mov","byte ptr [eax],0x1"),
 0xDBC76:("inc","dword ptr [ebp-0x1c]"),
 0xDBC7F:("cmp","byte ptr [ebp-0x8],0x0"),
 0xDBC85:("mov","eax,dword ptr [ebp+0x20]"),
 0xDBC8D:("cmp","byte ptr [ebp-0x4],0x0"),
 0xDBC96:("cmp","ax,word ptr [ebp-0x14]"),
 0xDBC9A:("jle","0xdbb9b"),
 0xDBCA0:("cmp","byte ptr [ebp-0x8],0x0"),
 0xDBCA6:("mov","eax,dword ptr [ebp+0x1c]"),
 0xDBCA9:("mov","byte ptr [eax],0x1"),
 0xDBCAF:("ret","0x14"),
}
def csvrows(filename):
    with (ROOT/"decompilation"/filename).open(newline="") as f:return list(csv.DictReader(f))
def op(code,at):
    o=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
        f"--start-address=0x{at:x}",f"--stop-address=0x{at+16:x}",str(code)],
        capture_output=True,text=True,check=True)
    for row in o.stdout.splitlines():
        m=RX.match(row)
        if m and int(m[1],16)==at:return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Not a source instruction {at:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original MOO2 v1.31 executable hash changed")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Original LE CODE size changed")
    named={r["name"]:r for r in csvrows("functions.csv")}
    functions=[]
    for name,start,size,sha in BODIES:
        row=named[name]
        if int(row["offset"])!=start or int(row["inferred_size"])!=size:
            raise ValueError(f"Watcom source function extent mismatch: {name}")
        if hashlib.sha256(b[start:start+size]).hexdigest()!=sha:
            raise ValueError(f"Original {name} body bytes changed")
        functions.append({"symbol":name,"CODE_offset":hex(start),
                          "body_bytes":size,"complete_source_body_SHA256":sha})
    start,size,sha=ANON
    if hashlib.sha256(b[start:start+size]).hexdigest()!=sha:
        raise ValueError("Original 114-byte unnamed per-nebula lookup mismatch")
    globals={r["name"]:int(r["offset"]) for r in csvrows("symbols.csv")
             if r["segment"]=="2"}
    for name,addr in [
        ("_nebula",0x1B068),("_nebula_pict_seg",0x18298),
        ("_NUM_NEBULAS",0x21F0D),("_star",0x1B06C)]:
        if globals.get(name)!=addr:
            raise ValueError(f"Original DATA symbol {name} != {addr:#x}")
    for at,want in OPS.items():
        got=op(code,at)
        if got!=want:
            raise ValueError(f"Original i386 CODE {at:#x}: {got} != {want}")
    return {
        "original_executable_SHA256":EXE_SHA,
        "original_complete_named_bodies":functions,
        "unnamed_per_nebula_body":{"CODE_offset":"0xdb9c8","size":114,
             "complete_source_body_SHA256":sha},
        "verified_exact_original_opcode_sites":len(OPS),
        "source_environment_calls":{
            "0xdba57":"0xdb9c8 per-nebula bitmap lookup",
            "0xdbb66":"0x124c92 isqrt",
            "0xdbc45":"0xdba3a Point_Is_In_Some_Nebula",
            "0xdbc67":"0xdbac3 warp interdictor"},
        "nebula_data":"_nebula pointer 5-byte records, _NUM_NEBULAS unsigned BYTE, _nebula_pict_seg original 16-byte records with bitmap pointer +12; signed coordinate differences divide by 3, bitmap BYTE+16 >5",
        "warp_data":"star BYTE+0x39 bit mask excludes player shift bit, signed squared distance <=8100 from signed star WORDs+0x0f,+0x11",
        "movement_data":"signed dx/dy, original isqrt of 32-bit squared-distance, steps of 30 times t; roundup (abs(delta)*t*30+sqrt-1)/sqrt, stop on destination/nebula/warp/maximum speed",
        "original_arrival_owner_local_effect":"CODE 0xdbba8 clears low16 of originally saved owner EAX on destination-arrival branch; subsequent warp check receives excluded owner 0 on that branch",
        "movement_stack_args":"speed, output X*, output Y*, optional nebula flag*, required warp flag*; original RET 0x14",
        "reconstruction_limitations":"valid original-format input and safe host bounds; original DOS dynamic differential execution not performed, original game assets are not included"
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
