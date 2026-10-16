#!/usr/bin/env python3
"""Authenticate original new-game writers of research planet-code 10 and 11.

Static source provenance: canonical v1.31 EXE and Watcom LE CODE, complete
named-body hashes, exact source operand bytes, callgraph membership and
controlled branch/lookup fixtures. Does not prove occupied colony reachability
or use original DOS execution.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from audit_colony_empire_base_formulas_v131 import scientist

ROOT=Path(__file__).resolve().parents[1]
GAME_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BODIES=[
 ("Init_New_Game_",0x2479,801,"d09b0be693dc6e48b44811a5f3022630220f97546948222d874aa0734d10cc2d"),
 ("Generate_Home_Worlds_",0x6B8CD,745,"f4cfb1e0dc82a25d1796a96fae93be264e61d1d24ae2498c65b52e03643b9f9e"),
 ("Modify_Home_Worlds_",0x6C4AF,576,"868919235947ff50eeca75301fa7c6ae5d07cee7b73a9937a101aa9d497a2f05"),
 ("Generate_Orion_",0x6BBBC,459,"697f4b6bb2041aca6d49a43a33333e406ed42444bd1ef89f353ad3b6423678cc"),
 ("Enforce_Artifacts_Special_",0x6B5B2,33,"f5b424bd3263c800e1af3d7f018fb1b2f672084c26c14e7bbbbc59d98f51ad27"),
 ("Colony_Research_Per_Scientist_",0xCFDC6,177,"7d9e54a024e600115cf99d1d299806ceaf74f93c1aa95638a135b97e2efadd14"),
]
# Distinct source opcodes: call chain, two independent code-10 writers, the
# code-11 writer, its original unowned-planet marker, and scientist consumer.
OP={
 0x252A:"e89e930600",       # CALL Generate_Home_Worlds_
 0x6BB46:"e864090000",      # CALL Modify_Home_Worlds_
 0x6BBA7:"e810000000",      # CALL Generate_Orion_
 0x6C614:"69d0a90e0000",    # original player stride 0xEA9
 0x6C61A:"a198ff0100",      # original global _player
 0x6C61F:"80bc02af08000000",# compare BYTE [player+0x8af],0
 0x6C627:"7421",            # skip code-10 writes if zero
 0x6C62D:"6bd211",          # planet stride 17
 0x6C630:"a1d4b00100",      # original global _planet
 0x6C635:"c644020f0a",      # store planet BYTE+0xf = 10
 0x6C645:"c64402280a",      # store star BYTE+0x28 = 10
 0x6BD12:"a1d4b00100",      # original global _planet
 0x6BD17:"66c70406ffff",    # original planet WORD+0 = -1
 0x6BD3E:"c644060f0b",      # store original Orion planet BYTE+0xf = 11
 0x6B5B4:"6bd811",          # helper planet stride 17
 0x6B5B7:"a1d4b00100",      # original global _planet
 0x6B5BC:"c644030f0a",      # original helper planet BYTE+0xf = 10
 0xCFE35:"0fbf4002",        # colony's planet-id word
 0xCFE39:"6bc011",          # planet stride 17
 0xCFE3C:"8b0dd4b00100",    # same _planet global
 0xCFE42:"8a44010f",        # read planet BYTE +0xf
 0xCFE46:"3c0a",            # compare code 10
 0xCFE4C:"3c0b",            # compare code 11
 0xCFE54:"42",              # 10: +1
 0xCFE55:"42",              # 10: +1
 0xCFE5A:"83832602000002",  # breakdown +2
 0xCFE65:"83c205",          # 11: +5
 0xCFE6C:"83832602000005",  # breakdown +5
}

def sha(data): return hashlib.sha256(data).hexdigest()

def original_home_planet_special(flag_8af,existing):
    """Actual observed branch of Modify_Home_Worlds_; no other state assumed."""
    if not 0<=flag_8af<256 or not 0<=existing<256:
        raise ValueError("original byte range")
    return 10 if flag_8af else existing

def original_scientist_planet_bonus(code):
    if not 0<=code<256:raise ValueError("planet value must be BYTE")
    # Include no other building or player bonuses (controlled fixture only).
    return scientist(code,{},breakdown=True)["return"]-3

def check_cases():
    n=0
    for flag,prior,expected in [
       (0,0,0),(0,11,11),(1,0,10),(1,11,10),(255,3,10)]:
        assert original_home_planet_special(flag,prior)==expected
        n+=1
    for planet,exp in [(0,0),(9,0),(10,2),(11,5),(12,0),(255,0)]:
        assert original_scientist_planet_bonus(planet)==exp
        n+=1
    assert original_scientist_planet_bonus(original_home_planet_special(1,0))==2
    n+=1
    # Orion starts with original planet ownership field -1. That does NOT
    # establish a currently colonized legal route to production.
    assert int.from_bytes(bytes.fromhex(OP[0x6BD17])[-2:],"little",signed=True)==-1
    n+=1
    return n

def audit(exe,code):
    original=exe.read_bytes(); b=code.read_bytes()
    if sha(original)!=GAME_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("Original v1.31 executable/code image identity mismatch")
    byname={x["name"]:x for x in csv.DictReader(
        (ROOT/"decompilation/functions.csv").open(newline=""))}
    bodies=[]
    for name,addr,size,expected in BODIES:
        r=byname[name]
        if int(r["offset"])!=addr or int(r["inferred_size"])!=size:
            raise ValueError("Original named body boundaries changed "+name)
        actual=sha(b[addr:addr+size])
        if actual!=expected:
            raise ValueError("Complete source function bytes changed "+name)
        bodies.append({"name":name,"CODE_offset":hex(addr),"length":size,"sha256":actual})
    for addr,digits in OP.items():
        want=bytes.fromhex(digits)
        if b[addr:addr+len(want)]!=want:
            raise ValueError(f"Original opcode mismatch at CODE {addr:#x}")
    syms={(r["name"],r["segment"]):int(r["offset"]) for r in
         csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    for name,segment,offset in [
        ("_planet","2",0x1B0D4),("_player","2",0x1FF98),
        ("_star","2",0x1B06C)]:
        if syms.get((name,segment))!=offset:
            raise ValueError(f"Original DATA global mismatch {name}")
    edges={ (r["caller"],r["callee"]) for r in
        csv.DictReader((ROOT/"decompilation/game_call_edges.csv").open(newline="")) }
    expected_edges=[
      ("Init_New_Game_","Generate_Home_Worlds_"),
      ("Generate_Home_Worlds_","Modify_Home_Worlds_"),
      ("Generate_Home_Worlds_","Generate_Orion_")]
    if not set(expected_edges).issubset(edges):
        raise ValueError("Original source named generation callgraph differs")
    n=check_cases()
    return {
       "status":"source-verified-planet-special-10-11-new-game-generation-provenance",
       "official_game_sha256":GAME_SHA,"Watcom_LE_CODE_sha256":CODE_SHA,
       "complete_source_verified_named_bodies":bodies,
       "opcode_anchors_checked":len(OP),
       "original_new_game_named_direct_calls":[{"caller":a,"callee":c}
                                                for a,c in expected_edges],
       "original_homeworld_code_10":{
          "function":"Modify_Home_Worlds_","CODE_gate":"0x6c61f",
          "original_source_player_flag":"BYTE player+0x8af !=0",
          "CODE_write":"0x6c635", "planet_record_stride":17,
          "outcome":"planet BYTE+0xf = 10, star BYTE+0x28 = 10 if gate true"},
       "original_orion_code_11":{
          "function":"Generate_Orion_","CODE_write":"0x6bd3e",
          "outcome":"planet BYTE+0xf = 11",
          "initial_planet_owner_word":"-1, original CODE 0x6bd17",
          "limit":"initially unowned does not imply colony reachable at that point"},
       "independent_artifact_writer":{
          "function":"Enforce_Artifacts_Special_","CODE_write":"0x6b5bc",
          "source_target":"planet BYTE+0xf = 10",
          "limit":"No direct caller established in original named CALL graph"},
       "source_consumption":{
          "function":"Colony_Research_Per_Scientist_","CODE_read":"0xcfe42",
          "same_global_planet_DATA":"0x1b0d4",
          "planet_byte_10_add":2,"planet_byte_11_add":5},
       "bounded_synthetic_checks":n,
       "conformance_limits":[
         "Source demonstrates explicit new-game assignment of codes 10 and 11, not every combined player/colony state",
         "No original DOS savegame/dynamic-differential runtime validation was performed",
         "No proof yet that a 0x8af-enabled homeworld achieves all particular synthetic research worker, settings, gravity, ownership and morale predicates",
         "No evidence that Orion's initial owner WORD -1 is a colonized game state",
         "The original function raw bytes and complete bodies were checked; no claim of full machine-instruction CFG coverage for large generation functions",
       ],
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
