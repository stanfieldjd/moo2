#!/usr/bin/env python3
"""Source-authenticate MOO2 v1.31 Update_Ship_ETAs_ ETA iteration.

Checks SHA256 of original EXE, complete 253-byte named function,
the 422-byte named movement dependency, 7-byte external shared
Watcom LEAVE/POPs/RET, original Watcom symbols and DATA pointers,
and exact disassembled opcode locations. No original DOS dynamic
differential run; the C port uses a callback for movement physics.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
MAIN=(0xF041C,253,"5a1ebf719a02098beadf2b344252ce74850a8f6fc2c978dbb0f21910b603e78b")
MOVE=(0xDBB0C,422,"01baaeca994622f9d2d56541ef9b5a5463ffdd619a20054c34c4230e8e2c64cb")
SHARED=(0xEF792,7,"1c903070ad87dea1760b46e99addec3215f3983c955b643356bd4e063a57466a")
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
  0xF041C:("push","ebx"),
  0xF041D:("push","ecx"),
  0xF041E:("push","edx"),
  0xF041F:("push","esi"),
  0xF0420:("push","edi"),
  0xF0421:("enter","0x1c,0x0"),
  0xF0425:("push","eax"),
  0xF0426:("movsx","eax,word ptr ds:0x21994"),
  0xF042D:("imul","eax,eax,0x81"),
  0xF0433:("mov","esi,dword ptr ds:0x1ff9c"),
  0xF043B:("jmp","0xf0508"),
  0xF0440:("sub","esi,0x81"),
  0xF0446:("cmp","byte ptr [esi+0x64],0x2"),
  0xF044A:("je","0xf0456"),
  0xF044C:("cmp","byte ptr [esi+0x64],0x1"),
  0xF0450:("jne","0xf0508"),
  0xF0456:("movsx","ax,byte ptr [esi+0x63]"),
  0xF045B:("cmp","ax,word ptr [ebp-0x20]"),
  0xF045F:("je","0xf0508"),
  0xF0465:("mov","dl,byte ptr [esi+0x64]"),
  0xF0468:("mov","ax,word ptr [esi+0x65]"),
  0xF046C:("cmp","dl,0x1"),
  0xF0471:("jbe","0xf047a"),
  0xF0473:("cmp","dl,0x2"),
  0xF0476:("je","0xf0482"),
  0xF047A:("sub","eax,0x1f4"),
  0xF0482:("sub","eax,0x3e8"),
  0xF0488:("movsx","edi,ax"),
  0xF048B:("imul","eax,edi,0x71"),
  0xF048E:("mov","edx,dword ptr ds:0x1b06c"),
  0xF0496:("movsx","edx,word ptr [eax+0xf]"),
  0xF049A:("movsx","eax,word ptr [eax+0x11]"),
  0xF04A1:("mov","ax,word ptr [esi+0x67]"),
  0xF04A8:("mov","word ptr [ebp-0xc],0x0"),
  0xF04AE:("mov","ax,word ptr [esi+0x69]"),
  0xF04B8:("movsx","eax,word ptr [ebp-0x14]"),
  0xF04BC:("cmp","eax,dword ptr [ebp-0x1c]"),
  0xF04C1:("movsx","eax,word ptr [ebp-0x10]"),
  0xF04C5:("cmp","eax,dword ptr [ebp-0x18]"),
  0xF04C8:("je","0xf0502"),
  0xF04CA:("lea","eax,[ebp-0x8]"),
  0xF04CE:("cmp","byte ptr [esi+0x6b],0x0"),
  0xF04D2:("je","0xf04d8"),
  0xF04D4:("xor","eax,eax"),
  0xF04D8:("lea","eax,[ebp-0x4]"),
  0xF04DC:("lea","eax,[ebp-0x10]"),
  0xF04DF:("movsx","ebx,word ptr [ebp-0x10]"),
  0xF04E4:("lea","eax,[ebp-0x14]"),
  0xF04E7:("movsx","edx,word ptr [ebp-0x14]"),
  0xF04EC:("movzx","eax,byte ptr [esi+0x6c]"),
  0xF04F0:("mov","ecx,edi"),
  0xF04F3:("movsx","eax,byte ptr [esi+0x63]"),
  0xF04F7:("inc","word ptr [ebp-0xc]"),
  0xF04FB:("call","0xdbb0c"),
  0xF0500:("jmp","0xf04b8"),
  0xF0502:("mov","al,byte ptr [ebp-0xc]"),
  0xF0505:("mov","byte ptr [esi+0x6d],al"),
  0xF0508:("cmp","esi,dword ptr ds:0x1ff9c"),
  0xF050E:("ja","0xf0440"),
  0xF0514:("jmp","0xef792"),
  0xEF792:("leave",""),
  0xEF793:("pop","edi"),
  0xEF794:("pop","esi"),
  0xEF795:("pop","edx"),
  0xEF796:("pop","ecx"),
  0xEF797:("pop","ebx"),
  0xEF798:("ret",""),
  # verify exact named movement implementation entry without claiming
  # the 422-byte function's effects are already rebuilt.
  0xDBB0C:("push","esi"),
  0xDBB0D:("push","edi"),
  0xDBB0E:("enter","0x38,0x0"),
  0xDBB12:("mov","edi,dword ptr [ebp+0x14]"),
  0xDBB15:("mov","esi,dword ptr [ebp+0x18]"),
  0xDBCAC:("leave",""),
  0xDBCAD:("pop","edi"),
  0xDBCAE:("pop","esi"),
  0xDBCAF:("ret","0x14"),
}
def rows(name):
    with (ROOT/"decompilation"/name).open(newline="") as f:return list(csv.DictReader(f))
def op(code,at):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
        f"--start-address=0x{at:x}",f"--stop-address=0x{at+16:x}",str(code)],
        capture_output=True,text=True,check=True)
    for l in p.stdout.splitlines():
        m=RX.match(l)
        if m and int(m[1],16)==at:return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Original opcode absent at {at:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Wrong original game EXE")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Original CODE length changed")
    funcs={r["name"]:r for r in rows("functions.csv")}
    bodies=[]
    for name,(at,size,sha) in [("Update_Ship_ETAs_",MAIN),
                                ("Move_Player_1_Turn_To_Star_",MOVE)]:
        if(int(funcs[name]["offset"]),int(funcs[name]["inferred_size"]))!=(at,size):
            raise ValueError(f"Original named function extent changed {name}")
        if hashlib.sha256(b[at:at+size]).hexdigest()!=sha:
            raise ValueError(f"Original complete CODE body changed {name}")
        bodies.append({"name":name,"CODE_offset":hex(at),"body_bytes":size,
                       "original_SHA256":sha})
    at,size,sha=SHARED
    if hashlib.sha256(b[at:at+size]).hexdigest()!=sha:
        raise ValueError("External shared LEAVE POP RET changed")
    data={r["name"]:int(r["offset"]) for r in rows("symbols.csv")
          if r["segment"]=="2"}
    for n,at in [("_NUM_SHIPS",0x21994),("_ship",0x1FF9C),("_star",0x1B06C)]:
        if data.get(n)!=at:raise ValueError(f"Original named DATA differs {n}")
    for at,expected in OPS.items():
        got=op(code,at)
        if got!=expected:raise ValueError(f"Original {at:#x} {got} != {expected}")
    return {
        "original_EXE_SHA256":EXE_SHA,
        "original_named_function_bodies":bodies,
        "original_instruction_sites":len(OPS),
        "shared_external_return":{"original_CODE":"0xef792",
                                  "bytes":7,"original_SHA256":SHARED[2],
                                  "located_in_named_function":"Can_Order_Ship_"},
        "original_DATA":{"_NUM_SHIPS":"0x21994","_ship":"0x1ff9c",
                         "_star":"0x1b06c"},
        "reverse_source_scan":"_NUM_SHIPS signed WORD, ship stride 0x81, highest index first",
        "selected_ship_states":[1,2],
        "selected_ship_owner_condition":"signed ship BYTE+0x63 != input EAX low WORD (owner); equality skips",
        "target_star_decoder":"signed WORD(ship+0x65 - (state1?500:1000)), star stride 0x71",
        "target_coordinates":"signed WORDs star+0x0f and +0x11",
        "local_initial_coordinates":"signed WORDs ship+0x67 and +0x69; original ship coordinates are not written",
        "movement_call":"Move_Player_1_Turn_To_Star_ CODE 0xdbb0c, original 422 bytes; EAX owner, ECX star, EDX x, EBX y, 5 stack args: BYTE ship+0x6c, x*, y*, conditional optional byte*, required byte*",
        "optional_pointer":"source ship BYTE+0x6b zero => pointer; nonzero => NULL",
        "turn_count":"local WORD increment for each source movement call, ship BYTE+0x6d assigned only its low BYTE on arrival; already-arrived writes zero",
        "C_safety_differences":"invalid original pointers/indexes rejected, callback failures and iteration cap reported; no original DOS equivalence asserted for malformed state",
        "scope":"complete named ETA-source loop recovered with external original movement logic represented by typed callback; ship physics/collisions not yet reconstructed or dynamically compared with original DOS run"
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
