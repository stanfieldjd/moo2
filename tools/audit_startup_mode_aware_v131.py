#!/usr/bin/env python3
"""Verify original DOS startup payload removal and classify remaining mixed-mode CODE.

Identifies original Watcom source executable startup JMP over vendor metadata,
revalidates the recovered _cstart_ CFG, preserves unresolved symbol accounting,
and lists directly byte-proven data and real-mode-only source intervals.
No speculative forced code/dynamic DOS parity/semantic completion percentage.
"""
import argparse,collections,csv,hashlib,io,json,subprocess
from pathlib import Path
from export_resynchronized_disassembly import audited_segments,audited_direct_branch_restart_points,audited_literal_spans

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"decompilation"
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
PARENT="466708db6e14742b4c8cc40e9d4d4067e82c8a7e"
PREFIX="WATCOM C/C++32 Run-Time system. (c) Copyright by WATCOM International Corp. 1988-1995. All rights reserved."
EXPECTED_REMAINING={
 "_Alphabet":4,"__GreenleafFastRealIsr":3,
 "_max_planet_flags":1,"_flag_replacement_colors":1,
 "_climate_maintenance_modifiers":1,"___GETDSEnd_":1,
 "_netLobby":1,"anon_runtime_0012F1D8":1,
 "__SegmentStartRR16":1,"__IrqDataArrayRR16":1,
 "__VideoBasePD16":1,"__RealDispatcherRR16":1,
 "__SegmentEndRR16":1,"__SegmentStartPC32":1,"__SegmentEndPC32":1,
}
SYM_KIND_5={"_Alphabet","_max_planet_flags","_flag_replacement_colors"}
MODE_16={"__GreenleafFastRealIsr","__RealDispatcherRR16"}
PURE_ZERO={
 "__SegmentStartRR16":1,"__IrqDataArrayRR16":620,
 "__SegmentEndRR16":4,"__SegmentStartPC32":1,"__SegmentEndPC32":1
}
def hash_bytes(b):return hashlib.sha256(b).hexdigest()
def old(rel):return subprocess.check_output(["git","-C",str(ROOT),"show",f"{PARENT}:{rel}"])
def indexed_csv(raw):
    v=list(csv.DictReader(io.StringIO(raw.decode())))
    r={(x["offset"],x["name"]):x for x in v}
    if len(r)!=len(v):raise ValueError("Original function identity duplicates")
    return r

def audit(exe,code):
    orig=code.read_bytes()
    if len(orig)!=1410709 or hash_bytes(orig)!=CODE_SHA or hash_bytes(exe.read_bytes())!=EXE_SHA:
        raise ValueError("Original DOS v1.31 Watcom EXE/CODE SHA fingerprints do not match")
    blob,starts,ends,tables_owners,tables=audited_segments()
    if orig!=blob or len(starts)!=5546 or len(tables)!=205:
        raise ValueError("Authentic original source CODE/switch anchors changed")
    branches=audited_direct_branch_restart_points(blob,starts,ends,tables)
    literals=audited_literal_spans(blob,starts,ends,tables,branches)
    if literals!={0xFFF18:[(0xFFF1A,0xFFF90,"Watcom startup header (non-executed on original entry)")]}:
        raise ValueError("Source-authenticated startup literal owner/span differed")
    if orig[0xFFF18:0xFFF1A]!=bytes.fromhex("eb76"):
        raise ValueError("Canonical source Watcom JMP short over startup metadata changed")
    payload=orig[0xFFF1A:0xFFF90]
    if len(payload)!=118 or not payload.startswith(PREFIX.encode()) or payload[-4:]!=b"con\x00":
        raise ValueError("Original vendor startup payload is not the expected 118 bytes")
    if orig[0xFFF90:0xFFF96]!=bytes.fromhex("fb83e4fc89e3"):
        raise ValueError("Resumed original startup executable instructions differ")
    dis=(D/"code_object_1_resynced.disasm").read_text(errors="replace")
    if ";; SOURCE_CODE_SEGMENT 0xfff90 END" not in dis:
        raise ValueError("Authenticated Watcom startup executable resynchronization missing")
    if ";; SOURCE_CODE_SEGMENT 0xfff18 END 0xfff1a" not in dis:
        raise ValueError("Authenticated original JMP-only first segment missing")
    if "fff90:\tfb" not in dis:
        raise ValueError("Source first actual startup instruction STI not decoded")
    original_cfg=indexed_csv(old("decompilation/function_cfg_extents.csv"))
    now=indexed_csv((D/"function_cfg_extents.csv").read_bytes())
    if set(original_cfg)!=set(now) or len(now)!=5635:
        raise ValueError("Original named and synthetic Watcom CODE identity set changed")
    delta=[]
    for key,b in original_cfg.items():
        a=now[key]
        gained=int(a["reachable_instructions"])-int(b["reachable_instructions"])
        if gained or b["status"]!=a["status"]:
            delta.append((b,a,gained))
    if len(delta)!=1 or delta[0][0]["name"]!="_cstart_" or delta[0][2]!=167:
        raise ValueError("Unexpected original CODE function changed")
    before,after,change=delta[0]
    if (before["status"],after["status"],before["unresolved_edges"],after["unresolved_edges"])!=(
        "shorter+unresolved","matches","1","0"):
        raise ValueError("Original startup CFG coverage/edge change differs")
    original_meta=json.loads(old("decompilation/function_cfg_extents.json"))
    new_meta=json.loads((D/"function_cfg_extents.json").read_text())
    original_dis=json.loads(old("decompilation/resynced_disassembly.json"))
    new_dis=json.loads((D/"resynced_disassembly.json").read_text())
    if (original_meta["cfg_membership_records"],new_meta["cfg_membership_records"])!=(396138,396305):
        raise ValueError("Source authenticated global CFG gain changed")
    if (original_meta["matches_provisional_end"],new_meta["matches_provisional_end"])!=(5038,5039):
        raise ValueError("Original provisional boundary result changed")
    if (original_meta["ends_before_provisional_end"],new_meta["ends_before_provisional_end"])!=(548,547):
        raise ValueError("Original conservative endpoint status changed")
    if (original_dis["independent_disassembly_segments"],new_dis["independent_disassembly_segments"])!=(5578,5579):
        raise ValueError("Authenticated original Watcom disassembly segment change differs")
    if new_dis["source_authenticated_embedded_literal_bytes"]!=118 or new_dis["source_authenticated_embedded_literal_spans"]!=1 or new_dis["source_authenticated_direct_branch_restarts"]!=17 or new_dis["failed_segments"]!=0:
        raise ValueError("Original source literal accounting differs from proven startup record")
    for idx,meta in [(original_cfg,original_meta),(now,new_meta)]:
        if sum(int(r["reachable_instructions"]) for r in idx.values())!=meta["cfg_membership_records"]:
            raise ValueError("Membership totals do not agree with all 5635 original rows")
    original_edges=sum(int(r["unresolved_edges"]) for r in original_cfg.values())
    current_edges=sum(int(r["unresolved_edges"]) for r in now.values())
    if (original_edges,current_edges)!=(21,20):
        raise ValueError("Original source residual CFG edge counts differ")

    kind={x["name"]:x for x in csv.DictReader((D/"symbols.csv").open()) if x["segment"]=="1"}
    unresolved=[x for x in now.values() if int(x["unresolved_edges"])>0]
    actual={x["name"]:int(x["unresolved_edges"]) for x in unresolved}
    if actual!=EXPECTED_REMAINING:
        raise ValueError("Unexpected original x86 unresolved symbol set")
    report_entries=[]
    for name,count in sorted(actual.items()):
        x=next(r for r in unresolved if r["name"]==name)
        off=int(x["offset"]);size=int(x["inferred_size"])
        evidence=orig[off:off+size]
        record={"symbol":name,"CODE_offset":hex(off),"original_symbol_kind":int(kind[name]["kind"]) if name in kind else None,
             "source_provisional_bytes":size,"legacy_i386_unresolved_edges":count,
             "exact_original_interval_SHA256":hash_bytes(evidence),"first_24_original_machine_bytes":evidence[:24].hex()}
        if name in SYM_KIND_5:
            if record["original_symbol_kind"]!=5:raise ValueError("Original Watcom symbol metadata changed")
            record["mode_aware_class"]="source-data-labelled-in-CODE"
            record["confidence"]="original symbol kind 5; content inspected"
        elif name in MODE_16:
            record["mode_aware_class"]="source-verified-16bit-runtime-code"
            record["confidence"]="fully authenticated source i8086 decoding from prior separately audited whole-body report"
        elif name in PURE_ZERO:
            if size!=PURE_ZERO[name] or any(evidence):
                raise ValueError("Original zero-filled symbol marker / IRQ array changed")
            record["mode_aware_class"]="source-confirmed-zero-filled-marker-or-storage"
            record["confidence"]="exact full original source interval consists only of zero bytes; allocation/usage semantics not independently proven"
        elif name=="_netLobby":
            if evidence!=b"MOO2\xEC\x00\x00\x00\x00\x00":
                raise ValueError("Original embedded MOO2 local lobby marker changed")
            record["mode_aware_class"]="source-literal-signature-data"
            record["confidence"]="complete 10-byte original symbol contains ASCII MOO2 signature; broader object semantics not independently proven"
        elif name=="__VideoBasePD16":
            if evidence[:8]!=b"\x00"*8 or evidence[8:12]!=bytes.fromhex("558bec1e"):
                raise ValueError("Original video record mixed data/16bit code marker changed")
            record["mode_aware_class"]="mixed-original-8byte-zero-storage-plus-16bit-style-runtime-code"
            record["confidence"]="original first 8 bytes zero; rest starts 16-bit BP/DS save prologue; full handler boundaries not yet audited"
        elif name=="_climate_maintenance_modifiers":
            if evidence[:10]!=bytes.fromhex("32190019000000000000"):
                raise ValueError("Original climate table-looking source bytes changed")
            record["mode_aware_class"]="unresolved-original-code-object-table-like-bytes"
            record["confidence"]="only exact full byte identity and source symbol metadata; not yet proven wholly non-executable"
        elif name=="___GETDSEnd_":
            record["mode_aware_class"]="unresolved-runtime-segment-end-marker"
            record["confidence"]="source symbol name is suggestive, but exact use/relocation not independently verified"
        elif name=="anon_runtime_0012F1D8":
            record["mode_aware_class"]="unresolved-synthetic-entry-point"
            record["confidence"]="not a source-named symbol; requires separate resynchronization and original entry proof"
        else:
            record["mode_aware_class"]="unresolved-special-runtime-code-or-marker"
            record["confidence"]="no definitive CPU mode or semantic classification yet"
        report_entries.append(record)
    alphabet=orig[0x134942:0x134967]
    if alphabet!=b"0123456789abcdefghijklmnopqrstuvwxyz\x00" or orig[0x13498F:0x134996]!=bytes.fromhex("2e8a9242491300"):
        raise ValueError("Source original CS-indexed Alphabet lookup data proof changed")
    known_kind5={n:next(x for x in report_entries if x["symbol"]==n)["exact_original_interval_SHA256"] for n in SYM_KIND_5}
    if known_kind5!={"_Alphabet":"be149e90794daca621037591f18f882d29a217dee550adbd1a9ed33080a7e664",
                    "_max_planet_flags":"5b345a341eb7afbc44e524e3ed3062ba78e32a4ec99416e26eb342ee2910d27a",
                    "_flag_replacement_colors":"2a27fc160143bb319b8c2a7574c74c33520cbc608bd25c4587c957c09896be1c"}:
        raise ValueError("Source original Watcom CODE-embedded kind-5 symbol bytes differ")
    return {
      "status":"authenticated-original-v131-Watcom-startup-CFG-recovery-and-mode-aware-residual-triage",
      "original_EXE_SHA256":EXE_SHA,"original_CODE_SHA256":CODE_SHA,
      "comparison_git_commit":PARENT,
      "source_verified_startup_jump_site":"0xfff18","source_encoded_machine_bytes":"eb76",
      "source_verified_startup_resumption_CODE":"0xfff90",
      "source_verified_embedded_record_bytes":len(payload),
      "original_vendor_message_prefix":PREFIX,
      "original_embedded_record_SHA256":hash_bytes(payload),
      "full_original_game_function_entries":len(now),
      "source_disassembly_segments_before":original_dis["independent_disassembly_segments"],
      "source_disassembly_segments_after":new_dis["independent_disassembly_segments"],
      "original_CODE_instruction_memberships_before":original_meta["cfg_membership_records"],
      "original_CODE_instruction_memberships_after":new_meta["cfg_membership_records"],
      "net_CFG_instruction_membership_gain":change,
      "only_changed_function":"_cstart_",
      "start_function_memberships_before":int(before["reachable_instructions"]),
      "start_function_memberships_after":int(after["reachable_instructions"]),
      "unresolved_edges_before":original_edges,"unresolved_edges_after":current_edges,
      "source_mode_aware_unresolved_entries":report_entries,
      "total_remaining_legacy_i386_unresolved_entry_count":len(report_entries),
      "source_16bit_fully_authenticated":["__GreenleafFastRealIsr","__RealDispatcherRR16"],
      "source_readonly_Alphabet_proof":"Original CODE 0x13498f CS-indexed load of ASCII radix alphabet at CODE 0x134942",
      "measure_scope":"Legacy global i386 CFG traversal still includes CODE inline data and 16-bit source markers as attempted entries; per-entry classes supplied separately, not discarded from legacy denominator without audited new metric.",
      "limitations":["No new original DOS dynamic behavioral parity","Remaining marker and mixed CPU-mode offsets are not all conclusively typed","Do not combine global i386 CFG memberships with separate 16-bit instructions","No whole-game semantic completion percentage or browser-game playable status follows from this audit"]
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
