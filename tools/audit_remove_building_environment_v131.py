#!/usr/bin/env python3
"""Audit exact original MOO2 v1.31 Remove_Building_ environmental branch.

Verifies complete original Watcom CODE hashes of Remove_Building_,
First_Prod_Colony_Queue_Slot_, Delete_Prod_From_Colony_Queue_,
Delete_From_Colony_Queue_, Colony_Environmental_Stuff_,
Enforce_Population_Limits_At_Colony_, and Colony_Calculation_,
plus exact original x86 instruction checkpoints and DATA globals.

The C reconstruction specializes original Delete_Prod(...,44) via
source-proven positive-item exact-match semantics. Colony food per
farmer, population limits, and downstream calculation are not claimed
as fully reimplemented here. No original DOS dynamic execution.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
BODIES=[
 ("Remove_Building_",0x45EA,493,"8e0eb8d52268bf214d1ce3ec73d0e9970f0b4db1b0d1cae035810ace87179875"),
 ("First_Prod_Colony_Queue_Slot_",0xA1C5D,250,"11867a68c2ee5ba78c659d3427ce47578b18c2eaa2fa0eea7cfaabb34f0f6a05"),
 ("Delete_Prod_From_Colony_Queue_",0xA206F,50,"ff7eaeb75eddf9e05c4f489a5ec8b2be1bc833b06cce80336e8ad75d483da4c9"),
 ("Delete_From_Colony_Queue_",0xA1E19,94,"f3826251d3060f54504bbd3cfefbfd77b33c9c55fbf3f535b57d6e94ffa14316"),
 ("Colony_Environmental_Stuff_",0xD1CED,108,"94c8b7df7075f34a74650d3dc72ff466c6d9e69d57afaaa2502679d16131a086"),
 ("Enforce_Population_Limits_At_Colony_",0xDC97C,489,"6e728e998d84105e2a3004ad1809c94ea1acf201db4ab907a6a935be54b92845"),
 ("Colony_Calculation_",0xD2A70,65,"e667850010cdc8cb620bb98fcc6fe0c2b12971f572a8c48930c88833b940d63d"),
]
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
 0x460A:("mov","byte ptr [esi+eax*1+0x136],0x0"),
 0x4618:("jbe","0x47aa"),
 0x4624:("jbe","0x477a"),
 0x464E:("cmp","bx,0x18"),
 0x4652:("jbe","0x477a"),
 0x477A:("movsx","esi,cx"),
 0x477D:("imul","eax,esi,0x169"),
 0x4783:("mov","edx,dword ptr ds:0x1ab18"),
 0x4789:("movsx","eax,word ptr [edx+eax*1+0x2]"),
 0x478E:("imul","eax,eax,0x11"),
 0x4791:("mov","edx,dword ptr ds:0x1b0d4"),
 0x4797:("cmp","byte ptr [edx+eax*1+0x8],0x2"),
 0x479C:("jae","0x47aa"),
 0x479E:("mov","edx,0x2c"),
 0x47A3:("mov","eax,esi"),
 0x47A5:("call","0xa206f"),
 0x47AA:("movsx","edx,cx"),
 0x47AD:("imul","esi,edx,0x169"),
 0x47B3:("mov","eax,ds:0x1ab18"),
 0x47B8:("add","eax,esi"),
 0x47BA:("call","0xd1ced"),
 0x47BF:("mov","eax,ds:0x1ab18"),
 0x47C4:("add","eax,esi"),
 0x47C6:("call","0xdc97c"),
 0x47CB:("mov","eax,edx"),
 0x47CD:("call","0xd2a70"),
 0x47D2:("jmp","0x45e4"),
 # Positive building/product ID44 in First_Prod selects exact WORD match.
 0xA1C61:("mov","ecx,eax"),
 0xA1C63:("xor","eax,eax"),
 0xA1C6A:("test","dx,dx"),
 0xA1C6D:("jle","0xa1c9c"),
 0xA1C6F:("cmp","dx,0x31"),
 0xA1C73:("jge","0xa1c9c"),
 0xA1C75:("movsx","esi,cx"),
 0xA1C89:("cmp","dx,word ptr [esi+ebx*2+0x115]"),
 0xA1C91:("jne","0xa1d42"),
 0xA1D42:("inc","eax"),
 0xA1D43:("cmp","ax,0x7"),
 0xA1D47:("jl","0xa1c6a"),
 0xA1D4D:("mov","eax,0xffffffff"),
 0xA206F:("push","ebx"),
 0xA2072:("mov","ecx,eax"),
 0xA2074:("mov","esi,edx"),
 0xA207A:("call","0xa1c5d"),
 0xA2085:("cmp","edx,0xffffffff"),
 0xA2088:("je","0xa1e73"),
 0xA2090:("call","0xa1e19"),
 0xA209A:("call","0xa1c5d"),
 0xA209F:("jmp","0xa2082"),
 0xA1E42:("cmp","ecx,0xffffff9c"),
 0xA1E45:("jg","0xa1e68"),
 0xA1E6E:("call","0xa20ed"),
 # Environment source: fallback +0xe2, colony food +0xe0.
 0xD1CED:("push","ebx"),
 0xD1CEF:("push","edx"),
 0xD1CF0:("mov","ecx,eax"),
 0xD1CF2:("movsx","eax,word ptr [eax+0x2]"),
 0xD1CF6:("imul","edx,eax,0x11"),
 0xD1CF9:("mov","eax,ds:0x1b0d4"),
 0xD1CFE:("mov","al,byte ptr [edx+eax*1+0x8]"),
 0xD1D02:("mov","byte ptr [ecx+0xe2],al"),
 0xD1D08:("cmp","al,0x1"),
 0xD1D0A:("jne","0xd1d32"),
 0xD1D0C:("cmp","byte ptr [ecx+0x14d],0x0"),
 0xD1D13:("jne","0xd1d2b"),
 0xD1D15:("cmp","byte ptr [ecx+0x14e],0x0"),
 0xD1D1C:("jne","0xd1d2b"),
 0xD1D1E:("cmp","al,al"),
 0xD1D20:("jne","0xd1d32"),
 0xD1D22:("cmp","byte ptr [ecx+0x152],0x0"),
 0xD1D29:("je","0xd1d32"),
 0xD1D2B:("mov","byte ptr [ecx+0xe2],0x2"),
 0xD1D32:("mov","eax,ecx"),
 0xD1D34:("movsx","edx,byte ptr [ecx]"),
 0xD1D37:("xor","ebx,ebx"),
 0xD1D39:("call","0xce03e"),
 0xD1D3E:("test","ax,ax"),
 0xD1D41:("jne","0xd1d4e"),
 0xD1D43:("mov","byte ptr [ecx+0xe0],0x0"),
 0xD1D4E:("mov","byte ptr [ecx+0xe0],0xff"),
 0xD1D4A:("pop","edx"),
 0xD1D55:("pop","edx"),
 0xD1D58:("ret",""),
 # Original Enforce_Population_Limits_At_Colony_ saves/restores EDX.
 0xDC97E:("push","edx"),
 0xDCB61:("pop","edx"),
 0xD2A70:("push","ebx"),
 0xD2A71:("push","edx"),
 0xD2A72:("cwde",""),
 0xD2A73:("imul","eax,eax,0x169"),
}
def csvrows(filename):
    with (ROOT/"decompilation"/filename).open(newline="") as f:return list(csv.DictReader(f))
def decode(code,at):
    r=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
       f"--start-address=0x{at:x}",f"--stop-address=0x{at+16:x}",str(code)],
       capture_output=True,text=True,check=True)
    for line in r.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==at:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Unrecognized original CODE instruction at {at:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Original v1.31 executable mismatch")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Original LE CODE length changed")
    funcs={r["name"]:r for r in csvrows("functions.csv")}
    rows=[]
    for name,off,size,sha in BODIES:
        r=funcs[name]
        if int(r["offset"])!=off or int(r["inferred_size"])!=size:
            raise ValueError(f"Original Watcom function extent changed {name}")
        if hashlib.sha256(b[off:off+size]).hexdigest()!=sha:
            raise ValueError(f"Original full source body mismatch {name}")
        rows.append({"symbol":name,"original_CODE_offset":hex(off),
                     "body_bytes":size,"original_complete_body_sha256":sha})
    globals={r["name"]:int(r["offset"]) for r in csvrows("symbols.csv")
             if r["segment"]=="2"}
    for name,addr in [("_colony",0x1AB18),("_planet",0x1B0D4)]:
        if globals.get(name)!=addr:
            raise ValueError(f"Original DATA pointer changed {name}")
    for at,expected in OPS.items():
        got=decode(code,at)
        if got!=expected:
            raise ValueError(f"Original x86 {at:#x}: {got} != {expected}")
    return {
      "original_executable_SHA256":EXE_SHA,
      "source_verified_complete_named_function_bodies":rows,
      "exact_original_opcode_checkpoints":len(OPS),
      "original_named_DATA":{"_colony":"0x1ab18","_planet":"0x1b0d4"},
      "building_ids":[15,23,24,28],
      "first_write":"colony[0x136+building_id]=0 at CODE 0x460a",
      "building15":"direct environmental+population-limits+colony-calculation path (CODE 0x47aa)",
      "building23_24_and_28":"if unsigned planet BYTE+8 <2, original Delete_Prod_From_Colony_Queue_(colony,44), then common environment/population/colony calculation",
      "product44_queue":"for positive DX44, First_Prod_Colony_Queue_Slot_ scans seven exact matching queue WORDs; repeated Delete_From_Colony_Queue_ compacts and removes -10 placeholders",
      "environmental_source":"colony+0xe2 starts planet BYTE+8; if value==1 and (colony+0x14d or +0x14e nonzero), replace with 2",
      "building_flag_prerequisites":"ID23 removal clears colony+0x14d, ID24 clears colony+0x14e; both flags are tested after that initial clear by the environmental function",
      "environmental_unreachable_conditional":"CODE 0xd1d1e CMP AL,AL; subsequent JNE at 0xd1d20 can never be taken; consequently colony+0x152 is irrelevant in the observed path",
      "food_state":"Colony_Food2_Per_Farmer_(colony pointer, signed colony owner, EBX0) at 0xce03e; low WORD zero => colony BYTE+0xe0=0 else 255",
      "shared_downstream_calls":"Colony_Environmental_Stuff_ 0xd1ced -> Enforce_Population_Limits_At_Colony_ 0xdc97c -> Colony_Calculation_ 0xd2a70",
      "original_register_preservation":"Environmental and population-limit routines push/pop EDX; final MOV EAX,EDX sends original colony index to Colony_Calculation_",
      "scope":"fully source-authenticated building dispatch, specialized queue purge, full environmental arithmetic with food callback; population limits, colony calculation and food per farmer source effects not yet replaced; no DOS dynamic differential execution"
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
