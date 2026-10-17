#!/usr/bin/env python3
"""Evidence-based triage of original MOO2 DOS/4GW mixed-mode CFG residuals.

Checks original DOS MZ/Watcom DOS/4GW fingerprints; proves climate table
source reads and GETDS segment-boundary arithmetic; verifies 16-bit runtime
audits and all original code-vs-data marker bytes. Deliberately leaves one
synthetic CODE entry with uncertain source reference provenance. Does not
rewrite the honest full i386-only CFG or claim game semantic completion.
"""
import argparse,csv,hashlib,json,subprocess
from pathlib import Path
from audit_mixed_mode_runtime_v131 import (
    FUNCTIONS as RR16_FUNCTIONS, EXPECTED_BRANCHES as RR16_BRANCHES,
    EXPECTED_CALLS as RR16_CALLS, SOURCE_OPCODE_ANCHORS as RR16_OPS,
    parsed_source_16bit as decode_original_rr16,
    source_displacement as original_rr16_target,
)
from audit_video_pd16_v131 import audit as verify_original_video16

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"decompilation"
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
LEGACY_EDGES={
 "_Alphabet":4,"__GreenleafFastRealIsr":3,"__IrqDataArrayRR16":1,
 "__RealDispatcherRR16":1,"__SegmentEndPC32":1,"__SegmentEndRR16":1,
 "__SegmentStartPC32":1,"__SegmentStartRR16":1,"__VideoBasePD16":1,
 "___GETDSEnd_":1,"_climate_maintenance_modifiers":1,
 "_flag_replacement_colors":1,"_max_planet_flags":1,
 "_netLobby":1,"anon_runtime_0012F1D8":1
}
CLIMATE_READS={
 0xC2958:"0fb680bad40c00",
 0xC2EBC:"0fb680bad40c00",
 0xD09D7:"0fb689bad40c00",
 0xD545F:"660fb680bad40c00",
}
GETDS_REFERENCES={
 0x143E5C:"baef011000",  # MOV EDX,CODE+0x1001EF
 0x143E61:"b8e4011000",  # MOV EAX,CODE+0x1001E4
 0x143E66:"81eae4011000",  # SUB EDX,0x1001E4; yields 11
}
LOBBY_REFERENCES={0x128F9C:"ba318f1200",0x128FBD:"ba318f1200",
                  0x12950C:"b8318f1200"}
ZERO_MARKERS={
 "__SegmentStartRR16":1,
 "__IrqDataArrayRR16":620,
 "__SegmentEndRR16":4,
 "__SegmentStartPC32":1,
 "__SegmentEndPC32":1,
}
AUTHENTICATED_32BIT_DATA={"_Alphabet","_max_planet_flags","_flag_replacement_colors"}
RUNTIME_MODE16={"__GreenleafFastRealIsr","__RealDispatcherRR16","__VideoBasePD16"}
CLIMATE_TABLE="_climate_maintenance_modifiers"
GETDS_END="___GETDSEnd_"
UNKNOWN="anon_runtime_0012F1D8"

def sha(b):return hashlib.sha256(b).hexdigest()
def audited_opcode(code,site,expected):
    buf=bytes.fromhex(expected)
    if code[site:site+len(buf)]!=buf:
        raise ValueError(f"Original v1.31 source CODE opcode mismatch at {site:#x}")
    return {"CODE_site":hex(site),"original_machine_bytes":expected}

def source_byte_authenticated_16bit_runtime(code,image):
    """Reuse old decoder/source assertions without its obsolete global CFG baseline."""
    count=0
    for name,at,length,body_sha,expected_n,ending in RR16_FUNCTIONS:
        if sha(image[at:at+length])!=body_sha:
            raise ValueError('Original signed real-mode function body changed: '+name)
        decoded,extra=decode_original_rr16(image,code,at,length)
        if len(decoded)!=expected_n or decoded[-1][2]!=ending:
            raise ValueError('Original 16bit body count/end differs: '+name)
        indexed={addr:(raw,op,args) for addr,raw,op,args in decoded}
        for addr,(op,target) in RR16_BRANCHES[name].items():
            src=indexed[addr]
            if src[1]!=op or original_rr16_target(image,addr,src[0],op,src[2])!=target or target not in indexed:
                raise ValueError('Original 16bit control transfer not byte-verified')
        for addr,target in RR16_CALLS[name].items():
            raw,op,args=indexed[addr]
            if op!='call' or raw[0]!=0xe8 or addr+len(raw)+int.from_bytes(raw[1:],'little',signed=True)!=target or image[target]!=0xc3:
                raise ValueError('Original 16bit delay helper CALL changed')
        for addr,(op,args) in RR16_OPS[name].items():
            if indexed[addr][1:]!=(op,args):
                raise ValueError('Original 16bit named opcode anchor changed')
        count+=len(decoded)
    if count!=81:raise ValueError('Original 16bit source body count differs')
    return {'complete_16bit_original_instructions_decoded':count}

def audit(exe,code):
    orig_exe=exe.read_bytes()
    source=code.read_bytes()
    if sha(orig_exe)!=EXE_SHA or sha(source)!=CODE_SHA or len(source)!=1410709:
        raise ValueError("Official original v1.31 DOS EXE or Watcom LE CODE image mismatch")
    if orig_exe[:2]!=b"MZ":
        raise ValueError("Original executable is not a DOS MZ-backed image")
    dos4gw=[s for s in (b"DOS/4GW",b"DOS4GW") if s in orig_exe]
    if len(dos4gw)!=2:
        raise ValueError("Original DOS/4GW extender signature absent")
    source_symbols={r["name"]:r for r in
        csv.DictReader((D/"symbols.csv").open(newline="")) if r["segment"]=="1"}
    cfg={r["name"]:r for r in
        csv.DictReader((D/"function_cfg_extents.csv").open(newline=""))}
    extents={r["name"]:r for r in
        csv.DictReader((D/"functions.csv").open(newline=""))}
    previous=json.loads((D/"reports/startup_mode_aware_v131_2026-10-16.json").read_text())
    original_kind={r["symbol"]:r for r in previous["source_mode_aware_unresolved_entries"]}
    if set(original_kind)!=set(LEGACY_EDGES):
        raise ValueError("Authenticated original residual symbol inventory differs")
    if {n:int(cfg[n]["unresolved_edges"]) for n in LEGACY_EDGES}!=LEGACY_EDGES:
        raise ValueError("Legacy i386 apparent unresolved edges changed")
    if sum(int(r["unresolved_edges"]) for r in cfg.values())!=20:
        raise ValueError("Other original CODE undecoded branches absent from expected inventory")

    for name in AUTHENTICATED_32BIT_DATA:
        if (source_symbols[name]["kind"]!="5" or
            original_kind[name]["mode_aware_class"]!="source-data-labelled-in-CODE"):
            raise ValueError("Original Watcom kind 5 data symbol classification unsupported")
    # Exact original CODE-object literal and one authenticated indexed read.
    if (source[0x134942:0x134967]!=b"0123456789abcdefghijklmnopqrstuvwxyz\0"
        or source[0x13498F:0x134996]!=bytes.fromhex("2e8a9242491300")):
        raise ValueError("Original radix ASCII lookup and CS-indexed source read mismatch")

    climate=extents[CLIMATE_TABLE]
    start=int(climate["offset"]);size=int(climate["inferred_size"])
    if start!=0xCD4BA or size!=67 or source[start:start+10]!=bytes.fromhex("32190019000000000000"):
        raise ValueError("Original CODE climate-modifier table source identity differs")
    climate_accesses=[audited_opcode(source,a,v) for a,v in CLIMATE_READS.items()]
    if any(int.from_bytes(source[a+len(bytes.fromhex(v))-4:a+len(bytes.fromhex(v))],"little")!=start
        for a,v in CLIMATE_READS.items()):
        raise ValueError("Original indexed climate byte reads not addressed to source CODE table")
    if source_symbols[CLIMATE_TABLE]["kind"]!="4":
        raise ValueError("Climate data was silently recategorized from Watcom kind-4")

    getds=[audited_opcode(source,a,v) for a,v in GETDS_REFERENCES.items()]
    if (int(extents[GETDS_END]["offset"]),int(extents[GETDS_END]["inferred_size"]))!=(0x1001EF,1):
        raise ValueError("Source Watcom GETDS end marker symbol changed")
    if source[0x1001E4:0x1001ED]!=bytes.fromhex("662e8e1ded011000c3"):
        raise ValueError("Original Watcom GETDS helper source bytes changed")
    if source[0x1001ED:0x1001F0]!=b"\0"*3:
        raise ValueError("Original selector tail/end marker source bytes changed")
    getds_length=0x1001EF-0x1001E4
    if getds_length!=11:raise ValueError("GETDS linker-boundary length unexpected")

    # MOO2 runtime lobby signature is embedded literal data, not opcodes.
    if source[0x128F31:0x128F3B]!=b"MOO2\xec\0\0\0\0\0":
        raise ValueError("Original CODE MOO2 lobby signature changed")
    lobby=[audited_opcode(source,a,v) for a,v in LOBBY_REFERENCES.items()]
    if any(int.from_bytes(source[a+1:a+5],"little")!=0x128F31
       for a in LOBBY_REFERENCES):
        raise ValueError("Source MOO2 literal address references changed")

    zero=[]
    for name,size in ZERO_MARKERS.items():
        if (int(extents[name]["inferred_size"])!=size or
             source[int(extents[name]["offset"]):int(extents[name]["offset"])+size]!=b"\0"*size):
            raise ValueError("Original mixed runtime/storage source zero interval differs: "+name)
        zero.append({"symbol":name,"exact_source_zero_bytes":size,"CODE_start":hex(int(extents[name]["offset"]))})

    original_rr16=source_byte_authenticated_16bit_runtime(code,source)
    original_video=verify_original_video16(exe,code)
    if (original_rr16["complete_16bit_original_instructions_decoded"]!=81 or
       original_video["all_complete_original_16bit_instructions_authenticated"]!=104):
        raise ValueError("Prior separately authenticated real-mode instruction inventories changed")
    if source[0x15839D:0x1583A5]!=b"\0"*8:
        raise ValueError("Original PD16 video storage/code boundary differs")

    # Synthetic address 0x12F1D8 is distinguishable from the 32-bit parser's
    # preceding mislabeled instruction, but no original Watcom symbol/caller
    # has yet validated it as a real source entry point.
    off=0x12F1D8
    candidate=source[off:off+8]
    if candidate!=bytes.fromhex("668c1534ca0000c3") or UNKNOWN in source_symbols:
        raise ValueError("Original unproven synthetic CODE leaf changed or was promoted")
    # Encode both original instructions with a fresh exact-offset source check.
    proc=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
                         f"--start-address={off}",f"--stop-address={off+8}",str(code)],
                         text=True,capture_output=True,check=True)
    ins=[line.strip() for line in proc.stdout.splitlines()
         if line.lstrip().startswith(("12f1d8:","12f1df:"))]
    if (len(ins)!=2 or "data16 mov WORD PTR ds:0xca34,ss" not in ins[0] or
        not ins[1].endswith("ret")):
        raise ValueError("Synthetic source leaf not independently 32-bit decoded")

    classified={}
    for name,count in LEGACY_EDGES.items():
        if name in AUTHENTICATED_32BIT_DATA:kind="original_Watcom_symbol_kind5_data"
        elif name in ("__GreenleafFastRealIsr","__RealDispatcherRR16"):kind="fully_authenticated_original_16bit_runtime"
        elif name=="__VideoBasePD16":kind="authenticated_16bit_video_and_zero_header"
        elif name in ZERO_MARKERS:kind="original_zero_filled_runtime_marker_or_storage"
        elif name==CLIMATE_TABLE:kind="original_game_CODE_indexed_byte_table_with_four_proven_reads"
        elif name==GETDS_END:kind="original_GETDS_linker_boundary_used_as_address"
        elif name=="_netLobby":kind="original_MOO2_signature_literal_and_references"
        else:kind="source_valid_8byte_potential_leaf_entry_provenance_unverified"
        classified[name]={
         "legacy_i386_unresolved_edge_count":count,
         "mode_aware_class":kind,
         "CODE_offset":hex(int(cfg[name]["offset"])),
         "actual_original_Watcom_named_CODE_symbol":name in source_symbols,
         "source_interval_sha256":original_kind[name]["exact_original_interval_SHA256"],
         "trusted_non_i386_problem_or_incomplete_entry":name!=UNKNOWN,
        }
    annotated=sum(d["legacy_i386_unresolved_edge_count"] for name,d in classified.items() if name!=UNKNOWN)
    still=sum(d["legacy_i386_unresolved_edge_count"] for name,d in classified.items() if name==UNKNOWN)
    if (annotated,still,sum(LEGACY_EDGES.values()))!=(19,1,20):
        raise ValueError("Honest remaining original source type evidence partition changed")
    baseline=json.loads((D/"function_cfg_extents.json").read_text())
    if (baseline["functions"],baseline["cfg_membership_records"])!=(5635,396305):
        raise ValueError("Global CFG modified or misrepresented")
    return {
      "status":"original-v131-DOS4GW-Watcom-compatibility-and-mode-aware-residual-provenance",
      "original_EXE_SHA256":EXE_SHA,"original_CODE_SHA256":CODE_SHA,
      "original_MZ_signature":orig_exe[:2].decode(),
      "verified_original_DOS_extender_signatures":[x.decode() for x in dos4gw],
      "original_executable_architecture":"DOS-compatible MZ/WATCOM LE protected-mode program with 16-bit DOS real-mode runtime components. Windows 95 could host DOS programs, but Windows-native PE/NE game identity is NOT established.",
      "original_climate_modifier_data_CODE_offset":"0xcd4ba",
      "original_climate_modifier_provisional_bytes":67,
      "original_source_indexed_climate_byte_reads":climate_accesses,
      "climate_table_extent_caveat":"Four CODE-indexed BYTE loads prove table usage; original symbol kind4 and full 67-byte record not independently established as only non-code.",
      "GETDS_original_named_span_start":"0x1001e4",
      "GETDS_original_named_span_end_marker":"0x1001ef",
      "source_GETDS_code_span_difference_bytes":getds_length,
      "original_GETDS_address_arithmetic_site_evidence":getds,
      "MOO2_lobby_original_signature":"MOO2",
      "MOO2_lobby_source_absolute_address_sites":lobby,
      "verified_zero_runtime_marker_intervals":zero,
      "separately_authenticated_real_mode_interrupt_instructions":original_rr16["complete_16bit_original_instructions_decoded"],
      "separately_authenticated_16bit_video_instructions":original_video["all_complete_original_16bit_instructions_authenticated"],
      "exact_potential_synthetic_8byte_helper":{
        "CODE_start":hex(off),"CODE_bytes":candidate.hex(),
        "independent_32bit_decode":ins,
        "classification":"machine-code valid 2-instruction SS-selector storing RET leaf, but this synthetic address lacks separately proven entry/caller authority",
      },
      "original_legacy_i386_CFG_instruction_memberships_unchanged":baseline["cfg_membership_records"],
      "original_legacy_i386_CFG_apparent_unresolved_edges":20,
      "apparent_edges_with_source_type_or_runtime_explanations":annotated,
      "remaining_unproven_synthetic_entry_apparent_edges":still,
      "per_original_source_symbol_residual_type_evidence":classified,
      "scope":"Classification/evidence overlay only; the 32-bit CFG is still conservatively reported with 20 raw unresolved edges, not rewritten as 1 remaining edge or renamed 100% code recovered.",
      "important_limits":["Windows 95 DOS compatibility does not turn original DOS/4GW game into a Windows 95 PE executable.",
                          "Some embedded CODE table intervals remain only partially type-proven despite original indexed reads.",
                          "Hardware IRQ behavior, original DOS execution and native browser game not validated.",
                          "Whole-executable semantic decompilation completion percentage remains unmeasured."]
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe",required=True,type=Path)
    parser.add_argument("--code",required=True,type=Path)
    parser.add_argument("--output",type=Path)
    a=parser.parse_args()
    report=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
