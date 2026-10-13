#!/usr/bin/env python3
"""Evidence-backed triage of seven v1.31 CFG entry-decode exceptions.

Separates zero-filled boundary/data labels from a real runtime initializer and
from mixed initialized data plus 16-bit instructions. No output of game bytes.
"""
import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
PAD_NAMES={"___GETDSEnd_","__SegmentStartRR16","__IrqDataArrayRR16",
           "__SegmentStartPC32","__SegmentEndPC32"}
INIT_NAME="anon_runtime_0012F1D8"
MIXED_NAME="__VideoBasePD16"

def main(exe, code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError("Original v1.31 executable digest differs")
    blob=code.read_bytes()
    if len(blob)!=1410709:
        raise ValueError("Unexpected LE code-object size")
    with (ROOT/"decompilation/function_cfg_extents.csv").open(newline="") as f:
        flagged=[r for r in csv.DictReader(f) if r["status"]=="no_entry_decode"]
    if len(flagged)!=7 or {r["name"] for r in flagged}!=PAD_NAMES|{INIT_NAME,MIXED_NAME}:
        raise ValueError("Decode exception inventory changed")
    classifications=[]
    for row in flagged:
        off=int(row["offset"]);size=int(row["inferred_size"])
        chunk=blob[off:off+size]
        if len(chunk)!=size:
            raise ValueError("Entry crosses source-image bounds")
        if row["name"] in PAD_NAMES:
            if any(chunk):
                raise ValueError("Nonzero bytes detected in expected boundary/data label")
            status="zero-data-or-boundary-label"
            evidence=f"all {size} bytes zero"
        elif row["name"]==INIT_NAME:
            # Explicit x86 instructions: mov [absolute data address],SS; RET.
            # Watcom runtime initializer table identifies this exact start.
            if chunk!=bytes.fromhex("66 8c 15 34 ca 17 00 c3"):
                raise ValueError("Runtime init byte sequence does not match")
            with (ROOT/"decompilation/runtime_init_targets.csv").open(newline="") as f:
                valid=any(int(r["target_offset"])==off and r["function"]=="__InitRtns"
                          for r in csv.DictReader(f))
            if not valid:
                raise ValueError("Missing runtime init pointer to anonymous routine")
            status="valid-code-missing-from-resynchronized-export"
            evidence="initializer-table xref and eight-byte x86 mov/ret"
        else:
            if chunk[:8]!=bytes(8) or chunk[8:11]!=bytes.fromhex("55 8b ec"):
                raise ValueError("16-bit island prefix changed")
            p=subprocess.run(["objdump","-D","-M","intel","-b","binary",
                  "-m","i8086","--adjust-vma=0x10000",
                  f"--start-address={off+0x10008:x}",
                  f"--stop-address={off+0x10038:x}",str(code)],
                  capture_output=True,text=True,check=True)
            if "push   bp" not in p.stdout or "mov    bp,sp" not in p.stdout:
                raise ValueError("16-bit decoder did not recognize procedure prologue")
            status="data-prefix-followed-by-16-bit-code"
            evidence="eight zero bytes; i8086 procedure prologue at +8"
        classifications.append({"name":row["name"],"object_offset":hex(off),
           "interval_bytes":size,"status":status,"evidence":evidence})
    return {
        "original_sha256":SOURCE_SHA,
        "prior_32bit_decode_exceptions":len(flagged),
        "zero_filled_data_or_boundary":5,
        "runtime_initializer_to_add_to_code_corpus":1,
        "mixed_data_and_16bit_code_to_analyze_separately":1,
        "remaining_note":"Only this exact seven-entry inventory is triaged; 16-bit island routines and other CFG gaps remain to reconstruct.",
        "entries":classifications
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=main(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
