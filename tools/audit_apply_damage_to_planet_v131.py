#!/usr/bin/env python3
"""Source-byte audit of original MOO2 v1.31 Apply_Damage_To_Planet_.

Verifies the entire 775-byte original Watcom CODE extent and selected
instruction/call/branch anchors. Identifies the independent biological
and conventional damage branches and the original bit-7 helper.
Does not claim full semantic C reconstruction or DOS differential runs.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
ENTRY=0x2A3C3
SIZE=775
BODY_SHA="36b773f8747c65d082b0458980138d9df024c44f2fbe5b38e0c133780e262212"
RX=re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
INS={
0x2A3CA:("mov","ecx,eax"),
0x2A3CC:("mov","word ptr [ebp-0x4],bx"),
0x2A3D8:("call","0x117776"),
0x2A3DD:("mov","eax,ds:0x1a864"),
0x2A3E2:("movzx","eax,byte ptr [eax+0x20]"),
0x2A3E6:("call","0x4685f"),
0x2A3EC:("imul","eax,eax,0xf"),
0x2A3EF:("movsx","eax,word ptr [eax+0x7642]"),
0x2A40D:("test","byte ptr [ebp-0x4],0x80"),
0x2A411:("je","0x2a4ef"),
0x2A417:("mov","word ptr ds:0x218e2,0x1"),
0x2A429:("mov","byte ptr ds:0x21b5f,0x1"),
0x2A430:("cmp","byte ptr [eax+0x26],0x17"),
0x2A434:("je","0x2a6bd"),
0x2A43A:("movsx","eax,word ptr ds:0x2188e"),
0x2A441:("imul","edx,eax,0xea9"),
0x2A447:("mov","eax,ds:0x1ff98"),
0x2A44E:("cmp","byte ptr [eax+0x182],0x3"),
0x2A464:("cmp","byte ptr [eax+0x1d8],0x3"),
0x2A480:("mov","eax,0x64"),
0x2A485:("call","0x1147a0"),
0x2A48D:("cmp","eax,edx"),
0x2A48F:("jg","0x2a6bd"),
0x2A4B1:("inc","word ptr ds:0x21b60"),
0x2A4C4:("cmp","word ptr ds:0x218f6,0x0"),
0x2A4E5:("call","0xcd2f2"),
0x2A4EF:("mov","edx,0x7"),
0x2A4F4:("xor","eax,eax"),
0x2A4F6:("call","0x3b0d3"),
0x2A4FB:("cmp","ax,0x1"),
0x2A4FF:("jne","0x2a517"),
0x2A501:("mov","ax,word ptr [ecx]"),
0x2A504:("cwd",""),
0x2A506:("shl","dx,0x2"),
0x2A50A:("sbb","ax,dx"),
0x2A50D:("sar","ax,0x2"),
0x2A511:("mov","word ptr [ecx],ax"),
0x2A514:("dec","word ptr [ecx]"),
0x2A51A:("call","0x2a142"),
0x2A527:("mov","eax,ds:0x1a864"),
0x2A52C:("mov","si,word ptr [ecx]"),
0x2A52F:("sub","si,word ptr [eax+0x29]"),
0x2A555:("mov","bx,word ptr [ecx]"),
0x2A558:("sub","bx,word ptr [eax+0x2b]"),
0x2A55C:("test","si,si"),
0x2A561:("test","byte ptr [ebp-0x4],0x8"),
0x2A567:("test","byte ptr [ebp-0x4],0x20"),
0x2A574:("add","word ptr [eax+0xc0],si"),
0x2A57B:("cmp","di,word ptr [eax+0xc0]"),
0x2A599:("call","0x2a19e"),
0x2A5D3:("test","byte ptr [ebp-0x4],0x8"),
0x2A5DD:("test","byte ptr [ebp-0x4],0x20"),
0x2A5EA:("cmp","word ptr [eax+0xaa],0x7d00"),
0x2A5F5:("add","word ptr [eax+0xaa],bx"),
0x2A602:("cmp","word ptr [edx+0xaa],0x64"),
0x2A633:("mov","byte ptr ds:0x21b5c,0x1"),
0x2A65B:("call","0xcd2f2"),
0x2A69D:("mov","byte ptr [eax+0x26],0x0"),
0x2A6A1:("sub","word ptr [eax+0x29],dx"),
0x2A6A5:("sub","word ptr [eax+0x2b],dx"),
0x2A6B2:("sub","word ptr [eax+0xaa],dx"),
0x2A6BD:("add","esi,ebx"),
0x2A6BF:("mov","eax,dword ptr [ebp-0x8]"),
0x2A6C2:("mov","word ptr [ecx],si"),
0x2A6C9:("ret",""),
}
HELPERS={
"Clear_Structure_":0x117776,
"Best_Armor_":0x4685f,
"Random_":0x1147A0,
"Apply_Bomb_Hits_":0xCD2F2,
"Does_Combat_Ship_Have_Special_":0x3B0D3,
"Does_Combat_Planet_Have_Defenses_":0x2A142,
"Destroy_Colony_Defense_":0x2A19E,
}
GLOBALS={
"_combat_data":0x1A864,
"_player":0x1FF98,
"_armor":0x7638,
"_bio_weapon_flag":0x218E2,
"_combat_bomb_result":0x21B5A,
"_combat_defender_player":0x2188E,
"_combat_attacker_player":0x218AC,
"_cmbt_colony_id":0x21878,
"_apply_damage_to_planet":0x218F6,
}

def getrows(name):
    with (ROOT/"decompilation"/name).open(newline="") as f:
        return list(csv.DictReader(f))

def decode(code,at):
    res=subprocess.run(["objdump","-D","-M","intel","-b","binary","-m","i386",
        f"--start-address=0x{at:x}",f"--stop-address=0x{at+15:x}",str(code)],
        capture_output=True,text=True,check=True)
    for line in res.stdout.splitlines():
        m=RX.match(line)
        if m and int(m[1],16)==at:return m[3].lower(),m[4].strip().lower()
    raise ValueError(f"Undecoded instruction {at:#x}")

def audit(exe,code):
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=EXE_SHA:
        raise ValueError("Wrong original DOS executable SHA-256")
    b=code.read_bytes()
    if len(b)!=1410709:raise ValueError("Unexpected original LE CODE object size")
    if hashlib.sha256(b[ENTRY:ENTRY+SIZE]).hexdigest()!=BODY_SHA:
        raise ValueError("Entire Apply_Damage_To_Planet_ original byte extent differs")
    names={r["name"]:r for r in getrows("functions.csv")}
    source=names["Apply_Damage_To_Planet_"]
    if (int(source["offset"]),int(source["inferred_size"]))!=(ENTRY,SIZE):
        raise ValueError("Original Watcom named function extent differs")
    for name,at in HELPERS.items():
        if int(names[name]["offset"])!=at:
            raise ValueError(f"Original callee identity differs: {name}")
    symbols={r["name"]:int(r["offset"]) for r in getrows("symbols.csv")
             if r["segment"]=="2"}
    for name,at in GLOBALS.items():
        if symbols.get(name)!=at:
            raise ValueError(f"Original DATA global changed: {name}")
    for at,expect in INS.items():
        op=decode(code,at)
        if op!=expect:
            raise ValueError(f"Original source instruction mismatch {at:#x}: {op} != {expect}")
    return {
        "original_sha256":EXE_SHA,
        "original_watcom_function":"Apply_Damage_To_Planet_",
        "original_code_offset":hex(ENTRY),
        "original_function_size_bytes":SIZE,
        "complete_original_function_sha256":BODY_SHA,
        "verified_instruction_anchors":len(INS),
        "source_named_helpers":{k:hex(v) for k,v in HELPERS.items()},
        "source_named_globals":{k:hex(v) for k,v in GLOBALS.items()},
        "input":"EAX points to writable candidate damage, EBX low16 is weapon field +0x12 (flags), EDX=0 on Fire_Bomb_ call",
        "bio_branch":"original TEST low byte weapon flags 0x80 at CODE+0x2a40d; bio path sets _bio_weapon_flag and _combat_bomb_result and uses Random_(100) and Apply_Bomb_Hits_",
        "conventional_branch":"CODE+0x2a4ef; check ship special bit ID7; if special=1 modify *damage signed16 with trunc_toward_zero(*damage/4)-1 using x86 CWD SHL SBB SAR DEC",
        "conventional_damage_consumer":"CODE+0x2a51a Does_Combat_Planet_Have_Defenses_, ship+0x29/+0x2b, ship+0xC0, +0xAA and original named colony-defense/hit callbacks",
        "damage_inout_writeback":"CODE 0x2a6c2 stores low16 SI into WORD [ECX] original candidate pointer",
        "return":"EAX loaded from local DWORD [EBP-8] at 0x2a6bf; not the same as the inout damage output",
        "scope":"full original function bytes and selected instruction/data/call map verified; full player/colony and planet-damage behavior NOT yet equivalently reconstructed in C"
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
