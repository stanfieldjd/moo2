#!/usr/bin/env python3
"""Quantify CFG improvement from merging 70 original-source-verified switches.

Previous CFG inventory is sourced from an immutable Git parent. The audit
re-authenticates Watcom jump tables, detects any per-function CFG regressions,
and reports membership counts rather than claiming semantic game completion.
"""
import argparse,collections,csv,hashlib,io,json,subprocess
from pathlib import Path
from merge_verified_switch_targets_v131 import audit as verify_switch_sources

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"decompilation"
BASE_COMMIT="5d6c4d9757bfc97229eb8c4b5ac3395815b64744"

def git_base(path):
    r=subprocess.run(["git","-C",str(ROOT),"show",f"{BASE_COMMIT}:{path}"],
                     capture_output=True,check=True)
    return r.stdout
def csvdict(raw):
    rows=list(csv.DictReader(io.StringIO(raw.decode())))
    look={(r["offset"],r["name"]):r for r in rows}
    if len(look)!=len(rows):raise ValueError("Duplicate original CFG name+offset")
    return look
def audit(exe,code):
    expected_rows,source=verify_switch_sources(exe,code)
    actual=list(csv.DictReader((D/"switch_targets_reconciled.csv").open(newline="")))
    if len(actual)!=len(expected_rows):
        raise ValueError("Merged original-byte-verified switch count changed")
    for a,b in zip(actual,expected_rows):
        if {k:int(a[k],16) if k in ("site_hex","target_hex") else
            int(a[k]) if k in ("case_index","target_offset") else a[k]
            for k in a}!={k:int(b[k],16) if k in ("site_hex","target_hex") else
             b[k] for k in b}:
            raise ValueError("Original source switch CSV case row differs")
    old=csvdict(git_base("decompilation/function_cfg_extents.csv"))
    new=csvdict((D/"function_cfg_extents.csv").read_bytes())
    if len(old)!=5635 or set(old)!=set(new):
        raise ValueError("Original function entry index changed")
    oldmeta=json.loads(git_base("decompilation/function_cfg_extents.json"))
    meta=json.loads((D/"function_cfg_extents.json").read_text())
    if (meta.get("switch_target_inventory"),meta.get("source_verified_switch_sites"),
        meta.get("source_verified_switch_cases"))!=("switch_targets_reconciled.csv",205,1625):
        raise ValueError("CFG did not consume source-verified extended dispatch inventory")
    aftertotal=sum(int(x["reachable_instructions"]) for x in new.values())
    beforetotal=sum(int(x["reachable_instructions"]) for x in old.values())
    if aftertotal!=meta["cfg_membership_records"] or beforetotal!=oldmeta["cfg_membership_records"]:
        raise ValueError("CFG manifest membership count mismatch")
    deltas=[];regress=[]
    for key,x in old.items():
        y=new[key]
        gained=int(y["reachable_instructions"])-int(x["reachable_instructions"])
        if gained<0:regress.append((key,gained))
        if gained:
            deltas.append({"name":x["name"],"CODE_offset":int(x["offset"]),
             "before_instructions":int(x["reachable_instructions"]),
             "after_instructions":int(y["reachable_instructions"]),
             "membership_gain":gained,
             "original_covered_provisional_bytes":int(x["inferred_size"]),
             "previous_status":x["status"],"current_status":y["status"]})
    if regress:raise ValueError("Some original source function paths regressed")
    if sum(x["membership_gain"] for x in deltas)!=aftertotal-beforetotal:
        raise ValueError("Measured source gains do not sum to total")
    if aftertotal!=372703 or beforetotal!=367349 or len(deltas)!=54:
        raise ValueError("Expected 2026-10-16 baseline gains changed")
    membership_set={int(x["instruction_offset"]) for x in
        csv.DictReader((D/"function_cfg_membership.csv").open(newline=""))}
    verified_sites=[int(x["site_offset"],16) for x in
        json.loads((D/"reports/omitted_game_switches_v131_2026-10-13.json").read_text())["additional_switches"]]
    verified_sites.extend(int(x["site_offset"],16) for x in
        json.loads((D/"reports/omitted_prescaled_dispatches_v131_2026-10-13.json").read_text())["sites"])
    reachable_verified=sum(site in membership_set for site in verified_sites)
    if len(verified_sites)!=70 or reachable_verified!=63:
        raise ValueError("New verified source dispatch reachability differs")
    full_old=sum(int(x["unresolved_edges"]) for x in old.values())
    full_new=sum(int(x["unresolved_edges"]) for x in new.values())
    result={"status":"source-verified-v131-CFG-expanded-from-reconciled-switch-targets",
       "original_exe_sha256":source["original_EXE_SHA256"],
       "original_code_sha256":source["original_CODE_SHA256"],
       "parent_git_commit":BASE_COMMIT,
       "all_function_entry_records":len(new),
       "source_verified_switch_sites":205,
       "source_verified_switch_cases":1625,
       "added_original_source_verified_sites":70,
       "newly_added_sites_already_reachable_after_recovery":reachable_verified,
       "newly_added_sites_still_unreached":[hex(x) for x in verified_sites if x not in membership_set],
       "previous_cfg_membership_records":beforetotal,
       "new_cfg_membership_records":aftertotal,
       "increased_cfg_instruction_memberships":aftertotal-beforetotal,
       "relative_membership_increase_percent":round((aftertotal-beforetotal)/beforetotal*100,2),
       "functions_with_instruction_membership_gain":len(deltas),
       "functions_with_instruction_membership_loss":len(regress),
       "previous_functions_matching_provisional_end":oldmeta["matches_provisional_end"],
       "new_functions_matching_provisional_end":meta["matches_provisional_end"],
       "previous_functions_ending_short":oldmeta["ends_before_provisional_end"],
       "new_functions_ending_short":meta["ends_before_provisional_end"],
       "previous_unresolved_cfg_edges":full_old,
       "new_unresolved_cfg_edges":full_new,
       "unresolved_count_explanation":"Additional source-confirmed reachable control-flow paths can expose more unresolved edges. 425 -> 446 here is increased inspection of reachable branches, not lost source CFG coverage.",
       "largest_function_gains":sorted(deltas,key=lambda x:(-x["membership_gain"],x["CODE_offset"]))[:30],
       "measurement_scope":"Original source verified game+support switch cases connected to conservative x86 CFG; counts are per-function instruction memberships, not unique instructions, translated semantic functions, original DOS runtime parity or native browser gameplay completion.",
       "remaining_uncertainties":["Seven original authenticated additional switch sites have not yet become reachable under current conservative entry-point traversal",
                                  "Remaining indirect edges, boundary merges and Watcom CODE inline tables require continued source verification",
                                  "This is not a measured whole-executable semantic decompilation percentage"],
       }
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
