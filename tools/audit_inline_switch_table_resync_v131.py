#!/usr/bin/env python3
"""Audit v1.31 source-byte-verified inline switch table disassembly boundaries.

Re-verifies all original CODE switch table DWORD values, omitted table bytes
and the one newly recovered Farload_Library_Data_ branch/switch site using
original Watcom machine bytes and pre-change immutable Git CFG manifests.
A conservative CFG coverage audit, not DOS gameplay parity.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path
from export_resynchronized_disassembly import audited_segments

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"decompilation"
BASELINE="ab732e68280da096e44fdf4c028cbc6bc2435a1f"
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
FARLOAD_TABLE=0x117145
FARLOAD_TABLE_END=0x117155
FARLOAD_CASE_TARGETS=[0x117197,0x1171BA,0x1171E0,0x117206]
FARLOAD_INDIRECT_JUMP_SITE=0x117190

def sha(b):return hashlib.sha256(b).hexdigest()
def parent(path):
    return subprocess.check_output(["git","-C",str(ROOT),"show",f"{BASELINE}:{path}"])
def rows(raw):
    v=list(csv.DictReader(io.StringIO(raw.decode())))
    o={(x["offset"],x["name"]):x for x in v}
    if len(o)!=len(v):raise ValueError("duplicate Watcom original name/offset")
    return o

def audit(exe,code):
    image=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(image)!=1410709 or sha(image)!=CODE_SHA:
        raise ValueError("Original official DOS EXE/CODE fingerprints mismatch")
    source,starts,boundaries,owned,ranges=audited_segments()
    if source!=image:raise ValueError("Original table verifier source code mismatch")
    if len(starts)!=5546 or len(ranges)!=205:
        raise ValueError("Original named CODE intervals or switch count changed")
    # Authentic original Watcom table is inline CODE data, not instructions.
    if (int.from_bytes(image[FARLOAD_TABLE:FARLOAD_TABLE+4],"little")!=FARLOAD_CASE_TARGETS[0]
        or [int.from_bytes(image[FARLOAD_TABLE+4*i:FARLOAD_TABLE+4*i+4],"little")
            for i in range(4)]!=FARLOAD_CASE_TARGETS):
        raise ValueError("Canonical inline original Farload switch table bytes mismatch")
    if image[FARLOAD_TABLE_END:FARLOAD_TABLE_END+5]!=bytes.fromhex("bb01000000"):
        raise ValueError("Original Farload code at table end doesn't begin MOV EBX,1")
    if image[FARLOAD_INDIRECT_JUMP_SITE:FARLOAD_INDIRECT_JUMP_SITE+7]!=bytes.fromhex("2effa045711100"):
        raise ValueError("Original Farload CS indexed JMP x86 machine instruction mismatch")
    # The original direct CALL branch fall-through reaches the first instruction
    # *after* the 16-byte inline table. Previously linear decoding at the
    # start of that function mistook the table's target address bytes for code.
    if image[0x117140:0x117142]!=bytes.fromhex("eb13"):
        raise ValueError("Original direct branch source opcode changed")
    assert 0x117140+2+0x13==FARLOAD_TABLE_END
    manifest=json.loads((D/"resynced_disassembly.json").read_text())
    was_manifest=json.loads(parent("decompilation/resynced_disassembly.json"))
    if (was_manifest["intervals_exported"],manifest["independent_disassembly_segments"],
        manifest["source_verified_switch_tables_skipped"],
        manifest["source_verified_table_data_bytes_not_disassembled"],
        manifest["failed_segments"])!=(5546,5562,205,6500,0):
        raise ValueError("Whole Watcom CODE disassembly segmentation differs")
    disasm=(D/"code_object_1_resynced.disasm").read_text(errors="replace")
    if ";; SOURCE_CODE_SEGMENT 0x117155 END" not in disasm:
        raise ValueError("Expected original CODE segment resync at table end missing")
    if not re.search(r'^\s*117155:\s+bb 01 00 00 00\s+mov\s+ebx,0x1',disasm,re.M|re.I):
        raise ValueError("Original x86 MOV at Farload table end not present")
    if not re.search(r'^\s*117190:\s+2e ff a0 45 71 11 00\s+jmp\s+DWORD PTR cs:\[eax\+0x117145\]',disasm,re.M|re.I):
        raise ValueError("Original Watcom indirect switch instruction still not disassembled")
    old=rows(parent("decompilation/function_cfg_extents.csv"))
    new=rows((D/"function_cfg_extents.csv").read_bytes())
    if set(old)!=set(new) or len(new)!=5635:
        raise ValueError("Named source function identities changed")
    delta=[]
    for key,x in old.items():
        y=new[key]
        gain=int(y["reachable_instructions"])-int(x["reachable_instructions"])
        if gain or x["status"]!=y["status"]:
            delta.append({"name":x["name"],"original_CODE_offset":int(x["offset"]),
                          "before_count":int(x["reachable_instructions"]),
                          "after_count":int(y["reachable_instructions"]),
                          "membership_gain":gain,"old_status":x["status"],"new_status":y["status"],
                          "unresolved_edges_before":int(x["unresolved_edges"]),
                          "unresolved_edges_after":int(y["unresolved_edges"])})
    if len(delta)!=1 or delta[0]["name"]!="Farload_Library_Data_" or delta[0]["membership_gain"]!=64:
        raise ValueError("Unexpected original Watcom CODE function CFG changes")
    if (delta[0]["old_status"],delta[0]["new_status"])!=("shorter+unresolved","matches"):
        raise ValueError("Expected original Farload CFG end-status recovery missing")
    oldmeta=json.loads(parent("decompilation/function_cfg_extents.json"))
    newmeta=json.loads((D/"function_cfg_extents.json").read_text())
    if (oldmeta["cfg_membership_records"],newmeta["cfg_membership_records"])!=(395671,395735):
        raise ValueError("Corrected whole-CODE CFG numeric outcome changed")
    if (oldmeta["matches_provisional_end"],newmeta["matches_provisional_end"])!=(5033,5034):
        raise ValueError("Expected original function boundary recovery missing")
    if (oldmeta["ends_before_provisional_end"],newmeta["ends_before_provisional_end"])!=(553,552):
        raise ValueError("Expected shortened provisional interval recovery missing")
    old_unresolved=sum(int(x["unresolved_edges"]) for x in old.values())
    new_unresolved=sum(int(x["unresolved_edges"]) for x in new.values())
    if (old_unresolved,new_unresolved)!=(45,43):
        raise ValueError("Original CODE CFG unresolved edges changed")
    if (sum(int(x["reachable_instructions"]) for x in old.values())!=oldmeta["cfg_membership_records"]
       or sum(int(x["reachable_instructions"]) for x in new.values())!=newmeta["cfg_membership_records"]):
        raise ValueError("Source per-function membership count inconsistent")
    with (D/"function_cfg_membership.csv").open(newline="") as f:
        reachable={int(x["instruction_offset"]) for x in csv.DictReader(f)}
    for site in (0x117140,0x117155,0x117190,*FARLOAD_CASE_TARGETS):
        if site not in reachable:
            raise ValueError(f"Original source switch site or case target unreachable: {site:#x}")
    if FARLOAD_TABLE in reachable:
        raise ValueError("Original verified inline jump-table DATA was incorrectly treated as CODE")
    return {
      "status":"v131-original-source-verified-inline-switch-table-resynchronization",
      "official_original_EXE_SHA256":EXE_SHA,
      "original_Watcom_LE_CODE_SHA256":CODE_SHA,
      "baseline_git_commit":BASELINE,
      "original_function_intervals":len(starts),
      "original_switch_tables_source_authenticated":len(ranges),
      "original_switch_case_DWORD_entries_verified":1625,
      "inline_original_data_bytes_excluded_from_code_decode":6500,
      "previous_source_disassembly_segments":was_manifest["intervals_exported"],
      "source_disassembly_segments_now":manifest["independent_disassembly_segments"],
      "exact_original_recovered_inline_data_region":[hex(FARLOAD_TABLE),hex(FARLOAD_TABLE_END)],
      "original_code_resynchronization_at":hex(FARLOAD_TABLE_END),
      "original_instruction_bytes_at_resync":"bb01000000",
      "original_authenticated_indirect_jump_site":hex(FARLOAD_INDIRECT_JUMP_SITE),
      "original_verified_case_offsets":[hex(t) for t in FARLOAD_CASE_TARGETS],
      "source_function_correction":delta[0],
      "net_original_CFG_instruction_memberships_gained":newmeta["cfg_membership_records"]-oldmeta["cfg_membership_records"],
      "unresolved_CFG_edges_before":old_unresolved,
      "unresolved_CFG_edges_after":new_unresolved,
      "functions_with_more_reachable_instructions":len(delta),
      "other_functions_changed":0,
      "all_original_source_verified_dispatch_sites_now_reachable":True,
      "measurement_scope":"Conservative source-disassembled original CODE CFG membership, not unique original bytes, compilable gameplay reconstruction, DOS dynamic parity, or browser-playable native implementation",
      "remaining_uncertainties":[
         "43 original code branches remain conservatively unresolved",
         "Some source opcode/operand semantics, runtime callbacks and game-state parity remain unverified",
         "Original game and legally hosted browser implementation remain incomplete",
         "No measured whole-game semantic decompilation-completion percentage is derived"],
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
