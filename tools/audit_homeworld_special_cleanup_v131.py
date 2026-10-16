#!/usr/bin/env python3
"""Audit original v1.31 homeworld special10 setup versus later cleanup branch.

Source-authenticate named CODE bodies, two ordered new-game stage CALLs,
star/planet special writes, star-special dispatch, relevant direct branch
destinations and original shared return tail. No DOS runtime equivalence.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from audit_remaining_colony_production_callers_v131 import parse
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BODIES=[
 ("Init_New_Game_",0x2479,801,"d09b0be693dc6e48b44811a5f3022630220f97546948222d874aa0734d10cc2d"),
 ("Generate_Home_Worlds_",0x6B8CD,745,"f4cfb1e0dc82a25d1796a96fae93be264e61d1d24ae2498c65b52e03643b9f9e"),
 ("Modify_Home_Worlds_",0x6C4AF,576,"868919235947ff50eeca75301fa7c6ae5d07cee7b73a9937a101aa9d497a2f05"),
 ("Twiddle_Initial_Homeworlds_",0xD5832,693,"c5ca5500d59e4b1a4e386416845502c62a4359981fa350afdc779e9c92f7987b"),
 ("Twiddle_Initial_Homeworld_",0xD55BE,530,"63231cd00c846d3dc955e8144437ae7deb45d76525ee8d52866b275a2173e891")]
OP={
 "Init_New_Game_":{
 0x252A:("call","0x6b8cd"),0x2700:("call","0xd5832")},
 "Generate_Home_Worlds_":{
 0x6BB46:("call","0x6c4af")},
 "Modify_Home_Worlds_":{
 0x6C61F:("cmp","byte ptr [edx+eax*1+0x8af],0x0"),
 0x6C627:("je","0x6c64a"),
 0x6C635:("mov","byte ptr [edx+eax*1+0xf],0xa"),
 0x6C645:("mov","byte ptr [edx+eax*1+0x28],0xa"),
 0x6C6A3:("call","0x3fa7")},
 "Twiddle_Initial_Homeworlds_":{
 0xD5862:("sub","ebx,0x169"),
 0xD586A:("call","0xd55be")},
 "Twiddle_Initial_Homeworld_":{
 0xD55F3:("movsx","eax,word ptr [ebx+0x2]"),
 0xD55F7:("imul","eax,eax,0x11"),
 0xD55FA:("mov","edx,dword ptr ds:0x1b0d4"),
 0xD5600:("movzx","eax,byte ptr [edx+eax*1+0x2]"),
 0xD5605:("imul","edx,eax,0x71"),
 0xD570D:("mov","bl,byte ptr [eax+0x28]"),
 0xD5710:("cmp","bl,0x6"),
 0xD5713:("jb","0xd5733"),
 0xD5715:("cmp","bl,0x7"),
 0xD5718:("jbe","0xd574e"),
 0xD571A:("cmp","bl,0x9"),
 0xD571D:("jb","0xd5785"),
 0xD571F:("jbe","0xd1f98"),
 0xD5725:("cmp","bl,0xa"),
 0xD5728:("jbe","0xd57c7"),
 0xD572E:("jmp","0xd1f98"),
 0xD574E:("mov","ecx,edx"),
 0xD5750:("mov","byte ptr [eax+0x28],0x0"),
 0xD576D:("imul","ebx,edx,0x11"),
 0xD5776:("mov","byte ptr [edx+ebx*1+0xf],0x0"),
 0xD57C7:("mov","byte ptr [eax+0x70],0x1"),
 0xD57CB:("jmp","0xd1f98")}
}
# Init_New_Game_ has disassembler holes elsewhere; exact CALL sites only.
SCOPES={"Init_New_Game_":[(0x252A,5),(0x2700,5)]}
EDGES=[
 ("Init_New_Game_",0x252A,"Generate_Home_Worlds_"),
 ("Init_New_Game_",0x2700,"Twiddle_Initial_Homeworlds_"),
 ("Generate_Home_Worlds_",0x6BB46,"Modify_Home_Worlds_"),
 ("Twiddle_Initial_Homeworlds_",0xD586A,"Twiddle_Initial_Homeworld_")]
def sha(x):return hashlib.sha256(x).hexdigest()
def cleanup_dispatch(star_byte_28):
    """Only source direct special-switch effects; no dynamic helper side effects."""
    if not 0<=star_byte_28<=255:raise ValueError("original source BYTE")
    if 2<=star_byte_28<=3:
        return {"planet_special_clear_loop":False,"star_special_cleared":True,"star_flag_70_set":False}
    if 6<=star_byte_28<=7:
        return {"planet_special_clear_loop":True,"star_special_cleared":True,"star_flag_70_set":False}
    if star_byte_28==10:
        return {"planet_special_clear_loop":False,"star_special_cleared":False,"star_flag_70_set":True}
    if star_byte_28==8:
        return {"planet_special_clear_loop":False,"star_special_cleared":True,"star_flag_70_set":False}
    return {"planet_special_clear_loop":False,"star_special_cleared":False,"star_flag_70_set":False}
def fixtures():
    n=0
    for code in range(256):
        d=cleanup_dispatch(code)
        assert d["planet_special_clear_loop"]==(code in (6,7))
        n+=1
        assert d["star_flag_70_set"]==(code==10)
        n+=1
        assert d["star_special_cleared"]==(code in (2,3,6,7,8))
        n+=1
    # Source setter uses identical star special10 value as original later test.
    d=cleanup_dispatch(10)
    assert d["star_flag_70_set"] and not d["planet_special_clear_loop"]
    n+=1
    return n
def audit(exe,code):
    b=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("canonical original game source mismatch")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    body=[];lookups={};count=0
    for name,at,size,digest in BODIES:
        row=fs[name]
        if (int(row["offset"]),int(row["inferred_size"]))!=(at,size) or sha(b[at:at+size])!=digest:
            raise ValueError("original named function identity differs "+name)
        spans=SCOPES.get(name,[(at,size)])
        original={};total=0;continuations=0
        for start,n in spans:
            ins,continued=parse(code,start,n)
            for address,raw,op,arg in ins:
                if b[address:address+len(raw)]!=raw:raise ValueError("original disassembly bytes differ")
                original[address]=(op,arg)
            total+=len(ins);continuations+=len(continued)
        for site,want in OP[name].items():
            if original.get(site)!=want:
                raise ValueError(f"source site {name} {site:#x}: {original.get(site)} != {want}")
        count+=total;lookups[name]=original
        body.append({"name":name,"CODE_offset":hex(at),"original_complete_bytes":size,"sha256":digest,
                     "verified_instructions_within_scope":total,
                     "scope":"complete named body" if name not in SCOPES else "two exact new-game CALL instruction spans, full body separately SHA-verified",
                     "original_decoder_continuation_rows":continuations,
                     "selected_opcode_anchors":len(OP[name])})
    with (ROOT/"decompilation/game_call_edges.csv").open(newline="") as f:
        pairs={(r["caller"],r["callee"]) for r in csv.DictReader(f)}
    for caller,site,target in EDGES:
        if (caller,target) not in pairs or lookups[caller].get(site)!=("call",hex(int(fs[target]["offset"]))):
            raise ValueError("source named CALL target differs")
        if b[site]!=0xE8 or site+5+int.from_bytes(b[site+1:site+5],"little",signed=True)!=int(fs[target]["offset"]):
            raise ValueError("original x86 direct CALL bytes changed")
    symbols={(r["name"],r["segment"]):int(r["offset"]) for r in
        csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    for name,off in [("_planet",0x1B0D4),("_star",0x1B06C),("_colony",0x1AB18)]:
        if symbols.get((name,"2"))!=off:raise ValueError("original DATA symbol differs")
    # Original jump to shared x86 epilogue: pop edi,esi,edx,ecx,ebx,ret
    if b[0xD1F98:0xD1F9E]!=bytes.fromhex("5f5e5a595bc3"):
        raise ValueError("original source shared return tail changed")
    n=fixtures()
    return {"status":"source-verified-star-special-ten-bypasses-later-planet-special-clear",
      "canonical_v131_EXE_SHA256":EXE_SHA,"original_CODE_SHA256":CODE_SHA,
      "complete_original_bodies_and_scopes":body,
      "original_instructions_decoded_within_stated_scopes":count,
      "original_opcode_checkpoints":sum(len(v) for v in OP.values()),
      "original_named_direct_edges":[{"caller":a,"CODE_site":hex(site),"callee":target} for a,site,target in EDGES],
      "generation_order":"Init_New_Game_ CALL Generate_Home_Worlds_ at 0x252a precedes later CALL Twiddle_Initial_Homeworlds_ at 0x2700",
      "original_writer":"Modify_Home_Worlds_ sets linked planet BYTE+0x0f and corresponding star BYTE+0x28 to code 10 under player BYTE+0x8af !=0",
      "later_dispatch":"Twiddle_Initial_Homeworld_ selects star through linked colony planet id and star id and tests star BYTE+0x28",
      "case_6_7":"clear star special BYTE+0x28 and loop through planet indices clearing planet BYTE+0x0f",
      "case_10":"original JBE at CODE 0xd5728 branches to CODE 0xd57c7 to set star BYTE+0x70=1 and jump to shared epilogue, without entering planet-special clearing loop at CODE 0xd5776",
      "original_shared_return_tail_CODE":"0xd1f98: 5f5e5a595bc3",
      "bounded_synthetic_branch_assertions":n,
      "limitations":["No full runtime state-lifecycle proof that no unrelated helper modifies the planet special at a different time",
          "Twiddle can reassign packed worker jobs during earlier calculations; initial research job is not claimed invariant after this routine",
          "No validated original DOS game-save state or observed production/display bug",
          "Original Init_New_Game_ complete SHA verified, only selected CALL instructions decoded",
          "No complete native-engine parity or whole-executable progress percentage recalculation"]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
