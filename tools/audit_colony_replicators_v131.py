#!/usr/bin/env python3
"""Authenticated static branch/field reconstruction of v1.31 Colony_Replicators_.

Source SHA, complete Watcom function bytes, selected machine-code instructions,
branch targets, and controlled non-overflow fixture outputs are verified.
This is not original DOS runtime testing and is not source-level equivalence.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXE_SHA = "4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA = "f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
START, SIZE = 0xCF66F, 594
BODY_SHA = "3f8ba1af2428e08626ee378742b5045e0e9a8d6bb0a80dd5635dd27fd3bf5447"
EPILOGUE = 0xD1F97
RX = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$", re.I)
OPS = {
  0xCF66F: ("push", "ebx"),
  0xCF674: ("enter", "0x1c,0x0"),
  0xCF67A: ("mov", "byte ptr [eax+0x114],0x0"),
  0xCF681: ("cmp", "byte ptr [eax+0x146],0x0"),
  0xCF688: ("je", "0xd1f97"),
  0xCF68E: ("mov", "di,word ptr [eax+0xe9]"),
  0xCF695: ("mov", "si,word ptr [eax+0xe7]"),
  0xCF69C: ("add", "edi,edi"),
  0xCF69E: ("movzx", "ax,byte ptr [eax+0x100]"),
  0xCF6AA: ("movsx", "eax,dx"),
  0xCF6B0: ("sar", "eax,1"),
  0xCF6B2: ("xor", "ecx,ecx"),
  0xCF6B4: ("add", "esi,esi"),
  0xCF6B9: ("test", "ax,ax"),
  0xCF6BC: ("jle", "0xcf895"),
  0xCF6C2: ("movzx", "ax,byte ptr [ebx+0xfc]"),
  0xCF6CA: ("sub", "eax,esi"),
  0xCF6CC: ("cwde", ""),
  0xCF6CD: ("inc", "eax"),
  0xCF6D1: ("sar", "eax,1"),
  0xCF6D6: ("jle", "0xcf6ff"),
  0xCF6D9: ("movsx", "edx,word ptr [ebp-0x10]"),
  0xCF6DF: ("cmp", "eax,edx"),
  0xCF6E1: ("jle", "0xcf6e5"),
  0xCF6E3: ("mov", "eax,edx"),
  0xCF6E8: ("sar", "eax,1"),
  0xCF6EA: ("add", "eax,eax"),
  0xCF6EC: ("mov", "dword ptr [ebp-0x1c],eax"),
  0xCF6F4: ("movsx", "edi,di"),
  0xCF6F7: ("add", "ecx,dword ptr [ebp-0x1c]"),
  0xCF6FA: ("add", "esi,dword ptr [ebp-0x1c]"),
  0xCF6FD: ("sub", "edi,eax"),
  0xCF70B: ("movzx", "ax,byte ptr [ebx+0x101]"),
  0xCF715: ("movzx", "ax,byte ptr [ebx+0x102]"),
  0xCF71F: ("movsx", "eax,dx"),
  0xCF72D: ("jle", "0xcf895"),
  0xCF733: ("movzx", "ax,byte ptr [ebx+0xfc]"),
  0xCF73E: ("movzx", "ax,byte ptr [ebx+0xfd]"),
  0xCF749: ("sub", "eax,esi"),
  0xCF755: ("jle", "0xcf77f"),
  0xCF75B: ("movsx", "eax,word ptr [ebp-0x8]"),
  0xCF761: ("jl", "0xcf765"),
  0xCF76A: ("add", "eax,eax"),
  0xCF76C: ("mov", "dword ptr [ebp-0x18],eax"),
  0xCF774: ("movsx", "edi,di"),
  0xCF777: ("add", "ecx,dword ptr [ebp-0x18]"),
  0xCF77A: ("add", "esi,dword ptr [ebp-0x18]"),
  0xCF77D: ("sub", "edi,eax"),
  0xCF79F: ("movzx", "ax,byte ptr [ebx+0x103]"),
  0xCF7A9: ("movsx", "eax,dx"),
  0xCF7B7: ("jle", "0xcf895"),
  0xCF7BD: ("movzx", "ax,byte ptr [ebx+0xfc]"),
  0xCF7CB: ("movzx", "ax,byte ptr [ebx+0xfd]"),
  0xCF7D5: ("movzx", "ax,byte ptr [ebx+0xfe]"),
  0xCF7DF: ("sub", "eax,esi"),
  0xCF7EB: ("jle", "0xcf815"),
  0xCF7F1: ("movsx", "eax,word ptr [ebp-0xc]"),
  0xCF7F7: ("jl", "0xcf7fb"),
  0xCF800: ("add", "eax,eax"),
  0xCF802: ("mov", "dword ptr [ebp-0x14],eax"),
  0xCF80A: ("movsx", "edi,di"),
  0xCF80D: ("add", "ecx,dword ptr [ebp-0x14]"),
  0xCF810: ("add", "esi,dword ptr [ebp-0x14]"),
  0xCF813: ("sub", "edi,eax"),
  0xCF83D: ("movsx", "eax,di"),
  0xCF84A: ("jle", "0xcf895"),
  0xCF84C: ("movzx", "dx,byte ptr [ebx+0xfd]"),
  0xCF854: ("movzx", "ax,byte ptr [ebx+0xfc]"),
  0xCF85E: ("movzx", "ax,byte ptr [ebx+0xfe]"),
  0xCF868: ("movzx", "ax,byte ptr [ebx+0xff]"),
  0xCF872: ("sub", "eax,esi"),
  0xCF87E: ("jle", "0xcf895"),
  0xCF881: ("movsx", "edx,di"),
  0xCF886: ("cmp", "edx,eax"),
  0xCF888: ("jge", "0xcf88c"),
  0xCF88A: ("mov", "eax,edx"),
  0xCF88F: ("sar", "eax,1"),
  0xCF891: ("add", "eax,eax"),
  0xCF893: ("add", "ecx,eax"),
  0xCF895: ("movsx", "eax,cx"),
  0xCF89B: ("sar", "eax,1"),
  0xCF89D: ("mov", "byte ptr [ebx+0x114],al"),
  0xCF8A3: ("mov", "edx,eax"),
  0xCF8A5: ("movsx", "eax,word ptr [ebx+0xe7]"),
  0xCF8AC: ("sub", "word ptr [ebx+0xe9],cx"),
  0xCF8B3: ("add", "eax,edx"),
  0xCF8B5: ("mov", "word ptr [ebx+0xe7],ax"),
  0xCF8BC: ("jmp", "0xd1f97"),
  0xD1F97: ("leave", ""),
  0xD1F9D: ("ret", ""),
}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def s16(n):
    w=n & 0xffff
    return w if w < 0x8000 else w-0x10000

def trunc2(n):
    # Exact original CDQ; SUB EAX,EDX; SAR EAX,1 sequence.
    return (n + (1 if n<0 else 0)) >> 1

def demand_half(n):
    # Exact source CWDE; INC EAX; CDQ; SUB EAX,EDX; SAR EAX,1 sequence.
    v=s16(n)+1
    return (v+(1 if v<0 else 0)) >> 1

def controlled_model(enabled, e9, e7, counters, usage):
    """Source-derived stage model only for controlled non-overflow fixtures.

    e9/e7 are original WORD fields; counters contain BYTE +0x100..+0x103;
    usage contains BYTE +0xFC..+0xFF. Values outside the small fixture domain
    are NOT treated as validated original game states.
    """
    if len(counters)!=4 or len(usage)!=4:
        raise ValueError("four fields expected in each vector")
    if not (0<=e9<=2000 and 0<=e7<=2000):
        raise ValueError("controlled input beyond non-overflow test scope")
    if any(not 0<=x<=255 for x in (*counters,*usage)):
        raise ValueError("controlled fields must be BYTEs")
    if not enabled:
        return {"byte_114":0,"word_E9":e9,"word_E7":e7,"spent":0,
                "stage_spent":[0,0,0,0]}
    # Initial doubled WORD registers; their high halves have no independent
    # evidentiary status, and all branch calculations use the signed low WORD.
    edi=s16(e9*2)
    esi=s16(e7*2)
    consumed=0
    stage_spent=[0,0,0,0]
    caps=[(0,),(0,1,2),(0,1,2,3),(0,1,2,3)]
    sources=[(0,), (0,1), (0,1,2), (0,1,2,3)]
    for stage in range(4):
        cap=trunc2(s16(edi-sum(counters[i] for i in caps[stage])))
        if cap<=0:
            break  # all stage-capacity exits target shared final accounting
        remaining=s16(sum(usage[i] for i in sources[stage])-esi)
        demand=demand_half(remaining)
        if demand<=0:
            continue
        even=2*trunc2(min(cap,2*demand))
        if even<0 or even%2:
            raise AssertionError("source allocation is nonnegative and even")
        consumed+=even
        stage_spent[stage]=even
        if stage<3:
            edi=s16(edi-even//2)
            esi=s16(esi+even)
    made=trunc2(s16(consumed))
    return {"byte_114":made&255,"word_E9":(e9-consumed)&65535,
            "word_E7":(e7+made)&65535,"spent":consumed,
            "stage_spent":stage_spent}

def fixtures():
    u=lambda *v: list(v)
    z=u(0,0,0,0)
    assert controlled_model(False,100,7,z,u(10,10,10,10))=={
      "byte_114":0,"word_E9":100,"word_E7":7,"spent":0,"stage_spent":z}
    assert controlled_model(True,0,0,z,u(10,0,0,0))["spent"]==0
    for i in range(4):
        values=z.copy()
        # Ordered stages use +FC, +FD, +FE, +FF respectively.
        values[i]=10
        x=controlled_model(True,100,0,z,values)
        assert x["stage_spent"]==[10 if j==i else 0 for j in range(4)]
        assert (x["spent"],x["byte_114"],x["word_E9"],x["word_E7"])==(10,5,90,5)
    x=controlled_model(True,2,0,z,u(20,0,0,0))
    assert (x["spent"],x["byte_114"],x["word_E9"],x["word_E7"])==(2,1,0,1)
    x=controlled_model(True,100,0,z,u(4,10,0,0))
    assert x["stage_spent"]==[4,10,0,0] and x["spent"]==14
    x=controlled_model(True,100,0,u(210,0,0,0),u(10,0,0,0))
    assert x["spent"]==0
    return 9

def decode(code, address):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
        f"--start-address=0x{address:x}",f"--stop-address=0x{address+16:x}",str(code)],
        capture_output=True,text=True,check=True)
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==address:
            return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"missing instruction {address:#x}")

def branches(code):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
        f"--start-address=0x{START:x}",f"--stop-address=0x{START+SIZE:x}",str(code)],
        capture_output=True,text=True,check=True)
    paths=[]
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if not m: continue
        at=int(m[1],16)
        opcode=m[3].lower()
        if opcode=="call":
            raise ValueError(f"unexpected nested CALL at {at:#x}")
        if opcode.startswith("j"):
            target=m[4].strip().lower()
            if not re.fullmatch(r"0x[0-9a-f]+",target):
                raise ValueError(f"unresolved transfer at {at:#x}: {target}")
            dst=int(target,16)
            if not (START<=dst<START+SIZE or dst==EPILOGUE):
                raise ValueError(f"branch escapes function/tail at {at:#x}: {dst:#x}")
            paths.append({"at":hex(at),"opcode":opcode,"target":hex(dst)})
    return paths

def audit(exe,code):
    image=exe.read_bytes()
    source=code.read_bytes()
    if sha(image)!=EXE_SHA or len(source)!=1410709 or sha(source)!=CODE_SHA:
        raise ValueError("Original executable or Watcom LE CODE identity changed")
    with (ROOT/"decompilation/functions.csv").open(newline="") as f:
        fs={r["name"]:r for r in csv.DictReader(f)}
    r=fs["Colony_Replicators_"]
    if (int(r["offset"]),int(r["inferred_size"]))!=(START,SIZE):
        raise ValueError("original Watcom function extent changed")
    if sha(source[START:START+SIZE])!=BODY_SHA:
        raise ValueError("original entire named body changed")
    for at,expected in OPS.items():
        got=decode(code,at)
        if got!=expected:
            raise ValueError(f"machine opcode mismatch at {at:#x}: {got} != {expected}")
    targets=branches(code)
    checks=fixtures()
    return {
      "status":"source-verified-static-stage-reconstruction",
      "source_SHA256":EXE_SHA,"LE_CODE_SHA256":CODE_SHA,
      "complete_named_body":{"symbol":"Colony_Replicators_","offset":hex(START),
          "bytes":SIZE,"full_body_SHA256":BODY_SHA},
      "verified_machine_instruction_anchors":len(OPS),
      "observed_direct_control_transfers":targets,
      "nested_calls_in_named_body":0,
      "controlled_small_range_fixtures":checks,
      "early_exit":"always zero colony BYTE+0x114; if BYTE+0x146==0, jump to shared epilogue, preserve WORD+0xe9 and WORD+0xe7",
      "stage_gate_sequence":["0xcf6bc","0xcf72d","0xcf7b7","0xcf84a"],
      "source_reads":["WORD+0xe9","WORD+0xe7","BYTE+0x100..+0x103",
                     "BYTE+0xfc..+0xff","BYTE+0x146"],
      "normal_final_writes":["BYTE+0x114 = low byte of trunc_half(signed WORD spent)",
                             "WORD+0xe9 -= spent low WORD", "WORD+0xe7 += same truncated-half result low WORD"],
      "limits":["No dynamic DOS differential execution","Controlled model valid only for bounded non-overflow synthetic inputs",
                "Native gameplay and in-game state domain remain unverified"],
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    out=audit(args.exe,args.code)
    if args.output: args.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
