#!/usr/bin/env python3
"""Reproducibly audit v1.31 CFG gains from classifying objdump byte-only rows first.

The original-byte-verified parser now treats an instruction continuation line
as bytes, not as an accidental one-byte mnemonic (e.g. 'ff'). The tests
compare GitHub's immutable previous CFG, the resynchronized original CODE
disassembly and regenerated source-authenticated whole-executable CFG.
Measurements count function/instruction *memberships*, not native gameplay.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"decompilation"
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BASELINE="8998afc20a4d3bae68cd81f26cf03f6a61209445"
CRITICAL={
 0x76240:("66c705ca190200ffff",0x76247,"ffff"),
 0x379A9:("66c705f4180200feff",0x379B0,"feff"),
 0x3317B:("66c704456ca90100f6ff",0x33182,"00f6ff"),
 0xDFB9:("66c70596210200ffff",0xDFC0,"ffff"),
 0xE045:("66c70596210200ffff",0xE04C,"ffff"),
 0x36CE3:("66c7844ea8490100ffff",0x36CEA,"00ffff"),
 0xC4817:("66c78564ffffffff",0xC481E,"ffff")
}
REQUIRED={
 "Do_Combat_Turn_":1600,"Tactical_Combat_":1100,"Main_Screen_":1000,
 "Get_Net_Diplomacy_Choices_":600,"Interpret_Mouse_Input_":1500,
 "Fleet_Screen_":600
}
EXTRA_SITES=[0xE198,0xE3C1,0xEBB7,0x12836,0x3352D,0x36D9F,0x117190]

def sha(b):return hashlib.sha256(b).hexdigest()

def previous(path):
    return subprocess.check_output(["git","-C",str(ROOT),"show",f"{BASELINE}:{path}"])

def read_cfg(raw):
    rr=list(csv.DictReader(io.StringIO(raw.decode())))
    result={(x["name"],x["offset"]):x for x in rr}
    if len(rr)!=len(result):raise ValueError("Duplicate CODE function identifiers")
    return result

def verify_raw_wrapped_instructions(code):
    dis=(D/"code_object_1_resynced.disasm")
    text=dis.read_text(errors="replace")
    # Anchored independent text patterns: first mnemonic-bearing line and
    # subsequent byte-only row. These are real original machine bytes, not
    # new guessed jump targets or reinterpretations of inline switch data.
    rawrow=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s*)+)$',re.I)
    seen={}
    for line in text.splitlines():
        m=rawrow.match(line)
        if m:
            addr=int(m.group(1),16)
            seen[addr]=bytes.fromhex(m.group(2).strip()).hex()
    for at,(expected,continuation,bytestr) in CRITICAL.items():
        binary=bytes.fromhex(expected)
        if code[at:at+len(binary)]!=binary:
            raise ValueError(f"Original complete x86 instruction bytes changed: {at:#x}")
        if seen.get(continuation)!=bytestr:
            raise ValueError(f"Original byte-only continuation is missing: {continuation:#x}")
        if not at<continuation<at+len(binary):
            raise ValueError("Continuation not interior to source original x86 instruction")
    return len(seen)

def audit(exe,code):
    image=code.read_bytes()
    if len(image)!=1410709 or sha(image)!=CODE_SHA or sha(exe.read_bytes())!=EXE_SHA:
        raise ValueError("Original DOS v1.31 EXE and CODE fingerprints changed")
    rawrow_count=verify_raw_wrapped_instructions(image)
    old=read_cfg(previous("decompilation/function_cfg_extents.csv"))
    new=read_cfg((D/"function_cfg_extents.csv").read_bytes())
    oldmeta=json.loads(previous("decompilation/function_cfg_extents.json"))
    newmeta=json.loads((D/"function_cfg_extents.json").read_text())
    if set(old)!=set(new) or len(old)!=5635:
        raise ValueError("Function name-offset identities not preserved")
    deltas=[]
    for key,before in old.items():
        after=new[key]
        delta=int(after["reachable_instructions"])-int(before["reachable_instructions"])
        if delta:
            deltas.append({
             "name":before["name"],"CODE_offset":int(before["offset"]),
             "original_provisional_bytes":int(before["inferred_size"]),
             "before_instructions":int(before["reachable_instructions"]),
             "after_instructions":int(after["reachable_instructions"]),
             "delta_memberships":delta,
             "before_status":before["status"],"after_status":after["status"],
             "before_unresolved":int(before["unresolved_edges"]),
             "after_unresolved":int(after["unresolved_edges"])})
    by_name={r["name"]:r for r in deltas}
    for fn,min_gain in REQUIRED.items():
        if by_name[fn]["delta_memberships"]<min_gain:
            raise ValueError("Source target function didn't recover expected original code: "+fn)
        if by_name[fn]["after_unresolved"]!=0:
            raise ValueError("Source target still has unresolved edges: "+fn)
    before_total=sum(int(r["reachable_instructions"]) for r in old.values())
    after_total=sum(int(r["reachable_instructions"]) for r in new.values())
    if (before_total,after_total)!=(372703,395671):
        raise ValueError("Baseline/current CFG membership counts changed")
    if (oldmeta["instruction_records"],newmeta["instruction_records"])!=(408409,407618):
        raise ValueError("Expected bogus instruction-entry correction not found")
    if (oldmeta["recombined_objdump_continuation_rows"],
        newmeta["recombined_objdump_continuation_rows"])!=(6931,7722):
        raise ValueError("Original continuation accounting unexpectedly changed")
    if oldmeta["recombined_objdump_continuation_bytes"]!=10646 or newmeta["recombined_objdump_continuation_bytes"]!=12398:
        raise ValueError("Expected original continuation byte count changed")
    if newmeta["orphan_objdump_continuation_rows"]!=0:
        raise ValueError("There are unmatched source continuation rows")
    if after_total!=newmeta["cfg_membership_records"] or before_total!=oldmeta["cfg_membership_records"]:
        raise ValueError("Per-function sums differ from exact CFG manifest")
    # Verified case-dispatch reachability: source cases unchanged; downstream
    # byte-row parser repair reaches six formerly blocked site instructions.
    with (D/"function_cfg_membership.csv").open(newline="") as f:
        reachable={int(r["instruction_offset"]) for r in csv.DictReader(f)}
    now_reached=[hex(s) for s in EXTRA_SITES if s in reachable]
    still_not=[hex(s) for s in EXTRA_SITES if s not in reachable]
    if now_reached!=[hex(s) for s in EXTRA_SITES[:-1]] or still_not!=[hex(EXTRA_SITES[-1])]:
        raise ValueError("Known original switch recoveries changed")
    gains=sorted((r for r in deltas if r["delta_memberships"]>0),
        key=lambda r:(-r["delta_memberships"],r["CODE_offset"]))
    losses=sorted((r for r in deltas if r["delta_memberships"]<0),
        key=lambda r:(r["delta_memberships"],r["CODE_offset"]))
    plus=sum(x["delta_memberships"] for x in gains)
    minus=sum(x["delta_memberships"] for x in losses)
    if plus!=23039 or minus!=-71 or len(gains)!=226 or len(losses)!=49:
        raise ValueError("Per-function pre-fix phantom instruction losses or actual gains differ")
    prev_unresolved=sum(int(r["unresolved_edges"]) for r in old.values())
    now_unresolved=sum(int(r["unresolved_edges"]) for r in new.values())
    if (prev_unresolved,now_unresolved)!=(446,45):
        raise ValueError("Source per-function unresolved edge counts differ")
    return {
      "status":"original-v131-verified-byte-only-continuation-CFG-recovery",
      "original_EXE_sha256":EXE_SHA,"original_CODE_sha256":CODE_SHA,
      "immutable_baseline_commit":BASELINE,
      "original_game_function_entries":len(old),
      "critical_original_split_instructions":[{"start":hex(k),
        "complete_source_machine_bytes":v[0],"source_continuation":hex(v[1]),
        "continuation_source_bytes":v[2]} for k,v in CRITICAL.items()],
      "source_byte_only_rows_in_disassembly":rawrow_count,
      "instruction_records_before":oldmeta["instruction_records"],
      "instruction_records_after":newmeta["instruction_records"],
      "continuation_rows_before":oldmeta["recombined_objdump_continuation_rows"],
      "continuation_rows_after":newmeta["recombined_objdump_continuation_rows"],
      "continuation_bytes_before":oldmeta["recombined_objdump_continuation_bytes"],
      "continuation_bytes_after":newmeta["recombined_objdump_continuation_bytes"],
      "orphans_after":0,
      "cfg_instruction_memberships_before":before_total,
      "cfg_instruction_memberships_after":after_total,
      "net_cfg_instruction_memberships_added":after_total-before_total,
      "positive_membership_gains":plus,
      "removed_old_phantom_or_obsolete_memberships":-minus,
      "affected_gain_function_count":len(gains),
      "affected_decrease_function_count":len(losses),
      "previous_functions_reaching_provisional_end":oldmeta["matches_provisional_end"],
      "current_functions_reaching_provisional_end":newmeta["matches_provisional_end"],
      "previous_functions_ending_short":oldmeta["ends_before_provisional_end"],
      "current_functions_ending_short":newmeta["ends_before_provisional_end"],
      "unresolved_edges_before":prev_unresolved,
      "unresolved_edges_after":now_unresolved,
      "previously_unreachable_source_verified_switch_sites_now_reached":now_reached,
      "source_verified_switch_sites_still_not_reached":still_not,
      "largest_verified_function_membership_gains":gains[:32],
      "largest_membership_decreases_due_to_reinterpretation":losses[:20],
      "scope_note":"Signed named-machine-code source CFG instruction memberships, not unique CODE bytes, game semantic completion, native browser compatibility or original DOS runtime parity. Negative changes are reported transparently; source byte-only rows can no longer be misread as one-byte machine mnemonics.",
      "next_priorities":["Source-recover Farload_Library_Data_ inline switch table alignment and remaining verified 0x117190 site","Investigate 45 remaining unresolved conservative CFG edges","Original DOS dynamic gameplay parity and native browser engine remain incomplete"],
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe",type=Path,required=True)
    ap.add_argument("--code",type=Path,required=True)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    report=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
