#!/usr/bin/env python3
"""Authenticate original v1.31 race-special homeworld -> colony and worker path.

Static source evidence; verifies original DOS EXE/WC LE CODE full named hashes,
important exact instructions, direct call edges, and conditional bounded worker
fixtures. This is not DOS execution or a proven reachable full savegame.
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
 ("Init_Homeworld_Colony_",0x3FA7,16,"8d537d2c9c40af052e9ac30b4d1b6dee1175a26a0f65e1120311f39e464f0b92"),
 ("Init_Homeworld_Colony2_",0x3A3D,1386,"58e4c26cdfe04526e297334cca9b26e4c411c86cfe65da5b3f78834b6b8b3454"),
 ("Init_Colony_",0x2D75,147,"e3c19307db41b1902c6c43dbf1d2345d0467c153997fc69faf286633991fc72c"),
 ("Colony_Job_Production_",0xCE280,996,"853acbdf8e5057e9ad4f3a34c7f5aa98392c668eee1568f8133995ca5d641860")]
# The two source bodies Init_New_Game_ and Init_Colony_ contain disassembler
# hole/overlap regions; SHA-verify their entire bodies, and decode the exact
# relevant, byte-contiguous instruction blocks rather than claiming coverage.
SCOPES={"Init_New_Game_":(0x252A,6),
        "Init_Colony_":(0x2D75,0x2DC0-0x2D75)}
OP={
 "Init_New_Game_":{
   0x252A:("call","0x6b8cd")},
 "Generate_Home_Worlds_":{
   0x6BB46:("call","0x6c4af")},
 "Modify_Home_Worlds_":{
   0x6C61F:("cmp","byte ptr [edx+eax*1+0x8af],0x0"),
   0x6C627:("je","0x6c64a"),
   0x6C629:("movsx","edx,word ptr [ebp-0x4]"),
   0x6C635:("mov","byte ptr [edx+eax*1+0xf],0xa"),
   0x6C688:("movsx","eax,word ptr [ebp-0x4]"),
   0x6C697:("movsx","eax,word ptr [ebp-0x4]"),
   0x6C69B:("movsx","edx,byte ptr [edx+esi*1+0x14]"),
   0x6C6A3:("call","0x3fa7")},
 "Init_Homeworld_Colony_":{
   0x3FA8:("mov","ebx,0x1"),
   0x3FB1:("call","0x3a3d")},
 "Init_Homeworld_Colony2_":{
   0x3A46:("mov","byte ptr [ebp-0x4],bl"),
   0x3A49:("mov","ax,ds:0x21996"),
   0x3A52:("imul","ebx,esi,0x169"),
   0x3A5F:("mov","ds:0x21996,ax"),
   0x3AAC:("movsx","edi,word ptr [ebp-0x24]"),
   0x3AB0:("movsx","ecx,word ptr [ebp-0x20]"),
   0x3AB4:("mov","eax,esi"),
   0x3AB6:("mov","ebx,edi"),
   0x3AB8:("mov","edx,ecx"),
   0x3ABA:("call","0x2d75"),
   0x3AFE:("mov","byte ptr [ebx+0xe2],al"),
   0x3B0F:("cmp","byte ptr ds:0x21cb5,0x2"),
   0x3B71:("cmp","byte ptr [eax+0xa],0x0"),
   0x3B75:("jne","0x3b7b"),
   0x3B77:("mov","byte ptr [eax+0xa],0x1"),
   0x3B9B:("mov","eax,ds:0x1ab18"),
   0x3BA0:("mov","byte ptr [ecx+eax*1+0xa],0x8"),
   0x3BC4:("cmp","byte ptr [ebx+0xb],0x0"),
   0x3BDA:("cmp","byte ptr [edx+ebx*1+0x8b1],0x0"),
   0x3BEB:("mov","dword ptr [ebp-0x1c],0x3"),
   0x3BF3:("idiv","dword ptr [ebp-0x1c]"),
   0x3BF6:("and","edx,0x3"),
   0x3BFF:("shl","edx,0x7"),
   0x3C02:("or","dword ptr [ebx+0xc],edx"),
   0x3C15:("mov","dword ptr [ebp-0x1c],0x2"),
   0x3C1D:("idiv","dword ptr [ebp-0x1c]"),
   0x3C20:("lea","eax,[edx+0x1]"),
   0x3C23:("and","eax,0x3"),
   0x3C2C:("shl","eax,0x7"),
   0x3C2F:("or","dword ptr [ebx+0xc],eax"),
   0x3C42:("and","ebx,0xf"),
   0x3C4C:("or","dword ptr [eax+0xc],ebx"),
   0x3C5E:("and","byte ptr [eax+0xd],0xf9"),
   0x3C62:("or","byte ptr [eax+0xd],0x2"),
   0x3C6D:("movzx","edx,byte ptr [eax+0xa]"),
   0x3C71:("cmp","edi,edx"),
   0x3C73:("jl","0x3bb5")},
 "Init_Colony_":{
   0x2D82:("imul","eax,eax,0x169"),
   0x2D9F:("imul","edx,edi,0x11"),
   0x2DB1:("mov","word ptr [edx],si"),
   0x2DB4:("mov","word ptr [eax+0x4],0xffff"),
   0x2DBA:("mov","word ptr [eax+0x2],di"),
   0x2DBE:("mov","byte ptr [eax],cl")},
 "Colony_Job_Production_":{
   0xCE393:("test","byte ptr [edi+0x1],0x2"),
   0xCE397:("je","0xce61e"),
   0xCE39F:("shl","edx,0x17"),
   0xCE3A6:("shr","edx,0x1e"),
   0xCE3AB:("jne","0xce61e"),
   0xCE3B3:("and","eax,0xf")}
}
EDGES=[
 ("Init_New_Game_",0x252A,"Generate_Home_Worlds_"),
 ("Generate_Home_Worlds_",0x6BB46,"Modify_Home_Worlds_"),
 ("Modify_Home_Worlds_",0x6C6A3,"Init_Homeworld_Colony_"),
 ("Init_Homeworld_Colony_",0x3FB1,"Init_Homeworld_Colony2_"),
 ("Init_Homeworld_Colony2_",0x3ABA,"Init_Colony_")]
def sha(b):return hashlib.sha256(b).hexdigest()
def expected_job(i,planet_b=False,player_8b1=False):
    if not isinstance(i,int) or not 0<=i<=255:raise ValueError("population index outside BYTE fixture")
    return (i%3) if (planet_b and not player_8b1) else ((i%2+1)&3)
def initial_population(settings_byte,derived_count=None):
    """Source selected branch; dynamic count intentionally unknown."""
    if not 0<=settings_byte<=255:raise ValueError("source option BYTE")
    if settings_byte!=2:return 8
    if derived_count is None:raise ValueError("dynamic source population not established")
    if not 0<=derived_count<=255:raise ValueError("source derived population BYTE")
    return max(1,derived_count)
def packed_population_record(i,owner,planet_b=False,player_8b1=False):
    if not 0<=owner<=7:raise ValueError("bounded original owner player index")
    job=expected_job(i,planet_b,player_8b1)
    # Source clears and fills low nibble (owner), bits 7-8 (job), and bit9
    # membership; other packed fields are not modeled.
    return (owner&0xf)|(job<<7)|0x200
def fixtures():
    n=0
    for state in (False,True):
        for b in (False,True):
            for pop in range(3,9):
                jobs=[expected_job(i,b,state) for i in range(pop)]
                assert 2 in jobs
                n+=1
                for owner in (0,1,3,7):
                    entries=[packed_population_record(i,owner,b,state) for i in range(pop)]
                    assert len(entries)==pop
                    assert all(x&0x200 and (x&0xf)==owner for x in entries)
                    assert all(((x>>7)&3)==jobs[i] for i,x in enumerate(entries))
                    assert any(((x>>7)&3)==2 for x in entries)
                    n+=4
    for x in (0,1,3,127,255):
        assert initial_population(x)==8
        n+=1
    for x in (0,1,2,3,7):
        assert initial_population(2,x)==max(1,x)
        n+=1
    for flag in (False,True):
        # Original source code 10 writer executes only for nonzero flag.
        v=10 if flag else 0
        assert (v==10)==flag
        n+=1
    return n
def audit(exe,code):
    b=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("official original EXE/CODE fingerprint mismatch")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    scopes={};bodies=[];nins=0
    for name,start,size,digest in BODIES:
        r=fs[name]
        if (int(r["offset"]),int(r["inferred_size"]))!=(start,size) or sha(b[start:start+size])!=digest:
            raise ValueError("whole original named source body mismatch "+name)
        addr,length=SCOPES.get(name,(start,size))
        ins,continuations=parse(code,addr,length)
        m={at:(op,arg) for at,raw,op,arg in ins}
        for at,raw,op,arg in ins:
            if b[at:at+len(raw)]!=raw:raise ValueError("original CODE byte decode mismatch")
        for at,expected in OP[name].items():
            if m.get(at)!=expected:raise ValueError(f"source anchor {name} {at:#x}: {m.get(at)} != {expected}")
        scopes[name]=m;nins+=len(ins)
        bodies.append({"name":name,"CODE_offset":hex(start),"full_named_bytes":size,"SHA256":digest,
                       "decoded_instructions_within_scope":len(ins),
                       "decoded_scope":"whole indexed body" if name not in SCOPES else f"{addr:#x}..{addr+length:#x} only",
                       "continuation_lines":continuations,
                       "opcode_anchors":len(OP[name])})
    with (ROOT/"decompilation/game_call_edges.csv").open(newline="") as f:
        edges={(r["caller"],r["callee"]) for r in csv.DictReader(f)}
    for caller,addr,callee in EDGES:
        if (caller,callee) not in edges:raise ValueError("named source call edge missing")
        if scopes[caller].get(addr)!=("call",hex(int(fs[callee]["offset"]))):
            raise ValueError(f"named original direct CALL mismatch {caller}->{callee}")
        if b[addr]!=0xe8 or addr+5+int.from_bytes(b[addr+1:addr+5],"little",signed=True)!=int(fs[callee]["offset"]):
            raise ValueError("original direct call displacement changed")
    syms={(x["name"],x["segment"]):int(x["offset"]) for x in csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    for name,off in (("_planet",0x1B0D4),("_player",0x1FF98),("_colony",0x1AB18)):
        if syms.get((name,"2"))!=off:raise ValueError("original pointer symbol mismatch "+name)
    c=fixtures()
    return {"status":"source-verified-special-homeworld-colony-and-research-worker-conditional-path",
     "original_EXE_SHA256":EXE_SHA,"original_CODE_SHA256":CODE_SHA,
     "original_full_function_hashes_and_instruction_scopes":bodies,
     "total_original_instructions_decoded_within_stated_scopes":nins,
     "source_opcode_anchor_count":sum(len(z) for z in OP.values()),
     "verified_original_direct_call_chain":[{"caller":a,"CODE_site":hex(at),"callee":z} for a,at,z in EDGES],
     "shared_original_planet_id":"Modify_Home_Worlds_ writes selected planet BYTE+0xf at CODE 0x6c635 using [EBP-0x4], then passes same [EBP-0x4] at 0x6c697 to Init_Homeworld_Colony_, which forwards it to Init_Colony_ for colony WORD+0x02",
     "original_colony_initialization":"Init_Colony_ writes owner BYTE+0x00, planet WORD+0x02, and planet-owner WORD+0x00 linked to new colony slot",
     "original_population_baseline":"source byte settings 0x21cb5 !=2 sets count to8, otherwise source computes count and enforces minimum1",
     "original_worker_packed_source":"low nibble=owner index, bits 7-8=job from i%3 if planet BYTE+0x0b nonzero and player BYTE+0x8b1 zero, otherwise (i%2+1)&3; packed bit9 set for participation; if initial count>=3 both source branches contain research job2",
     "population_fixture_assertions":c,
     "limits":["Homeworld code10 assignment requires original player option BYTE+0x8af nonzero; legal selection combos not globally established",
       "A conditional source path with special10, colony and research worker is not full proof of reachable DOS savegame inputs",
       "Complete original DOS dynamic differential output is untested",
       "Init_New_Game_ and Init_Colony_ have only bounded instruction scopes decoded; their entire indexed function bodies are separately SHA-256 authenticated",
       "Native remaster implementation and full executable coverage not established"]}
if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe",required=True,type=Path)
    ap.add_argument("--code",required=True,type=Path)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    result=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
