#!/usr/bin/env python3
"""Source-verified static control-flow and field-effects audit of Colony_Morale_ v1.31.

Replays full original CODE and referenced helper digests, covers ALL decoded
instruction boundaries/direct control transfers and confirms key branching,
literal tables, callbacks, and controlled arithmetic. It is NOT DOS
runtime-differential execution and cannot prove complete in-game equivalence.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXE_SHA = "4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA = "f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
MAIN = ("Colony_Morale_", 0xCDB25, 982, "48ceed247ef96250b8d8f42d877f40be558159fad96e7e1e382c5754fe42cdac")
CALLEES = [
    ("Mixed_Race_Morale_Penalty_", 0xCDAD4, 81, "0bbeb8a34235ce051f7c8c00e86abce69f0793ea04020f466b08caa8075c2f8c"),
    ("Colony_Officer_", 0xCD9F2, 68, "a573f1396f45fe66f4484dfc1965704989b7a3af6301a75b173c13ec9a98afcc"),
    ("Owned_Officer_Level_", 0x84951, 86, "c067e6142cc3347a958ff8a7d868a10f4039296419eb9acf5b989f0b7f438586"),
    ("sprintf_", 0x1165F2, 48, "f46feba187f8dac98b214d9f95e9f7de8d387731802675ace60857d61d0f3b38"),
]
# Original CODE literal table slices. These offsets are not in LE DATA.
TABLES = {
    "base_byte_morale": (0xCD4C4, bytes([252,252,252,0,0,0,0,0]),
                         "5e372738eead39ccb1f597e9fe1ccf5c64e2158e4582ea6ca9473469daf2ef7f"),
    "penalty_by_government_group": (0xCD4CC, bytes([246,249,252]),
                         "68bc449df5ccfb88d407a85d8d79358aeb6ec77844e7b657adcab13dd87fae68"),
    "extra_bonus_by_government": (0xCD4CF, bytes([4,4,4,4,0,0,0,0]),
                         "57e56a86aec374538c104986467b0120b3b83b312b6cbd108b84d2964e99c555"),
}
# Exact source opcode anchors, including both the byte-wrap arithmetic
# and direct formatting/return paths. Remaining instructions are verified
# via the complete original body digest and full decoded-body coverage.
OPS = {
    0xCDB25:("push","ebx"),
    0xCDB29:("enter","0x2c,0x0"),
    0xCDB31:("movsx","eax,byte ptr [eax]"),
    0xCDB34:("imul","eax,eax,0xea9"),
    0xCDB3A:("mov","ecx,dword ptr ds:0x1ff98"),
    0xCDB42:("movsx","eax,byte ptr [ecx+0x89f]"),
    0xCDB4C:("sar","eax,1"),
    0xCDB7F:("mov","esi,eax"),
    0xCDB8A:("call","0xcdad4"),
    0xCDB92:("movsx","eax,byte ptr [ecx+0x89f]"),
    0xCDBA0:("mov","al,byte ptr [eax+0xcd4c4]"),
    0xCDBA6:("mov","byte ptr [ebx+0x7],al"),
    0xCDBA9:("cmp","esi,0x3"),
    0xCDBAC:("je","0xcdd33"),
    0xCDBB4:("call","0xcd9f2"),
    0xCDBB9:("cmp","eax,0xffffffff"),
    0xCDBCD:("test","byte ptr [edx+0x2b],0x80"),
    0xCDBD3:("call","0x84951"),
    0xCDBEC:("call","0x84951"),
    0xCDBF6:("cmp","byte ptr [ebx+0x14a],0x0"),
    0xCDBFF:("mov","eax,0x4"),
    0xCDC0B:("cmp","byte ptr [ecx+0x1da],0x3"),
    0xCDC14:("mov","eax,0x4"),
    0xCDC20:("cmp","byte ptr [ebx+0x155],0x0"),
    0xCDC29:("mov","eax,0x6"),
    0xCDC55:("cmp","eax,0x3"),
    0xCDC58:("je","0xcdcb2"),
    0xCDC5A:("movsx","eax,word ptr [ecx+0x29]"),
    0xCDC6E:("movsx","eax,word ptr [eax]"),
    0xCDC7F:("cmp","byte ptr [eax+0x13f],0x0"),
    0xCDCA8:("movsx","eax,byte ptr [eax+0xcd4cc]"),
    0xCDCB2:("cmp","esi,0x1"),
    0xCDCB7:("cmp","byte ptr [ecx+0x1aa],0x3"),
    0xCDCC0:("mov","dword ptr [ebp-0xc],0x2"),
    0xCDCC7:("cmp","byte ptr [ebx+0x14c],0x0"),
    0xCDCD7:("movzx","eax,byte ptr [eax+0xcd4cf]"),
    0xCDCE3:("cmp","byte ptr [ebx+0x138],0x0"),
    0xCDCF3:("movzx","eax,byte ptr [eax+0xcd4cf]"),
    0xCDD0C:("mov","al,byte ptr [ebp-0x24]"),
    0xCDD0F:("add","al,byte ptr [ebp-0x8]"),
    0xCDD12:("add","al,byte ptr [ebp-0x1c]"),
    0xCDD15:("add","al,byte ptr [ebp-0x4]"),
    0xCDD18:("add","al,byte ptr [ebp-0x20]"),
    0xCDD1B:("add","byte ptr [ebx+0x7],al"),
    0xCDD1E:("mov","al,byte ptr [ebp-0xc]"),
    0xCDD21:("add","byte ptr [ebx+0x7],al"),
    0xCDD24:("mov","al,byte ptr [ebp-0x14]"),
    0xCDD27:("add","al,byte ptr [ebp-0x10]"),
    0xCDD2A:("add","byte ptr [ebx+0x7],al"),
    0xCDD2D:("mov","al,byte ptr [ebp-0x18]"),
    0xCDD30:("add","byte ptr [ebx+0x7],al"),
    0xCDD33:("test","edi,edi"),
    0xCDD35:("je","0xceb17"),
    0xCDD3B:("cmp","esi,0x3"),
    0xCDD3E:("jne","0xcdd55"),
    0xCDD40:("mov","esi,dword ptr ds:0x322fc"),
    0xCDD47:("lods","al,byte ptr ds:[esi]"),
    0xCDD48:("mov","byte ptr [edi],al"),
    0xCDD4D:("jne","0xcdd47"),
    0xCDD50:("jmp","0xceb17"),
    0xCDD60:("call","0x1165f2"),
    0xCDD75:("call","0x1165f2"),
    0xCDDA0:("call","0x1165f2"),
    0xCDE03:("call","0x1165f2"),
    0xCDED9:("call","0x1165f2"),
    0xCDEF6:("jmp","0xceb0e"),
}
RX = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$",re.I)
ALLOW_EXTERNAL = {0xCEB17,0xCEB0E}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def disassembly(code,lo,hi):
    p=subprocess.run(["objdump","-D","-b","binary","-m","i386","-M","intel",
            f"--start-address=0x{lo:x}",f"--stop-address=0x{hi:x}",str(code)],
          text=True,capture_output=True,check=True)
    out=[]
    for line in p.stdout.splitlines():
        m=RX.match(line)
        if m:out.append((int(m[1],16),bytes.fromhex(m[2].strip()),m[3].lower(),m[4].strip().lower()))
    return out,p.stdout

def mixed_race_morale_penalty(entry_tags,field_137):
    """Source-derived all-branch interpretation of Mixed_Race_Morale_Penalty_.

    Original only considers low-nibble tags <8; a different second valid
    low-nibble tag causes -4, except if no more than 1 entry or +0x137!=0.
    """
    if not all(isinstance(x,int) and 0<=x<=15 for x in entry_tags):
        raise ValueError("fixture tags must be low nibbles")
    if len(entry_tags)<2 or field_137:
        return 0
    first=None
    for tag in reversed(entry_tags):
        if tag>=8:
            continue
        if first is None:
            first=tag
        elif tag!=first:
            return -4
    return 0

def trunc_half(x):
    """Reconstruct CDQ; SUB EAX,EDX; SAR EAX,1, for 32-bit bounded inputs."""
    if not -(1<<31) < x < (1<<31)-1:
        raise ValueError("fixture input outside non-overflow test domain")
    return (x+(1 if x<0 else 0))>>1

def base_morale_for_government_signed_byte(gov):
    """Table lookup for fixture government byte index [0..7] only."""
    if not 0<=gov<8:
        raise ValueError("No negative/out-of-table indexing inference")
    return TABLES["base_byte_morale"][1][gov]

def signed_byte(x):
    y=x&0xff
    return y if y<128 else y-256

def add_to_morale_byte(base,bonuses):
    """Original CDD0C..CDD30 use AL/BYTE additions; modulo 256 is required."""
    total=base&0xff
    for v in bonuses:
        total=(total+(v&0xff))&0xff
    return total

def officer_bonus_from_leader_flags(flag_byte, owned_level):
    """Verifies source's mutually exclusive +0x80 / +0x40 leader paths.

    Caller only executes this after Colony_Officer_ returns an index != -1;
    owned_level is supplied by Owned_Officer_Level_ and is NOT inferred.
    """
    if not 0<=flag_byte<=255 or not 0<=owned_level<=5:
        raise ValueError("limited positive fixture domain")
    if flag_byte & 0x80:
        return trunc_half(3*owned_level+4)
    if flag_byte & 0x40:
        return owned_level+1
    return 0

def controlled_morale(government, *, mixed=0, officer=0, plus14a=False,
                      player1da3=False, plus155=False, origin_protected=True,
                      owner_planet_index_valid=True, player1aa3=False,
                      plus14c=False, plus138=False):
    """Branch-specific non-overflow illustration of the source BYTE+7 write.

    Source's full external player/planet/leader state is not modeled. Every
    caller-dependent value is supplied explicitly; tables are authenticated.
    For an invalid/nonexistent origin planet index, penalty applies.
    """
    base=base_morale_for_government_signed_byte(government)
    group=trunc_half(government)
    if group==3:
        return base  # original 0xCDBAC jumps over ALL bonus aggregation
    if not 0<=group<3:
        raise ValueError("government group outside table domain")
    bonuses=[int(mixed),int(officer),4*bool(plus14a),
             4*bool(player1da3),6*bool(plus155)]
    if not owner_planet_index_valid or not origin_protected:
        bonuses.append(signed_byte(TABLES['penalty_by_government_group'][1][group]))
    if group<=1 and player1aa3:
        bonuses.append(2)
    if plus14c or plus138:
        bonuses.append(TABLES['extra_bonus_by_government'][1][government])
    return add_to_morale_byte(base,bonuses)

def test_fixtures():
    tests=[
        ([],False,0),
        ([0],False,0),
        ([0,0],False,0),
        ([0,1],False,-4),
        ([1,0,1],False,-4),
        ([8,0,8,0],False,0),
        ([8,0,9,2],False,-4),
        ([0,1],True,0),
        ([8,9,10],False,0),
    ]
    for args,flag,expected in tests:
        assert mixed_race_morale_penalty(args,flag)==expected,(args,flag,expected)
    assert trunc_half(-5)==-2 and trunc_half(-4)==-2
    assert trunc_half(5)==2 and trunc_half(4)==2
    assert [signed_byte(base_morale_for_government_signed_byte(i)) for i in range(8)]==[-4,-4,-4,0,0,0,0,0]
    assert add_to_morale_byte(252,[4,6])==6
    assert add_to_morale_byte(250,[-10,4])==244
    assert officer_bonus_from_leader_flags(0x80,5)==9
    assert officer_bonus_from_leader_flags(0x40,5)==6
    assert officer_bonus_from_leader_flags(0xC0,5)==9
    assert officer_bonus_from_leader_flags(0,5)==0
    assert controlled_morale(6,mixed=-4,plus14a=True,player1da3=True,
                     plus155=True,origin_protected=False,plus14c=True)==0
    assert controlled_morale(0,origin_protected=False)==242
    assert controlled_morale(0,origin_protected=True)==252
    assert controlled_morale(0,origin_protected=True,plus14a=True)==0
    assert controlled_morale(0,origin_protected=True,player1aa3=True)==254
    assert controlled_morale(4,origin_protected=False)==252
    assert controlled_morale(4,origin_protected=True,plus155=True)==6
    assert controlled_morale(2,origin_protected=True,plus14c=True,plus138=True)==0
    assert controlled_morale(4,origin_protected=True,officer=3)==3
    assert controlled_morale(4,origin_protected=True,owner_planet_index_valid=False)==252
    return len(tests)+7+14

def audit(exe_path,code_path):
    exe,code=exe_path.read_bytes(),code_path.read_bytes()
    if sha(exe)!=EXE_SHA or len(code)!=1410709 or sha(code)!=CODE_SHA:
        raise ValueError("Original ORION2.EXE or LE CODE identity mismatch")
    with (ROOT/"decompilation/functions.csv").open(newline="") as f:
        functions={r["name"]:r for r in csv.DictReader(f)}
    verified_bodies=[]
    for name,start,size,expected in [MAIN,*CALLEES]:
        r=functions[name]
        if (int(r["offset"]),int(r["inferred_size"]))!=(start,size):
            raise ValueError("Original Watcom function extent differs: "+name)
        if sha(code[start:start+size])!=expected:
            raise ValueError("Entire function bytes differ: "+name)
        verified_bodies.append({"name":name,"CODE_start":hex(start),"bytes":size,"sha256":expected})
    with (ROOT/"decompilation/symbols.csv").open(newline="") as f:
        names={(r["name"],r["segment"]):int(r["offset"]) for r in csv.DictReader(f)}
    for key,off in {
        ("_player","2"):0x1FF98,("_planet","2"):0x1B0D4,
        ("_colony","2"):0x1AB18,("_leaders","2"):0x1B0DC,
        ("_unification_has_no_morale_msg","2"):0x322FC,
        ("_no_barracks_msg","2"):0x3232C,
    }.items():
        if names.get(key)!=off:
            raise ValueError(f"Watcom DATA symbol mismatch: {key}")
    source_tables={}
    for name,(off,value,digest) in TABLES.items():
        if code[off:off+len(value)]!=value or sha(value)!=digest:
            raise ValueError("Original CODE constant differs: "+name)
        source_tables[name]={"CODE_offset":hex(off),"unsigned_bytes":list(value),
                             "signed_bytes":[signed_byte(x) for x in value],"sha256":digest}
    start,end=MAIN[1],MAIN[1]+MAIN[2]
    instructions,_=disassembly(code_path,start,end)
    if not instructions or instructions[0][0]!=start:
        raise ValueError("Original routine entry was not decoded")
    # Verifies decoded disassembly has NO holes, overlaps or split raw bytes.
    pos=start
    decode_map={}
    for at,raw,op,arg in instructions:
        if at!=pos:raise ValueError(f"Disassembler missed/misaligned CODE at {pos:#x}")
        if code[at:at+len(raw)]!=raw:raise ValueError(f"Decoded CODE byte mismatch {at:#x}")
        if not raw:raise ValueError(f"Empty instruction at {at:#x}")
        decode_map[at]=(op,arg)
        pos+=len(raw)
    if pos!=end:
        raise ValueError(f"Decoded {pos-start} bytes, expected {end-start}")
    for address,expected in OPS.items():
        if decode_map.get(address)!=expected:
            raise ValueError(f"Expected source machine code {address:#x}: {expected}; decoded {decode_map.get(address)}")
    edges=[];calls={}
    for at,raw,op,arg in instructions:
        if op=="call" or op.startswith("j"):
            if not re.fullmatch(r"0x[0-9a-f]+",arg):
                raise ValueError(f"Unresolved outgoing control transfer {at:#x}: {op} {arg}")
            target=int(arg,16)
            if op=="call":
                calls.setdefault(target,[]).append(at)
                if target not in {n[1] for n in CALLEES}:
                    raise ValueError(f"Unknown direct call target {at:#x}->{target:#x}")
            elif not (start<=target<end or target in ALLOW_EXTERNAL):
                raise ValueError(f"Branch unexpectedly exits named body {at:#x}->{target:#x}")
            if op!="call" and target in decode_map or op=="call" or target in ALLOW_EXTERNAL:
                edges.append({"from":hex(at),"type":op,"to":hex(target)})
            elif op!="call":
                raise ValueError(f"Transfer to noninstruction address {at:#x}->{target:#x}")
    expected_calls={0xCDAD4:1,0xCD9F2:1,0x84951:2,0x1165F2:13}
    if {target:len(v) for target,v in calls.items()}!=expected_calls:
        raise ValueError(f"Original call inventory has changed: {calls}")
    fixtures=test_fixtures()
    return {
      "status":"source-verified-static-control-flow-and-selected-arithmetic",
      "EXE_sha256":EXE_SHA,"LE_CODE_sha256":CODE_SHA,
      "full_verified_named_function_bodies":verified_bodies,
      "decoded_entire_morale_body_bytes":pos-start,
      "decoded_morale_instruction_count":len(instructions),
      "selected_machine_instruction_anchors":len(OPS),
      "complete_direct_control_transfer_inventory":edges,
      "direct_call_inventory":[{"target":hex(t),"callee":next(n[0] for n in CALLEES if n[1]==t),
                 "sites":[hex(at) for at in locations]} for t,locations in sorted(calls.items())],
      "verified_CODE_table_slices":source_tables,
      "verified_Watcom_DATA_globals":["_player","_planet","_colony","_leaders",
                           "_unification_has_no_morale_msg","_no_barracks_msg"],
      "controlled_source_derived_fixtures":fixtures,
      "source_observed_morale_writes":["BYTE colony+0x07 from table at CODE 0xcd4c4",
                          "AL/BYTE accumulations at CODE 0xcdd0c..0xcdd30 wrap modulo 256"],
      "source_observed_gates":["derived signed-half government ==3 skips bonus evaluation",
                "output-formatting callback pointer EDI null jumps to shared epilogue 0xceb17",
                "formatting path branches to 0xceb0e after preparing final arguments"],
      "limits":["No original DOS dynamic differential comparison",
                "Formatter external string data not dynamically verified",
                "Complete game-state semantics and native gameplay equivalence not established"]
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",required=True,type=Path)
    p.add_argument("--code",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    out=audit(args.exe,args.code)
    if args.output:args.output.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
