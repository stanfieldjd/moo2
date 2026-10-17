#!/usr/bin/env python3
"""Authenticate original v1.31 hidden initializer callback and CFG recovery.

Combines full-source original DOS EXE/CODE/DATA identity checks, original
Watcom six-byte initialization record and CALL EAX loop code, exact leaf
machine instructions, and per-entry full-CODE CFG before/after verification.
No speculative entry and no native DOS/browser gameplay completion claim.
"""
import argparse,csv,hashlib,io,json,subprocess
from pathlib import Path
from export_resynchronized_disassembly import audited_segments,audited_initialized_callback_restarts

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"decompilation"
BASELINE="596c38a28271f2fbe2bda08057948b1318ba4ca5"
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
DATA_SHA="082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b"
DISPATCH_SHA="5d6e1ef83bad86b6e9a0d8c05c3f61d36e1f57a957ebd7e5c0b2749c06677af9"
LEAF_SHA="661acfe780d89bf88734a87eae4bfd629555259e4bb02cc56b2180b46427a098"
RECORD_SHA="2a788722d202a73ad5b23f85fd9fcba5a64718312e031658ab035987f9c996b1"
CALLBACK=0x12F1D8
RECORD=0x12FF2

def digest(b):return hashlib.sha256(b).hexdigest()
def parent(rel):
    return subprocess.check_output(["git","-C",str(ROOT),"show",f"{BASELINE}:{rel}"])
def load_cfg(raw):
    allrows=list(csv.DictReader(io.StringIO(raw.decode())))
    r={(x["name"],x["offset"]):x for x in allrows}
    if len(allrows)!=len(r):raise ValueError("Original CODE function names/addresses duplicate")
    return r

def audit(exe,code,data):
    e=exe.read_bytes();b=code.read_bytes();d=data.read_bytes()
    if (digest(e),digest(b),digest(d),len(b),len(d))!=(EXE_SHA,CODE_SHA,DATA_SHA,1410709,81920):
        raise ValueError("Official v1.31 DOS EXE or Watcom LE original image changed")
    if (digest(b[0x12EF6C:0x12EFB7]),digest(b[CALLBACK:CALLBACK+8]),
        digest(d[RECORD:RECORD+6]))!=(DISPATCH_SHA,LEAF_SHA,RECORD_SHA):
        raise ValueError("Authentic complete original dispatcher, callback or record bytes changed")
    if (d[RECORD:RECORD+6],b[CALLBACK:CALLBACK+8])!=(
        bytes.fromhex("0020d8f11200"),bytes.fromhex("668c1534ca0000c3")):
        raise ValueError("Original executable initializer callback provenance incorrect")
    instructions={
      0x12EF73:"3ebee62f0100", # initial record range begin
      0x12EF79:"3ebf10300100", # fixed record range end
      0x12EF96:"83c606",       # six-byte record stride
      0x12EF9F:"8b4302",       # initialized callback pointer load
      0x12EFA9:"ffd0",         # initialized CALL EAX
      CALLBACK:"668c1534ca0000",  # data16 MOV WORD PTR ds:0xca34,SS
      0x12F1DF:"c3",         # real original initializer RET
    }
    for addr,expected in instructions.items():
        raw=bytes.fromhex(expected)
        if b[addr:addr+len(raw)]!=raw:
            raise ValueError(f"Original source callback/dispatcher x86 bytes changed {addr:#x}")
    # Native Watcom init array: 7 records at six bytes each.
    rows=list(csv.DictReader((D/"runtime_init_targets.csv").open(newline="")))
    matching=[x for x in rows if x["function"]=="__InitRtns"]
    if len(matching)!=7:
        raise ValueError("Original Watcom initializer count/range mismatches")
    for i,row in enumerate(matching):
        off=0x12FE6+6*i
        if (int(row["record_offset"])!=off or int(row["record_index"])!=i or
            int(row["target_offset"])!=int.from_bytes(d[off+2:off+6],"little")):
            raise ValueError("Original initializer table does not match independent source CSV")
    selected=matching[2]
    if (int(selected["record_offset"]),int(selected["target_offset"]),
        selected["state"],selected["priority"],selected["named_target"])!=(RECORD,CALLBACK,"0","32","0"):
        raise ValueError("Original third anonymous init callback record metadata changed")
    source,starts,ends,tables,ranges=audited_segments()
    if source!=b or len(starts)!=5546 or len(ranges)!=205:
        raise ValueError("Original named CODE spans or source data tables changed")
    result=audited_initialized_callback_restarts(source,starts,ends)
    if result!={0x12F0C8:{CALLBACK}}:
        raise ValueError("Authenticated initializer disassembly restart not present")
    current_manifest=json.loads((D/"resynced_disassembly.json").read_text())
    previous_manifest=json.loads(parent("decompilation/resynced_disassembly.json"))
    if (previous_manifest["independent_disassembly_segments"],current_manifest["independent_disassembly_segments"],
        current_manifest["source_authenticated_initializer_callback_restarts"],
        current_manifest["source_authenticated_initializer_callback_CODE"],
        current_manifest["source_original_initialized_DATA_SHA256"])!=(
            5579,5580,1,"0x12f1d8",DATA_SHA):
        raise ValueError("Original source-init resynchronized disassembly metadata changed")
    dtext=(D/"code_object_1_resynced.disasm").read_text(errors="replace")
    if (";; SOURCE_CODE_SEGMENT 0x12f1d8 END 0x12f1e0" not in dtext or
        "12f1d8:\t66 8c 15 34 ca 00 00" not in dtext or
        "12f1df:\tc3" not in dtext):
        raise ValueError("Authenticated initializer source CODE disassembly was not decoded")
    before=load_cfg(parent("decompilation/function_cfg_extents.csv"))
    after=load_cfg((D/"function_cfg_extents.csv").read_bytes())
    if len(before)!=5635 or set(before)!=set(after):
        raise ValueError("CODE symbol and synthetic function identities changed")
    changes=[]
    for key,old in before.items():
        now=after[key]
        gain=int(now["reachable_instructions"])-int(old["reachable_instructions"])
        if gain or now["status"]!=old["status"]:
            changes.append((old["name"],gain,old["status"],now["status"],
                            int(old["unresolved_edges"]),int(now["unresolved_edges"])))
    if changes!=[("anon_runtime_0012F1D8",2,"no_entry_decode","matches",1,0)]:
        raise ValueError(f"Unanticipated original CODE source recovery or regression: {changes}")
    a=json.loads(parent("decompilation/function_cfg_extents.json"))
    c=json.loads((D/"function_cfg_extents.json").read_text())
    if (a["cfg_membership_records"],c["cfg_membership_records"],
        a["matches_provisional_end"],c["matches_provisional_end"],
        a["entry_decode_failures"],c["entry_decode_failures"])!=(396305,396307,5039,5040,7,6):
        raise ValueError("Original full-executable CFG and failed-entry changes differ")
    unresolved_before=sum(int(x["unresolved_edges"]) for x in before.values())
    unresolved_after=sum(int(x["unresolved_edges"]) for x in after.values())
    if (unresolved_before,unresolved_after)!=(20,19):
        raise ValueError("Source raw unresolved CFG edge count mismatch")
    return {
       "status":"authentic-original-Watcom-v131-previously-unnamed-initializer-callback-recovered",
       "canonical_original_EXE_sha256":EXE_SHA,"original_CODE_sha256":CODE_SHA,
       "original_initialized_DATA_sha256":DATA_SHA,
       "immutable_prior_git_commit":BASELINE,
       "source_named_init_dispatcher":"__InitRtns",
       "original_initializer_dispatcher_CODE_start":"0x12ef6c",
       "original_initializer_dispatcher_complete_75byte_SHA256":DISPATCH_SHA,
       "source_original_initializer_array_start":"0x12fe6",
       "source_original_initializer_array_end_exclusive":"0x13010",
       "source_original_initializer_record_size_bytes":6,
       "source_original_initializer_records":len(matching),
       "authenticated_source_init_record_offset":hex(RECORD),
       "authenticated_full_original_initializer_record_hex":d[RECORD:RECORD+6].hex(),
       "authenticated_original_initializer_state":0,"authenticated_original_initializer_priority":32,
       "authenticated_anonymous_original_callback_CODE_address":hex(CALLBACK),
       "authenticated_original_callback_entire_8byte_SHA256":LEAF_SHA,
       "original_callback_instructions":[
           {"CODE_offset":"0x12f1d8","source_bytes":"668c1534ca0000",
            "original_machine_operation":"MOV WORD PTR DS:[0xCA34], SS (operand size 16; protected-mode 32-bit addressing)"},
           {"CODE_offset":"0x12f1df","source_bytes":"c3","original_machine_operation":"RET"}
       ],
       "provenance":"Original initialized Watcom object-2 six-byte record read by original fixed-stride __InitRtns and invoked via original CALL EAX",
       "source_only_Cfg_affected_function":"anon_runtime_0012F1D8",
       "original_full_CFG_instruction_memberships_before":a["cfg_membership_records"],
       "original_full_CFG_instruction_memberships_after":c["cfg_membership_records"],
       "net_source_CFG_membership_gain":2,
       "original_conservative_function_end_matches_before":a["matches_provisional_end"],
       "original_conservative_function_end_matches_after":c["matches_provisional_end"],
       "source_failed_function_entry_decode_before":a["entry_decode_failures"],
       "source_failed_function_entry_decode_after":c["entry_decode_failures"],
       "raw_unresolved_32bit_CFG_edges_before":unresolved_before,
       "raw_unresolved_32bit_CFG_edges_after":unresolved_after,
       "non_target_functions_with_changed_instruction_memberships":0,
       "context":"This resolves the previously anonymous callback's entry provenance without asserting any native browser gameplay or complete DOS behavioral parity."
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe",required=True,type=Path)
    ap.add_argument("--code",required=True,type=Path)
    ap.add_argument("--data",required=True,type=Path)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    result=audit(a.exe,a.code,a.data)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
