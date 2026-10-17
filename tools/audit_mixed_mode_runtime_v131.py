#!/usr/bin/env python3
"""Recover original Watcom v1.31 real-mode ISR/dispatcher with a 16-bit decoder.

Checks all original machine bytes and instruction boundaries, all direct
16-bit branch targets and hardware I/O opcodes, then separately proves one
false 32-bit function (_Alphabet) is a lookup string in the CODE object.
Does NOT inflate the global 32-bit CFG or claim native browser/DOS parity.
"""
import argparse,csv,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXE_SHA="4e11be14217b4aafa1839f333bf5eba037f98b0c44e9e4752c96c464c260419f"
CODE_SHA="f72dd786b0127bcb9765b26218c1758fa148d2d8458bdaa1fd89d485479b2837"
FUNCTIONS=[
 ("__GreenleafFastRealIsr",0x15845A,104,"719f4b010de4b496843c030c66fbf1ec1408a44fda55a46d2a4eff3722e13609",45,"retf"),
 ("__RealDispatcherRR16",0x1584FE,61,"8dc35022433ecbaff7b4bc23e2e9ff1dcaa909420bbdf3d3f53c85cb84adf61d",36,"iret")
]
EXPECTED_BRANCHES={
 "__GreenleafFastRealIsr":{
 0x15846B:("jge",0x158471),
 0x158480:("je",0x15849D),
 0x15848A:("jge",0x158471),
 0x15849B:("jmp",0x158471),
 0x1584A1:("jle",0x1584B5),
 0x1584BC:("jne",0x158462)},
 "__RealDispatcherRR16":{
 0x158525:("je",0x158528),
 0x15852E:("je",0x158531)}
}
EXPECTED_CALLS={
 "__GreenleafFastRealIsr":{0x158475:0x158459,0x158483:0x158459,
                            0x1584A7:0x158459,0x1584B2:0x158459},
 "__RealDispatcherRR16":{}
}
SOURCE_OPCODE_ANCHORS={
 "__GreenleafFastRealIsr":{
 0x15845F:("lds","si,DWORD PTR [bp+0x6]"),
 0x158474:("in","al,dx"),
 0x15847B:("or","BYTE PTR [si+0x1e],al"),
 0x158482:("in","al,dx"),
 0x15848F:("mov","BYTE PTR [bx+si+0x3a],al"),
 0x158492:("inc","WORD PTR [si+0x12]"),
 0x158495:("and","WORD PTR [si+0x12],0x3ff"),
 0x1584A6:("in","al,dx"),
 0x1584B1:("out","dx,al"),
 0x1584B5:("lds","si,DWORD PTR [si+0x6]"),
 0x1584C1:("retf","")},
 "__RealDispatcherRR16":{
 0x158506:("push","cs"),
 0x158507:("pop","ds"),
 0x15850E:("inc","WORD PTR [si+0x3a]"),
 0x158517:("call","DWORD PTR [si+0x10]"),
 0x158522:("cmp","dx,0x0"),
 0x158527:("out","dx,al"),
 0x15852B:("cmp","dx,0x0"),
 0x158530:("out","dx,al"),
 0x15853A:("iret","")}
}
RX_INSTRUCTION=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*)$',re.I)
RX_BYTEONLY=re.compile(r'^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2}\s*)+)$',re.I)

def sha(b):return hashlib.sha256(b).hexdigest()
def parsed_source_16bit(image,path,at,length):
    # Keep an independent 16-bit decoder; the main global CFG deliberately
    # remains in 32-bit mode because it includes non-real-mode game code.
    cmd=["objdump","-D","-b","binary","-m","i8086","-M","intel",
         f"--start-address={at}",f"--stop-address={at+length}",str(path)]
    raw=subprocess.run(cmd,text=True,capture_output=True,check=True)
    decoded=[];continuations=0
    for line in raw.stdout.splitlines():
        # All-byte rows must be recognized FIRST so 0xFF isn't a mnemonic.
        m=RX_BYTEONLY.match(line)
        if m:
            addr=int(m.group(1),16);bytestr=bytes.fromhex(m.group(2))
            if not decoded or addr!=decoded[-1][0]+len(decoded[-1][1]):
                raise ValueError(f"Unowned original real-mode continuation at {addr:#x}")
            a,pre,op,args=decoded[-1];decoded[-1]=(a,pre+bytestr,op,args)
            continuations+=1
            continue
        m=RX_INSTRUCTION.match(line)
        if not m:continue
        addr=int(m.group(1),16);bytestr=bytes.fromhex(m.group(2))
        decoded.append((addr,bytestr,m.group(3).lower(),m.group(4).strip()))
    curr=at
    for addr,raw,op,args in decoded:
        if addr!=curr or image[addr:addr+len(raw)]!=raw:
            raise ValueError(f"Original source 16-bit byte coverage failed at {addr:#x}")
        curr+=len(raw)
    if curr!=at+length:raise ValueError(f"Original 16-bit function not fully decoded: {curr:#x} != {at+length:#x}")
    return decoded,continuations

def source_displacement(code,addr,raw,opcode,args):
    if not opcode.startswith("j"):raise ValueError("Non-branch")
    if raw[0] in (*range(0x70,0x80),0xeb,0xe3) and len(raw)==2:
        delta=int.from_bytes(raw[1:2],"little",signed=True)
    elif raw[0] in (0xe9,0xe8) and len(raw)==3:
        delta=int.from_bytes(raw[1:3],"little",signed=True)
    elif raw[:2] and raw[0]==0x0f and 0x80<=raw[1]<=0x8f and len(raw)==4:
        delta=int.from_bytes(raw[2:4],"little",signed=True)
    else:raise ValueError(f"Not an authenticated real-mode direct branch at {addr:#x}: {raw.hex()}")
    return addr+len(raw)+delta

def audit(exe,code):
    image=code.read_bytes()
    if sha(exe.read_bytes())!=EXE_SHA or sha(image)!=CODE_SHA or len(image)!=1410709:
        raise ValueError("Canonical original DOS v1.31 source EXE/CODE changed")
    symbols={(r["name"],r["segment"]):int(r["offset"]) for r in
             csv.DictReader((ROOT/"decompilation/symbols.csv").open(newline=""))}
    extents={r["name"]:r for r in
             csv.DictReader((ROOT/"decompilation/functions.csv").open(newline=""))}
    records=[];source_instructions=0;checked_branches=0;checked_calls=0;anchors=0
    for name,at,length,digest,n_ins,terminator in FUNCTIONS:
        r=extents[name]
        if (int(r["offset"]),int(r["inferred_size"]))!=(at,length):
            raise ValueError("Original named mixed-mode function interval changed "+name)
        if symbols.get((name,"1"))!=at or sha(image[at:at+length])!=digest:
            raise ValueError("Original named real-mode full body hash/offset differs "+name)
        decoded,cont=parsed_source_16bit(image,code,at,length)
        if len(decoded)!=n_ins or decoded[-1][2]!=terminator:
            raise ValueError("Unexpected complete original 16-bit instruction body "+name)
        instr={addr:(raw,op,args) for addr,raw,op,args in decoded}
        branches={addr for addr,raw,op,args in decoded if op.startswith("j")}
        if branches!=set(EXPECTED_BRANCHES[name]):
            raise ValueError("Unexpected original 16-bit direct branch set "+name)
        for addr,(op,dest) in EXPECTED_BRANCHES[name].items():
            src,have_op,args=instr[addr]
            if have_op!=op or source_displacement(image,addr,src,op,args)!=dest or dest not in instr:
                raise ValueError(f"Original 16-bit direct branch instruction/target differs {name} {addr:#x}")
            checked_branches+=1
        # 16-bit CALL near displacement, or the original indirect dispatcher
        # callback at [SI+0x10]. No made-up callback target address.
        calls={addr for addr,raw,op,args in decoded if op=="call"}
        expected_calls=set(EXPECTED_CALLS[name])
        if name=="__RealDispatcherRR16":expected_calls.add(0x158517)
        if calls!=expected_calls:raise ValueError("Unexpected original real-mode CALLs in "+name)
        for addr,dest in EXPECTED_CALLS[name].items():
            raw,op,args=instr[addr]
            if raw[0]!=0xe8 or len(raw)!=3 or addr+3+int.from_bytes(raw[1:],"little",signed=True)!=dest:
                raise ValueError("Incorrect original 16-bit source CALL displacement")
            if dest!=0x158459 or image[dest]!=0xc3:
                raise ValueError("Called original 16-bit helper is not verified RET")
            checked_calls+=1
        for addr,(expected_op,expected_args) in SOURCE_OPCODE_ANCHORS[name].items():
            raw,op,args=instr[addr]
            if (op,args)!=(expected_op,expected_args):
                raise ValueError(f"Original real-mode source opcode anchor differs {name} {addr:#x}: {(op,args)}")
            anchors+=1
        source_instructions+=len(decoded)
        records.append({"named_original_Watcom_symbol":name,"CODE_start":hex(at),
          "complete_original_bytes":length,"full_original_SHA256":digest,
          "decoded_real_mode_16bit_instructions":len(decoded),
          "16bit_branch_sites":[{"CODE_site":hex(s),"CODE_destination":hex(dest)}
                              for s,(op,dest) in EXPECTED_BRANCHES[name].items()],
          "16bit_direct_helper_calls":len(EXPECTED_CALLS[name]),
          "source_opcode_anchors":len(SOURCE_OPCODE_ANCHORS[name]),
          "byte_only_continuation_rows":cont,
          "verified_final_instruction":terminator})
    # Prove Watcom emitted a NUL-terminated radix alphabet *in CODE*,
    # not a third 32-bit gameplay procedure. Original explicit CS byte load
    # references exactly its symbol address.
    alphabet=0x134942
    data=b"0123456789abcdefghijklmnopqrstuvwxyz\x00"
    if (symbols.get(("_Alphabet","1"))!=alphabet or
        (int(extents["_Alphabet"]["offset"]),int(extents["_Alphabet"]["inferred_size"]))!=(alphabet,len(data)) or
        image[alphabet:alphabet+len(data)]!=data or
        image[0x13498f:0x134996]!=bytes.fromhex("2e8a9242491300")):
        raise ValueError("Original radix alphabet/code data identity is not proven")
    old_cfg=json.loads((ROOT/"decompilation/function_cfg_extents.json").read_text())
    if (old_cfg["cfg_membership_records"],old_cfg["functions"])!=(396138,5635):
        raise ValueError("Original baseline canonical full CODE CFG differs")
    if (source_instructions,checked_branches,checked_calls,anchors)!=(81,8,4,20):
        raise ValueError("Original source mixed-mode audit checkpoint count differs")
    return {
      "status":"original-v131-mixed-mode-Watcom-16bit-ISR-dispatcher-and-radix-DATA-verified",
      "canonical_official_EXE_sha256":EXE_SHA,
      "authentic_original_LE_CODE_sha256":CODE_SHA,
      "code_object_bytes":len(image),
      "original_verified_16bit_functions":records,
      "complete_16bit_original_instructions_decoded":source_instructions,
      "exact_16bit_branch_destinations_verified":checked_branches,
      "near_real_mode_helper_CALL_targets_verified":checked_calls,
      "source_original_16bit_opcodes_checked":anchors,
      "code_object_nonexecutable_alphabet":{
        "symbol":"_Alphabet","CODE_start":hex(alphabet),"exact_bytes":len(data),
        "original_lookup_string":data[:-1].decode("ascii"),
        "original_cs_byte_load_source_CODE":"0x13498f",
        "original_instruction_machine_bytes":"2e8a9242491300",
        "source_symbol_kind":"CODE object but literal read-only lookup data, not a third 32-bit x86 function"},
      "original_16bit_mode_indicators":{
        "Greenleaf":["BP/SP/SI/DX sixteen-bit registers","LDS SI far source pointer",
                    "16-bit I/O port IN/OUT","10-bit circular counter mask 0x03ff",
                    "FAR RET at 0x1584c1"],
        "RealDispatcher":["16-bit stack/register saving","far indirect callback [SI+0x10]",
                          "conditional hardware end-of-interrupt OUT",
                          "IRET at 0x15853a"]},
      "baseline_global_32bit_CFG_instruction_memberships":old_cfg["cfg_membership_records"],
      "baseline_global_32bit_CFG_unresolved_edges":21,
      "baseline_global_CFG_modified":False,
      "why_no_global_32bit_CFG_inflation":"The legacy global traversal assumes 32-bit protected CODE, but RR16/ISR bytes are real-mode 16-bit. Preserve baseline and publish a separately exact source-authenticated 16-bit mode audit.",
      "limitations":["No live original DOS runtime interrupt or hardware I/O tests",
                     "No proof of full 16-bit relocation/segment base wiring or native gameplay code",
                     "Remaining 32-bit CFG apparent errors include data labels and special runtime code; they cannot be resolved by pretending these are 32-bit functions",
                     "No defensible semantic whole-executable decompilation percentage or browser-game playability implied"]
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe",type=Path,required=True)
    p.add_argument("--code",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    report=audit(a.exe,a.code)
    if a.output:a.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
