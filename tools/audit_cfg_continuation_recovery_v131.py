#!/usr/bin/env python3
"""Measure authenticated v1.31 full-CODE CFG gains from objdump continuation fix.

Uses immutable pre-fix Git commit as baseline. Reports *instruction membership*
and conservative function-end classifications, not semantic completion or
native gameplay coverage.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PRE_FIX_COMMIT="5dc3e36806c18123b3afaf80df98aaf438d5ef62"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CSV_REL="decompilation/function_cfg_extents.csv"
MAN_REL="decompilation/function_cfg_extents.json"
REQUIRED_GAINS={"Combat_Draw_View_Ship_":1000,"Compute_AI_Data_":1000,
                "Draw_Field_":1000,"Race_Selection_Screen_":400,
                "Strategic_Combat_":400,"Print_Main_Screen_Data_":500}
SOURCE_SPLIT={"instruction_CODE_address":0x32FCE,
              "original_complete_machine_bytes":"66c70455061202000000",
              "old_parser_instruction_bytes":7,
              "recombined_instruction_bytes":10}

def sha(b):return hashlib.sha256(b).hexdigest()
def baseline_file(path):
    p=subprocess.run(["git","-C",str(ROOT),"show",f"{PRE_FIX_COMMIT}:{path}"],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return p.stdout

def read_csv(b):
    data=list(csv.DictReader(io.StringIO(b.decode())))
    unique={(r["offset"],r["name"]):r for r in data}
    if len(data)!=len(unique):raise ValueError("duplicate name+offset in original manifest")
    return unique

def audit(exe,code):
    b=code.read_bytes()
    if len(b)!=1410709 or sha(b)!=CODE_SHA:raise ValueError("original CODE does not match official v1.31")
    if sha(exe.read_bytes())!=EXE_SHA:raise ValueError("original EXE fingerprint mismatch")
    check=SOURCE_SPLIT
    start=check["instruction_CODE_address"]
    if b[start:start+10].hex()!=check["original_complete_machine_bytes"]:
        raise ValueError("Original critical split instruction bytes differ")

    old=read_csv(baseline_file(CSV_REL))
    after=read_csv((ROOT/CSV_REL).read_bytes())
    old_manifest=json.loads(baseline_file(MAN_REL))
    now=json.loads((ROOT/MAN_REL).read_text())
    if set(old)!=set(after):
        raise ValueError("Function identity comparison mismatch")
    if len(old)!=5635 or len(after)!=5635:
        raise ValueError("Unexpected source function count")
    if (now["recombined_objdump_continuation_rows"]<=0
        or now["orphan_objdump_continuation_rows"]!=0):
        raise ValueError("Expected authenticated split-instruction repairs not seen")
    if now["instruction_records"]!=old_manifest["instruction_records"]:
        raise ValueError("Original source instruction-entry inventory changed")
    base_status=collections.Counter(r["status"] for r in old.values())
    new_status=collections.Counter(r["status"] for r in after.values())
    entries=[];decreased=[];improved=0
    for key,x in old.items():
        y=after[key]
        start_old=int(x["reachable_instructions"])
        new=int(y["reachable_instructions"])
        gain=new-start_old
        if gain<0:decreased.append({"name":x["name"],"loss":gain})
        if gain>0:improved+=1
        entries.append({
          "name":x["name"],"CODE_offset":int(x["offset"]),
          "original_provisional_bytes":int(x["inferred_size"]),
          "before_instructions":start_old,"after_instructions":new,
          "instruction_membership_gain":gain,
          "before_unresolved_edges":int(x["unresolved_edges"]),
          "after_unresolved_edges":int(y["unresolved_edges"]),
          "before_status":x["status"],"after_status":y["status"],
        })
    if decreased:raise ValueError("CFG regressed for some source entries")
    by_name={x["name"]:x for x in entries}
    for name,gain in REQUIRED_GAINS.items():
        if by_name[name]["instruction_membership_gain"]<gain:
            raise ValueError("Original large-function gain lost: "+name)
    old_count=sum(int(x["reachable_instructions"]) for x in old.values())
    new_count=sum(int(x["reachable_instructions"]) for x in after.values())
    if new_count!=now["cfg_membership_records"]:
        raise ValueError("New membership total differs from regenerating manifest")
    if old_count!=old_manifest["cfg_membership_records"]:
        raise ValueError("Original pre-fix membership manifest inconsistent")
    top=sorted((x for x in entries if x["instruction_membership_gain"]>0),
               key=lambda x:(-x["instruction_membership_gain"],x["CODE_offset"]))
    high_risk=sorted((x for x in entries
                     if x["after_unresolved_edges"] or "shorter" in x["after_status"]
                     or "no_entry_decode" in x["after_status"]),
                   key=lambda x:(-x["original_provisional_bytes"],-x["after_unresolved_edges"]))[:35]
    result={
     "status":"original-v131-split-instruction-CFG-recovery-measured",
     "official_EXE_SHA256":EXE_SHA,"original_CODE_SHA256":CODE_SHA,
     "code_object_bytes":len(b),
     "pre_fix_commit":PRE_FIX_COMMIT,
     "all_function_entries":len(old),
     "before":{**old_manifest,"status_counts":dict(sorted(base_status.items())),
               "unresolved_edges":sum(int(x["unresolved_edges"]) for x in old.values())},
     "after":{**now,"status_counts":dict(sorted(new_status.items())),
              "unresolved_edges":sum(int(x["unresolved_edges"]) for x in after.values())},
     "measured_increased_membership_instructions":new_count-old_count,
     "relative_instruction_membership_increase_percent":round((new_count-old_count)/old_count*100,2),
     "functions_with_increased_reachable_instruction_memberships":improved,
     "functions_with_decreased_reachable_instruction_memberships":len(decreased),
     "original_machine_instruction_repaired":SOURCE_SPLIT,
     "largest_single_function_improvements":top[:30],
     "largest_remaining_unresolved_or_shorter_code_intervals":high_risk,
     "measurement_definition":"Sum of CFG instruction-membership records across named and synthetic function entries. May count shared instruction addresses per function. Not unique bytes, not code-understanding, not native implementation progress.",
     "remaining_uncertainties":["Unresolved indirect jumps/tables and shared tails",
                                "Out-of-line runtime address marker/data misclassification",
                                "Valid game-state and DOS runtime parity",
                                "Native browser gameplay not implemented",
                                "No defensible whole executable semantic-completion percentage from these data"],
    }
    return result,top

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    p.add_argument("--top-csv",type=Path)
    args=p.parse_args()
    report,rows=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(report,indent=2)+"\n")
    if args.top_csv:
        fieldnames=list(rows[0]) if rows else []
        with args.top_csv.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows[:100])
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
