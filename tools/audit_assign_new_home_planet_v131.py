#!/usr/bin/env python3
"""Authenticate complete original v1.31 Assign_New_Home_Planet_ source,
and the Remove_Building_(9) original caller register protocol.

No original game binaries committed; this verifies on local lawful
ORION2.EXE + unrelocated Watcom LE CODE object bytes.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
HOME=(0xDCB65,146,"b246802362b4d87ded1ea4efca66c4adaa18aa67f3f8b0ba6ba79b34374efd05")
BUILD=(0x45EA,493,"8e0eb8d52268bf214d1ce3ec73d0e9970f0b4db1b0d1cae035810ace87179875")
OP_RE=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
OPS={
  0x45F2:("mov","ecx,eax"),
  0x45F4:("mov","ebx,edx"),
  0x45F6:("movsx","edx,ax"),
  0x45F9:("imul","eax,edx,0x169"),
  0x4607:("movsx","esi,bx"),
  0x460A:("mov","byte ptr [esi+eax*1+0x136],0x0"),
  0x4662:("cmp","bx,0x9"),
  0x4666:("jbe","0x4674"),
  0x4674:("movsx","eax,byte ptr [eax]"),
  0x4677:("call","0xdcb65"),
  0x467C:("jmp","0x45e4"),
  0xDCB65:("push","ebx"),
  0xDCB66:("push","ecx"),
  0xDCB67:("push","esi"),
  0xDCB68:("push","edi"),
  0xDCB69:("enter","0x8,0x0"),
  0xDCB6D:("mov","esi,eax"),
  0xDCB6F:("mov","dword ptr [ebp-0x8],edx"),
  0xDCB72:("mov","ecx,0xffffffff"),
  0xDCB77:("movsx","eax,word ptr ds:0x21996"),
  0xDCB7E:("mov","dword ptr [ebp-0x4],0x0"),
  0xDCB85:("imul","ebx,eax,0x169"),
  0xDCB8B:("jmp","0xdcbb6"),
  0xDCB8D:("dec","eax"),
  0xDCB8E:("sub","ebx,0x169"),
  0xDCB94:("cmp","eax,dword ptr [ebp-0x8]"),
  0xDCB97:("je","0xdcbb6"),
  0xDCB99:("mov","edx,dword ptr ds:0x1ab18"),
  0xDCB9F:("add","edx,ebx"),
  0xDCBA1:("movsx","edi,byte ptr [edx]"),
  0xDCBA4:("cmp","esi,edi"),
  0xDCBA6:("jne","0xdcbb6"),
  0xDCBA8:("movzx","edx,byte ptr [edx+0xa]"),
  0xDCBAC:("cmp","edx,dword ptr [ebp-0x4]"),
  0xDCBAF:("jl","0xdcbb6"),
  0xDCBB1:("mov","dword ptr [ebp-0x4],edx"),
  0xDCBB4:("mov","ecx,eax"),
  0xDCBB6:("test","eax,eax"),
  0xDCBB8:("jg","0xdcb8d"),
  0xDCBBA:("imul","eax,esi,0xea9"),
  0xDCBC0:("cmp","ecx,0xffffffff"),
  0xDCBC3:("je","0xdcbe4"),
  0xDCBC5:("imul","edx,ecx,0x169"),
  0xDCBCB:("mov","ebx,dword ptr ds:0x1ab18"),
  0xDCBD1:("add","edx,ebx"),
  0xDCBD3:("mov","ebx,dword ptr ds:0x1ff98"),
  0xDCBD9:("mov","dx,word ptr [edx+0x2]"),
  0xDCBDD:("mov","word ptr [ebx+eax*1+0x29],dx"),
  0xDCBE2:("jmp","0xdcbf1"),
  0xDCBE4:("mov","edx,dword ptr ds:0x1ff98"),
  0xDCBEA:("mov","word ptr [edx+eax*1+0x29],0xffff"),
  0xDCBF1:("leave",""),
  0xDCBF2:("pop","edi"),
  0xDCBF3:("pop","esi"),
  0xDCBF4:("pop","ecx"),
  0xDCBF5:("pop","ebx"),
  0xDCBF6:("ret",""),
}
def rows(which):
    with (ROOT/"decompilation"/which).open(newline="") as f:return list(csv.DictReader(f))
def decode(code,address):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
       f"--start-address=0x{address:x}",f"--stop-address=0x{address+15:x}",str(code)],
       capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=OP_RE.match(line)
        if m and int(m[1],16)==address:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Unaligned original instruction at {address:#x}")
def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Wrong original executable")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Wrong original Watcom CODE length")
    named={r["name"]:r for r in rows("functions.csv")}
    details=[]
    for name,(start,n,sha) in [("Assign_New_Home_Planet_",HOME),("Remove_Building_",BUILD)]:
        row=named[name]
        if int(row["offset"])!=start or int(row["inferred_size"])!=n:
            raise ValueError(f"Function boundary changed: {name}")
        if hashlib.sha256(b[start:start+n]).hexdigest()!=sha:
            raise ValueError(f"Original full body SHA changed: {name}")
        details.append({"name":name,"offset":hex(start),"size_bytes":n,
                        "source_body_sha256":sha})
    globals={r["name"]:int(r["offset"]) for r in rows("symbols.csv") if r["segment"]=="2"}
    for name,off in [("_NUM_COLONIES",0x21996),("_colony",0x1AB18),("_player",0x1FF98)]:
        if globals.get(name)!=off:
            raise ValueError(f"Original named global changed: {name}")
    for at,wanted in OPS.items():
        got=decode(code,at)
        if got!=wanted:
            raise ValueError(f"Original instruction differs {at:#x}: {got} vs {wanted}")
    return {
      "original_exe_sha256":EXE_SHA,
      "entire_original_function_bodies":details,
      "original_instruction_checkpoints":len(OPS),
      "original_data_globals":{"_NUM_COLONIES":"0x21996","_colony":"0x1ab18","_player":"0x1ff98"},
      "caller_branch":"building_id==9 after original Remove_Building_ flag clear passes signed BYTE colony[0] as EAX and original sign-extended colony index as EDX into Assign_New_Home_Planet_",
      "home_search":"signed WORD _NUM_COLONIES original loops colony indexes from N-1 to 0, skipping EDX, matching signed owner BYTE+0, selecting max unsigned population BYTE+0x0a with >= tie rule (lowest index wins)",
      "destination":"WORD _player[owner*0xea9 + 0x29] = selected colony WORD+0x02 star ID, or 0xffff if no matching candidate",
      "scope":"complete original 146-byte home assignment reconstruction and building-9 call ABI; source-hash verified original CODE, tested derived C; not DOS dynamic differential execution or entire Remove_Building_ side effects"
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
