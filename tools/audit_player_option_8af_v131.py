#!/usr/bin/env python3
"""Verify original v1.31 player BYTE+0x8af derives from race option-toggle [7].

Checks full official EXE and LE CODE provenance, seven complete named
procedure hashes, original opcode identities and actual named CALL edges.
Controlled offset/value fixtures are source-derived, not DOS runtime parity.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
BODIES=[
 ("Newgame_Screen_",0xBD435,1200,"b34f2db4d36aae5225a0cd22c54ea6b7be0bf26e88e020a865b38f4187ffc714"),
 ("Race_Selection_Screen_",0x4C510,2599,"a1643c1f5177f626608828bc1fdcb970802db5d91f6eaa966b0a13f73e79bbb5"),
 ("Racial_Option_Screen_",0x4A3BC,1816,"66cbf31616cddf0231c07a5d1f333ac554c9db0a673369ca7666f96fd36930ee"),
 ("Convert_Player_To_Flags_",0x4AD97,161,"e84d39178d6ef63e679d205d734a991add5d774997653e3edba64b2a371f9d95"),
 ("Convert_Flags_To_Player_",0x4AE38,188,"55e168ee1847ba7de6868476a4acff3811b89d1b996c8555c0dec08666eb0fd5"),
 ("Modify_Home_Worlds_",0x6C4AF,576,"868919235947ff50eeca75301fa7c6ae5d07cee7b73a9937a101aa9d497a2f05"),
 ("Colony_Research_Per_Scientist_",0xCFDC6,177,"7d9e54a024e600115cf99d1d299806ceaf74f93c1aa95638a135b97e2efadd14")]
# Raw CODE bytes for selected actual original instructions; source-offset and
# explicit opcode bytes avoid inferred assembler labels or compiler heuristics.
OPS={
 0xBD722:"e8e9edf8ff",     # Newgame CALL race selection
 0x4C9D7:"e8e0d9ffff",     # Race selection CALL racial options
 0x4A3EF:"e8a3090000",     # Racial options CALL player->flags
 0x4A8D4:"e85f050000",     # Racial options CALL flags->player
 0x4ADA0:"8d989f080000",   # EBX = player+0x89f
 0x4ADDD:"660fbe0419",     # signed player option byte, index DX
 0x4ADE5:"0fbfc6",         # flags loop accumulator ESI
 0x4ADE8:"01c8",           # flags index = ESI + ECX
 0x4ADED:"66893c45c8360200", # save WORD to base 0x236c8+2*index
 0x4ADF5:"6683fa0f",       # special slot 15
 0x4AE27:"be01000000",     # after index15, next flag index shifted +1
 0x4AE4F:"8db09f080000",   # ESI = player+0x89f
 0x4AE99:"663d0f00",       # special slot 15
 0x4AE9D:"7533",           # regular flags path
 0x4AEC8:"c745fc01000000", # source shift for index >15
 0x4AECF:"40",             # skip reserved index 16
 0x4AED2:"0fbfd0",         # source index
 0x4AED5:"0fbf4dfc",       # shift 0 or 1
 0x4AEDB:"29ca",           # effective player field = index-shift
 0x4AEDD:"8a1c5dc8360200", # read low byte of 16-bit option at 0x236c8+index*2
 0x4AEE4:"881c32",         # write player field
 0x6C614:"69d0a90e0000",   # player stride 0xea9
 0x6C61A:"a198ff0100",     # _player DATA pointer
 0x6C61F:"80bc02af08000000", # test player BYTE+0x8af
 0x6C627:"7421",           # if zero bypass code-10 write
 0x6C62D:"6bd211",         # planet stride 17
 0x6C635:"c644020f0a",     # planet BYTE+0xf=10
 0xCFE35:"0fbf4002",       # colony planet id signed WORD
 0xCFE39:"6bc011",         # planet 17-byte stride
 0xCFE3C:"8b0dd4b00100",   # _planet DATA pointer
 0xCFE42:"8a44010f",       # consume original planet BYTE+0xf
 0xCFE46:"3c0a",           # compare 10
 0xCFE54:"42",             # +1
 0xCFE55:"42",             # +1
}
EXPECTED_CALLS=[
 (0xBD722,"Newgame_Screen_","Race_Selection_Screen_"),
 (0x4C9D7,"Race_Selection_Screen_","Racial_Option_Screen_"),
 (0x4A3EF,"Racial_Option_Screen_","Convert_Player_To_Flags_"),
 (0x4A8D4,"Racial_Option_Screen_","Convert_Flags_To_Player_"),
]
def sha(x):return hashlib.sha256(x).hexdigest()
def s8(v):
    v=v&255
    return v if v<128 else v-256
def forward(player_byte_8af):
    """Convert_Player_To_Flags_ index DX=16 after special slot DX=15."""
    if not 0<=player_byte_8af<=255:raise ValueError("source input is BYTE")
    dx=16
    esi=(1 if dx>15 else 0)
    src_player_offset=0x89F+dx
    flag_index=dx+esi
    target=0x236C8+2*flag_index
    return {"player_BYTE_offset":src_player_offset,"WORD_option_DATA":target,
            "option_toggle_index":(target-0x236DC)//2,
            "WORD_signed":s8(player_byte_8af)}
def reverse(option_word):
    """Convert_Flags_To_Player_ after reserved 15 case skips index 16."""
    if not -32768<=option_word<=32767:raise ValueError("source option WORD")
    eax=17
    shift=1
    player_offset=0x89F+(eax-shift)
    option_at=0x236C8+2*eax
    return {"option_WORD_DATA":option_at,"player_BYTE_offset":player_offset,
            "stored_unsigned_BYTE":option_word&255}
def fixtures():
    checks=0
    for flag in [0,1,2,10,127,128,254,255]:
        a=forward(flag);b=reverse(a["WORD_signed"])
        assert a["player_BYTE_offset"]==0x8AF
        assert a["WORD_option_DATA"]==0x236EA
        assert a["option_toggle_index"]==7
        assert b["option_WORD_DATA"]==a["WORD_option_DATA"]
        assert b["player_BYTE_offset"]==a["player_BYTE_offset"]
        assert b["stored_unsigned_BYTE"]==flag
        checks+=6
    for val in [-32768,-256,-1,0,1,256,32767]:
        assert reverse(val)["stored_unsigned_BYTE"]==(val&255)
        checks+=1
    assert 0x236DC+7*2==0x236EA
    assert 0x89F+17-1==0x8AF
    checks+=2
    return checks

def audit(exe,code):
    b=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or len(b)!=1410709 or sha(b)!=CODE_SHA:
        raise ValueError("original official EXE/Watcom CODE fingerprint changed")
    fs={r["name"]:r for r in csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    bodies=[]
    for name,at,length,digest in BODIES:
        f=fs[name]
        if int(f["offset"])!=at or int(f["inferred_size"])!=length:
            raise ValueError(f"Original named symbol extent mismatch: {name}")
        if sha(b[at:at+length])!=digest:
            raise ValueError(f"Complete original body mismatch: {name}")
        bodies.append({"name":name,"CODE_offset":hex(at),"bytes":length,"SHA256":digest})
    for address,raw in OPS.items():
        original=bytes.fromhex(raw)
        if b[address:address+len(original)]!=original:
            raise ValueError(f"Original opcode differs {address:#x}")
    for site,caller,callee in EXPECTED_CALLS:
        f=fs[caller];at=int(f["offset"]);n=int(f["inferred_size"])
        if not at<=site<at+n:
            raise ValueError("Named CALL outside caller")
        assert b[site]==0xE8
        displacement=int.from_bytes(b[site+1:site+5],"little",signed=True)
        if site+5+displacement!=int(fs[callee]["offset"]):
            raise ValueError("Decoded original named direct CALL mismatch")
    with (ROOT/"decompilation/game_call_edges.csv").open(newline="") as f:
        edges={(row["caller"],row["callee"]) for row in csv.DictReader(f)}
    if not {(a,b) for _,a,b in EXPECTED_CALLS}.issubset(edges):
        raise ValueError("Named original linker callgraph differs")
    syms={(r["name"],r["segment"]):int(r["offset"])
          for r in csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    expected_symbols=[("_option_toggle","2",0x236DC),("_player","2",0x1FF98),
        ("_planet","2",0x1B0D4)]
    for sym,seg,offset in expected_symbols:
        if syms.get((sym,seg))!=offset:
            raise ValueError(f"Original DATA symbol identity differs: {sym}")
    n=fixtures()
    return {
      "status":"source-verified-player-8af-from-racial-option-toggle-7",
      "official_EXE_SHA256":EXE_SHA,"original_CODE_SHA256":CODE_SHA,
      "original_full_verified_bodies":bodies,
      "exact_opcode_checks":len(OPS),
      "verified_original_direct_call_sites":[{"CODE_site":hex(site),"caller":a,"callee":b}
                                             for site,a,b in EXPECTED_CALLS],
      "derived_address_equation":"Convert player offset 0x89f+16=0x8af; flag index 16+1=17; DATA 0x236c8+2*17=0x236ea; _option_toggle base 0x236dc => WORD index 7",
      "original_race_toggle_DATA":"0x236ea","original_option_symbol":"_option_toggle",
      "option_WORD_index":7,"player_BYTE_offset":"0x8af",
      "normal_conversion":"player signed BYTE+0x8af -> signed WORD option-toggle[7]; reverse conversion reads low BYTE of option WORD back into player+0x8af",
      "original_special_case":"At option index15, convert flags->player handles paired opposite-flag representation and skips index16; index17 becomes player offset16",
      "homeworld_source":"Modify_Home_Worlds_ tests that exact player BYTE+0x8af; if nonzero, writes source planet BYTE+0xf=10",
      "controlled_mapping_fixture_checks":n,
      "limitations":[
        "Original CODE proves race-option-to-player flag mapping; does not establish a particular visible UI option label or default selection",
        "The player DATA+0x8af flag may also be populated by whole-record initialization/copy; not all such paths audited",
        "This does not prove player choice of the flag alongside every previously constructed planet/worker/settings fixture",
        "No original DOS runtime comparison, save-state witness, or whole native engine equivalence",
        "Complete original named body hashes and selected opcode anchors checked; no whole-body instruction CFG coverage asserted",
      ]}
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
