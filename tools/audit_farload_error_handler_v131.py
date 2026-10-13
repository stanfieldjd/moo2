#!/usr/bin/env python3
"""Verify original v1.31 Farload error codes and fatal error-handler flow.

Proves the loader's ten calls pass specific literal codes, that the
439-byte handler contains the original diagnostic dispatch, and that it
passes through Exit_With_Message_ -> exit_(1). Source metadata only.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
HANDLER=0x1173DC
HANDLER_END=0x117593
LOADER_ERROR_CALLS=[
    (0x116F6D,4),(0x116FDF,1),(0x11702D,1),
    (0x117066,7),(0x11708D,8),(0x117122,10),
    (0x11713B,9),(0x1171B3,3),(0x1171D9,5),(0x1171FF,5)
]
# Code dispatch is not a guarantee of a distinct printed message:
# code 6 has no special suffix and all routes still call Exit.
HANDLER_CASES={
    1:0x1174C2,2:0x1174D7,3:0x1174EC,4:0x117505,
    5:0x117517,7:0x117529,8:0x11753B,9:0x11754D,
    10:0x11755F,16:0x117571
}

def decode(code,start,end):
    run=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
       f"--start-address=0x{start:x}",f"--stop-address=0x{end:x}",str(code)],
       capture_output=True,text=True,check=True)
    out=[]
    for line in run.stdout.splitlines():
        m=RX.match(line)
        if m:out.append((int(m[1],16),m[3].lower(),m[4].strip().lower()))
    return out

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError("The source is not the original verified v1.31 executable")
    if code.stat().st_size!=1410709:raise ValueError("Code object size differs")
    with (ROOT/"decompilation/functions.csv").open(newline="") as fp:
        f={row["name"]:row for row in csv.DictReader(fp)}
    if (int(f["Error_Handler_"]["offset"])!=HANDLER or
        int(f["Error_Handler_"]["inferred_size"])!=439):
        raise ValueError("Handler symbol/extent changed")
    instructions=decode(code,HANDLER,HANDLER_END)
    byaddr={r[0]:r for r in instructions}
    if len(instructions)!=106 or instructions[0][0]!=HANDLER:
        raise ValueError("Error handler machine-code inventory differs")
    for k,a in HANDLER_CASES.items():
        if a not in byaddr:
            raise ValueError(f"Missing code {k} message-branch target at {a:#x}")
    fatal=byaddr.get(0x117587)
    if fatal!=(0x117587,"call","0x116487"):
        raise ValueError("Error handler no longer calls Exit_With_Message_")
    # Exit_With_Message_ has an observed MOV EAX,1 followed by CALL exit_.
    exitcall=decode(code,0x1164B9,0x1164C3)
    if exitcall[:2]!=[(0x1164B9,"mov","eax,0x1"),
                       (0x1164BE,"call","0x12f2f4")]:
        raise ValueError("Fatal helper no longer invokes exit_(1)")
    inst=decode(code,0x116F3B,0x117145)+decode(code,0x117155,0x117233)
    offsets={a:i for i,(a,_,_) in enumerate(inst)}
    recorded=[]
    for addr,number in LOADER_ERROR_CALLS:
        if addr not in offsets:
            raise ValueError("Error call absent from original loader")
        i=offsets[addr]
        if inst[i]!=(addr,"call",f"0x{HANDLER:x}"):
            raise ValueError(f"Wrong call target at {addr:#x}")
        # Watcom register EDX assigned error code before two or three
        # register-setup MOVs. Search backward no further than 4 opcodes.
        prior=inst[max(i-4,0):i]
        edx=[p for p in prior if p[1]=="mov" and p[2]==f"edx,0x{number:x}"]
        if len(edx)!=1:
            raise ValueError(f"Missing EDX error code {number} at {addr:#x}")
        recorded.append({"call_offset":hex(addr),"error_code":number})
    calls=[(a,op,arg) for a,op,arg in inst if op=="call" and arg==f"0x{HANDLER:x}"]
    if len(calls)!=len(recorded):
        raise ValueError("Unclassified loader error calls detected")
    return {
        "original_sha256":SOURCE_SHA,
        "handler_original_code_offset":hex(HANDLER),
        "handler_length_bytes":439,
        "decoded_handler_instructions":len(instructions),
        "handler_code_cases":{str(n):hex(a) for n,a in HANDLER_CASES.items()},
        "loader_direct_error_calls":len(recorded),
        "original_error_helper":"Error_Handler_ -> Exit_With_Message_ -> exit_(1)",
        "scope":"observed fatal call chain and literal error code source only; message-content semantics and all error-handler effects are not fully simulated",
        "loader_calls":recorded
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
