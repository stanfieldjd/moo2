#!/usr/bin/env python3
"""Audit original v1.31 CODE branch-target resynchronization and remaining edges.

Authenticates exactly 16 direct branch displacements from the original
executable CODE; compares full 5635-entry CFG manifests with immutable
GitHub baseline; reports remaining unresolved spans without misclassifying
original Watcom inline DATA / 16-bit runtime markers as playable game code.
"""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path
from export_resynchronized_disassembly import audited_segments, audited_direct_branch_restart_points, BRANCH_RESYNC_ANCHORS

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"decompilation"
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BASELINE="4882a69f0e2b73c0afd2a90cd51af46347a85b03"
EXPECTED_NAMES={
 "_max_planet_flags","_flag_replacement_colors","_climate_maintenance_modifiers",
 "_cstart_","___GETDSEnd_","_netLobby","anon_runtime_0012F1D8",
 "_Alphabet","__GreenleafFastRealIsr","__SegmentStartRR16","__IrqDataArrayRR16",
 "__VideoBasePD16","__RealDispatcherRR16","__SegmentEndRR16",
 "__SegmentStartPC32","__SegmentEndPC32"
}
def sha(b):return hashlib.sha256(b).hexdigest()
def previous(rel):
    return subprocess.check_output(["git","-C",str(ROOT),"show",f"{BASELINE}:{rel}"])
def parsed(raw):
    rr=list(csv.DictReader(io.StringIO(raw.decode())))
    idx={(r["offset"],r["name"]):r for r in rr}
    if len(rr)!=len(idx):raise ValueError("Duplicated function identity")
    return idx
def audit(exe,code):
    b=code.read_bytes()
    if len(b)!=1410709 or sha(b)!=CODE_SHA or sha(exe.read_bytes())!=EXE_SHA:
        raise ValueError("Original official game executable/CODE identity mismatch")
    source,entry_starts,end_by_start,owned,table_ranges=audited_segments()
    if b!=source or len(table_ranges)!=205 or len(entry_starts)!=5546:
        raise ValueError("Source CODE or authenticated inline table boundaries mismatch")
    branchpoints=audited_direct_branch_restart_points(source,entry_starts,end_by_start,table_ranges)
    if len(BRANCH_RESYNC_ANCHORS)!=16 or sum(map(len,branchpoints.values()))!=16:
        raise ValueError("Expected independent v1.31 exact direct-branch verification did not complete")
    now_disasm=json.loads((D/"resynced_disassembly.json").read_text())
    old_disasm=json.loads(previous("decompilation/resynced_disassembly.json"))
    if (old_disasm["independent_disassembly_segments"],
        now_disasm["independent_disassembly_segments"],
        now_disasm["source_authenticated_direct_branch_restarts"],
        now_disasm["source_verified_table_data_bytes_not_disassembled"],
        now_disasm["failed_segments"])!=(5562,5578,16,6500,0):
        raise ValueError("Original source disassembly segmentation proof changed")
    old=parsed(previous("decompilation/function_cfg_extents.csv"))
    new=parsed((D/"function_cfg_extents.csv").read_bytes())
    if len(old)!=5635 or set(old)!=set(new):
        raise ValueError("Original compiler CODE/synthetic entry set changed")
    meta=json.loads((D/"function_cfg_extents.json").read_text())
    baseline=json.loads(previous("decompilation/function_cfg_extents.json"))
    before=sum(int(r["reachable_instructions"]) for r in old.values())
    after=sum(int(r["reachable_instructions"]) for r in new.values())
    if (before,after)!=(395735,396138) or (
        baseline["cfg_membership_records"],meta["cfg_membership_records"])!=(before,after):
        raise ValueError("Original CODE CFG instruction-membership delta changed")
    changed=[];losses=[]
    for key,before_r in old.items():
        after_r=new[key]
        delta=int(after_r["reachable_instructions"])-int(before_r["reachable_instructions"])
        if delta<0:losses.append((before_r["name"],delta))
        if delta or before_r["status"]!=after_r["status"]:
            changed.append({
             "name":before_r["name"],"original_CODE_offset":hex(int(before_r["offset"])),
             "before_instruction_memberships":int(before_r["reachable_instructions"]),
             "after_instruction_memberships":int(after_r["reachable_instructions"]),
             "gained_instruction_memberships":delta,
             "source_status_before":before_r["status"],"source_status_after":after_r["status"],
             "unresolved_edges_before":int(before_r["unresolved_edges"]),
             "unresolved_edges_after":int(after_r["unresolved_edges"])})
    if losses or len(changed)!=15 or sum(x["gained_instruction_memberships"] for x in changed)!=403:
        raise ValueError("Original CFG per-function target resynchronization gains/regressions differ")
    if (baseline["matches_provisional_end"],meta["matches_provisional_end"])!=(5034,5038):
        raise ValueError("Source function boundary status count changed")
    if (baseline["ends_before_provisional_end"],meta["ends_before_provisional_end"])!=(552,548):
        raise ValueError("Provisional CODE endpoint recovery changed")
    before_edges=sum(int(r["unresolved_edges"]) for r in old.values())
    after_edges=sum(int(r["unresolved_edges"]) for r in new.values())
    if (before_edges,after_edges)!=(43,21):
        raise ValueError("Source unresolved CFG edge count changed")
    remaining=[{"name":r["name"],"CODE_offset":hex(int(r["offset"])),
                "unresolved_edges":int(r["unresolved_edges"]),
                "status":r["status"],"source_provisional_bytes":int(r["inferred_size"])}
                for r in new.values() if int(r["unresolved_edges"])]
    if set(r["name"] for r in remaining)!=EXPECTED_NAMES:
        raise ValueError("Unexpected new original code unresolved function names")
    if sum(r["unresolved_edges"] for r in remaining)!=21:
        raise ValueError("Remaining source unresolved count mismatch")
    with (D/"function_cfg_membership.csv").open(newline="") as f:
        reachable={int(r["instruction_offset"]) for r in csv.DictReader(f)}
    for site,target in BRANCH_RESYNC_ANCHORS:
        if site not in reachable or target not in reachable:
            raise ValueError(f"Authenticated branch source/target not in source CFG {site:#x}->{target:#x}")
    anchors=[{"branch_CODE_site":hex(s),"resynchronized_CODE_target":hex(t),
              "original_machine_branch_opcode":b[s:s+(2 if b[s] in (*range(0x70,0x80),0xeb,0xe3) else 5 if b[s]==0xe9 else 6)].hex()}
              for s,t in BRANCH_RESYNC_ANCHORS]
    return {
      "status":"source-authenticated-v131-direct-branch-CFG-resynchronization",
      "original_EXE_sha256":EXE_SHA,"original_CODE_sha256":CODE_SHA,
      "baseline_git_commit":BASELINE,
      "watcom_CODE_symbol_intervals":len(entry_starts),
      "function_entry_records":len(new),
      "validated_original_switch_table_boundaries":len(table_ranges),
      "exact_original_case_DWORDs_verified":1625,
      "independent_disassembly_segments_before":old_disasm["independent_disassembly_segments"],
      "independent_disassembly_segments_after":now_disasm["independent_disassembly_segments"],
      "original_verified_direct_branch_resync_sites":anchors,
      "before_cfg_instruction_memberships":before,
      "after_cfg_instruction_memberships":after,
      "net_recovered_cfg_instruction_memberships":after-before,
      "original_function_entries_increased":len(changed),
      "original_function_entries_decreased":len(losses),
      "before_functions_matching_provisional_end":baseline["matches_provisional_end"],
      "after_functions_matching_provisional_end":meta["matches_provisional_end"],
      "before_functions_shorter_than_provisional_end":baseline["ends_before_provisional_end"],
      "after_functions_shorter_than_provisional_end":meta["ends_before_provisional_end"],
      "unresolved_edges_before":before_edges,"unresolved_edges_after":after_edges,
      "source_verified_function_gains":sorted(changed,key=lambda x:-x["gained_instruction_memberships"]),
      "remaining_unresolved_symbol_inventory":sorted(remaining,key=lambda x:(-x["unresolved_edges"],x["CODE_offset"])),
      "scope":"Original x86 control-flow membership recovered by exact raw-byte Watcom direct conditional/unconditional jump displacements. Runtime startup, data labels and low-level ISR entries remain conservatively unresolved; no branch targets invented and no dynamic DOS or browser gameplay parity claimed.",
      "completion_claim":"No numerical semantic whole-game completion percentage is verified by these source CFG measurements.",
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
