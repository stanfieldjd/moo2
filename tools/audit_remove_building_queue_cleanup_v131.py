#!/usr/bin/env python3
"""Audit source original MOO2 v1.31 building queue cleanup and ship reset.

Original full-body hashes: Remove_Building_ 493 bytes, original
Delete_From_Colony_Queue_ 94 bytes, plus nested unnamed 99-byte
colony compactor at CODE 0xA20ED within the original named
Defragment_Queue_ extent beginning at 0xA20BD (147 bytes).
All named symbols and original DATA fields checked; all source-byte
instruction references verified by objdump against the executable's
unrelocated LE CODE object. Original DOS execution is NOT performed.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODIES=[
 ("Remove_Building_",0x45EA,493,
  "8e0eb8d52268bf214d1ce3ec73d0e9970f0b4db1b0d1cae035810ace87179875"),
 ("Delete_From_Colony_Queue_",0xA1E19,94,
  "f3826251d3060f54504bbd3cfefbfd77b33c9c55fbf3f535b57d6e94ffa14316"),
 ("Defragment_Queue_",0xA20BD,147,
  "3ca97f6084a35d60406c997248be503e05363c921d983818d9df3df48b67ef18"),
]
ANON=(0xA20ED,99,"df9b86299e8c3494ff2637537a06e8deb43904b78133246d157dc30078896821")
OPRE=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
  0x460A:("mov","byte ptr [esi+eax*1+0x136],0x0"),
  0x462A:("cmp","bx,0x28"),
  0x462E:("jb","0x45e4"),
  0x4630:("cmp","bx,0x29"),
  0x4634:("jbe","0x4681"),
  0x4642:("cmp","bx,0x16"),
  0x4648:("jbe","0x4721"),
  0x465A:("cmp","bx,0x8"),
  0x4660:("jbe","0x4681"),
  0x4681:("xor","esi,esi"),
  0x4683:("jmp","0x46ce"),
  0x4685:("movsx","eax,cx"),
  0x468B:("imul","eax,eax,0x169"),
  0x4691:("mov","edx,dword ptr ds:0x1ab18"),
  0x4699:("movsx","edx,si"),
  0x46A1:("movsx","eax,word ptr [eax+0x115]"),
  0x46A8:("cmp","eax,0xffffff9c"),
  0x46AB:("jg","0x46cd"),
  0x46AD:("add","eax,0x64"),
  0x46B0:("imul","eax,eax,0xffffff7f"),
  0x46B6:("mov","edi,dword ptr ds:0x1ff9c"),
  0x46BE:("cmp","byte ptr [edi+0x10],0x2"),
  0x46C2:("jb","0x46cd"),
  0x46C4:("mov","eax,dword ptr [ebp-0x4]"),
  0x46C7:("call","0xa1e19"),
  0x46CC:("dec","esi"),
  0x46CD:("inc","esi"),
  0x46CE:("cmp","si,0x7"),
  0x46D2:("jl","0x4685"),
  0x46D4:("movsx","edx,cx"),
  0x46E2:("movsx","esi,word ptr [edx+eax*1+0x2]"),
  0x46EF:("movzx","eax,byte ptr [esi+eax*1+0x2]"),
  0x46FF:("call","0xd5296"),
  0x4704:("cmp","bx,0x2d"),
  0x4721:("movsx","esi,cx"),
  0x4724:("xor","ebx,ebx"),
  0x4728:("imul","eax,esi,0x169"),
  0x473E:("movsx","eax,word ptr [eax+0x115]"),
  0x4745:("cmp","eax,0xffffff9c"),
  0x4748:("jg","0x476e"),
  0x474A:("add","eax,0x64"),
  0x474D:("imul","eax,eax,0xffffff7f"),
  0x4756:("mov","eax,ds:0x1ff9c"),
  0x475E:("cmp","byte ptr [eax+0x11],0x2"),
  0x4762:("jne","0x476e"),
  0x4764:("mov","edx,edi"),
  0x4766:("mov","eax,esi"),
  0x4768:("call","0xa1e19"),
  0x476D:("dec","ebx"),
  0x476E:("inc","ebx"),
  0x476F:("cmp","bx,0x7"),
  0x4773:("jl","0x4728"),
  0x4775:("jmp","0x45e4"),
  0xA1E19:("push","ebx"),
  0xA1E1C:("mov","ebx,eax"),
  0xA1E1E:("cwde",""),
  0xA1E1F:("imul","eax,eax,0x169"),
  0xA1E25:("mov","esi,dword ptr ds:0x1ab18"),
  0xA1E2B:("movsx","ecx,dx"),
  0xA1E32:("mov","ax,word ptr [esi+eax*2+0x115]"),
  0xA1E3A:("cmp","ecx,0xffffffff"),
  0xA1E3D:("je","0xa1e73"),
  0xA1E3F:("movsx","ecx,ax"),
  0xA1E42:("cmp","ecx,0xffffff9c"),
  0xA1E45:("jg","0xa1e68"),
  0xA1E47:("add","eax,0x64"),
  0xA1E4C:("imul","eax,eax,0xffffffff"),
  0xA1E4F:("cwde",""),
  0xA1E50:("imul","eax,eax,0x81"),
  0xA1E56:("mov","ecx,dword ptr ds:0x1ff9c"),
  0xA1E5C:("mov","byte ptr [ecx+eax*1+0x64],0x5"),
  0xA1E61:("mov","word ptr [ecx+eax*1+0x65],0xffff"),
  0xA1E68:("movsx","edx,dx"),
  0xA1E6B:("movsx","eax,bx"),
  0xA1E6E:("call","0xa20ed"),
  0xA1E73:("pop","esi"),
  0xA1E76:("ret",""),
  0xA20ED:("push","ebx"),
  0xA20F0:("mov","ebx,eax"),
  0xA20F2:("mov","ecx,edx"),
  0xA20F4:("jmp","0xa211d"),
  0xA20F6:("movsx","eax,bx"),
  0xA20F9:("imul","eax,eax,0x169"),
  0xA20FF:("mov","esi,dword ptr ds:0x1ab18"),
  0xA2107:("movsx","eax,cx"),
  0xA210E:("mov","si,word ptr [eax+0x117]"),
  0xA2115:("inc","ecx"),
  0xA2116:("mov","word ptr [eax+0x115],si"),
  0xA211D:("cmp","cx,0x6"),
  0xA2121:("jl","0xa20f6"),
  0xA2123:("movsx","eax,bx"),
  0xA2126:("imul","esi,eax,0x169"),
  0xA212C:("mov","eax,ds:0x1ab18"),
  0xA2133:("movsx","esi,dx"),
  0xA2136:("mov","word ptr [eax+0x121],0xffff"),
  0xA213F:("movsx","eax,word ptr [eax+esi*2+0x115]"),
  0xA2147:("cmp","eax,0xfffffff6"),
  0xA214A:("je","0xa20f2"),
  0xA214C:("pop","esi"),
  0xA214F:("ret",""),
}
def rows(path):
    with (ROOT/"decompilation"/path).open(newline="") as fp:return list(csv.DictReader(fp))
def ins(path,address):
    output=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
       f"--start-address=0x{address:x}",f"--stop-address=0x{address+15:x}",str(path)],
       check=True,capture_output=True,text=True).stdout
    for line in output.splitlines():
        m=OPRE.match(line)
        if m and int(m[1],16)==address:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Original CODE instruction missing: {address:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original v1.31 game SHA differs")
    b=code.read_bytes()
    if len(b)!=1410709:
        raise ValueError("Original LE CODE object length differs")
    fs={r["name"]:r for r in rows("functions.csv")}
    authenticated=[]
    for name,start,size,sha in BODIES:
        f=fs[name]
        if int(f["offset"])!=start or int(f["inferred_size"])!=size:
            raise ValueError(f"Original Watcom function extent mismatch: {name}")
        if hashlib.sha256(b[start:start+size]).hexdigest()!=sha:
            raise ValueError(f"Complete original source-byte hash differs: {name}")
        authenticated.append({"original_symbol":name,"CODE_offset":hex(start),
                              "size_bytes":size,"complete_body_sha256":sha})
    start,size,sha=ANON
    if hashlib.sha256(b[start:start+size]).hexdigest()!=sha:
        raise ValueError("Anonymous original 0xA20ED queue shift body differs")
    if not(BODIES[2][1] <= start and start+size <= BODIES[2][1]+BODIES[2][2]):
        raise ValueError("Anonymous queue shift outside named Defragment_Queue_ extent")
    globals={r["name"]:int(r["offset"]) for r in rows("symbols.csv") if r["segment"]=="2"}
    for name,at in [("_colony",0x1AB18),("_ship",0x1FF9C),("_planet",0x1B0D4),("_star",0x1B06C)]:
        if globals.get(name)!=at:
            raise ValueError(f"Original Watcom DATA symbol mismatch {name}")
    for callee,at in [("Compute_Star_Colony_Stuff_",0xD5296)]:
        if int(fs[callee]["offset"])!=at:
            raise ValueError(f"Original named CODE helper mismatch {callee}")
    for at,expected in OPS.items():
        observed=ins(code,at)
        if observed!=expected:
            raise ValueError(f"Original opcode mismatch at {at:#x}: observed {observed}, expected {expected}")
    return {
        "original_executable_SHA256":EXE_SHA,
        "verified_original_named_function_bodies":authenticated,
        "anonymous_colony_queue_compactor":{"CODE_offset":hex(start),"length":size,
             "complete_body_sha256":sha,
             "within_named_interval":"Defragment_Queue_",
             "important_distinction":"Named Defragment_Queue_ starts 0xA20BD and handles separate global queue; Delete_From_Colony_Queue_ CALL is exactly 0xA20ED"},
        "original_instruction_anchors_verified":len(OPS),
        "remove_building_queue_scan_building_ids":[8,22,40,41],
        "star_recompute_after_deletions_for":[8,40,41],
        "no_star_recompute_for":[22],
        "seven_slot_scan":"colony WORDs from +0x115 to +0x121, slots0..6; signed <=-100 encodes ship index -(value+100)",
        "ship_source_record_stride":129,
        "ship_status_selection":"IDs8/40/41 ship BYTE+0x10 >=2, ID22 ship BYTE+0x11 ==2",
        "delete_original_ship_state":"for encoded ship queue slot, _ship[ship_id].BYTE+0x64=5 and WORD+0x65=-1",
        "queue_compaction":"shift queue WORD[i+1] into [i] from removed index through 5, set WORD[6]=-1, repeat while current selected slot == -10",
        "host_safety":"C derivatives bound indexes, expose callback failure and maximum deletions; original DOS does not validate these conditions",
        "scope":"authenticated original source bytes and branch/inner delete source reconstruction; star recomputation remains an explicit named callback, full Remove_Building_ still incomplete"
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
